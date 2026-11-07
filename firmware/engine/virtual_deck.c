/**
 * Tape Master v2 - Virtual Deck Playback Engine Implementation
 * 
 * Streams pulse intervals from .TAP, .TZX, or .CSW files to the PIO TX FIFO
 * with zero-jitter real-time execution and host MOTOR_SENSE auto-pause/resume.
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#include "virtual_deck.h"
#include "../config/hardware_pins.h"
#include "../drivers/motor_control.h"
#include "../drivers/tlc5916_leds.h"
#include "../formats/tap_c64.h"
#include "../formats/tzx_spectrum.h"
#include "../formats/csw_raw.h"

#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "pulse_gen_tx.pio.h"
#include "audio_pwm_tx.pio.h"
#include <string.h>
#include <strings.h>

#define PULSE_RING_SIZE     512
#define FILE_CHUNK_SIZE     1024

// PIO TX configuration
static PIO          s_pio = pio0;
static uint         s_sm = 0;
static uint         s_offset = 0;
static bool         s_is_pwm_mode = false;

// Ring buffer for decoded pulse intervals (in microseconds / ticks)
static volatile uint32_t s_pulse_ring[PULSE_RING_SIZE];
static volatile uint32_t s_ring_head = 0; // Written by Core 0
static volatile uint32_t s_ring_tail = 0; // Read by Core 1

// File and streaming state
static fat_file_t   s_active_file;
static uint8_t      s_chunk_buffer[FILE_CHUNK_SIZE];
static size_t       s_chunk_len = 0;
static size_t       s_chunk_pos = 0;

static tap_parser_t s_tap_parser;
static tzx_parser_t s_tzx_parser;
static csw_parser_t s_csw_parser;

static virtual_deck_status_t s_deck_status;
static absolute_time_t       s_start_time;

static inline bool ring_is_full(void) {
    return ((s_ring_head + 1) % PULSE_RING_SIZE) == s_ring_tail;
}

static inline bool ring_is_empty(void) {
    return s_ring_head == s_ring_tail;
}

static inline void ring_push(uint32_t pulse) {
    s_pulse_ring[s_ring_head] = pulse;
    s_ring_head = (s_ring_head + 1) % PULSE_RING_SIZE;
}

static inline uint32_t ring_pop(void) {
    uint32_t val = s_pulse_ring[s_ring_tail];
    s_ring_tail = (s_ring_tail + 1) % PULSE_RING_SIZE;
    return val;
}

void virtual_deck_init(void) {
    memset(&s_deck_status, 0, sizeof(s_deck_status));
    s_deck_status.state = DECK_STATE_STOPPED;
    s_deck_status.format = DECK_FORMAT_UNKNOWN;
    s_deck_status.ignore_motor_sense = false;

    s_ring_head = 0;
    s_ring_tail = 0;

    // Load default pulse generator PIO program onto PIO0
    s_offset = pio_add_program(s_pio, &pulse_gen_tx_program);
    pulse_gen_tx_program_init(s_pio, s_sm, s_offset, PIN_TAPE_EMU_OUT);
    s_is_pwm_mode = false;
}

static void configure_pio_mode(bool pwm_mode) {
    pio_sm_set_enabled(s_pio, s_sm, false);
    pio_remove_program(s_pio, s_is_pwm_mode ? &audio_pwm_tx_program : &pulse_gen_tx_program, s_offset);

    if (pwm_mode) {
        s_offset = pio_add_program(s_pio, &audio_pwm_tx_program);
        audio_pwm_tx_program_init(s_pio, s_sm, s_offset, PIN_TAPE_EMU_OUT);
        s_is_pwm_mode = true;
    } else {
        s_offset = pio_add_program(s_pio, &pulse_gen_tx_program);
        pulse_gen_tx_program_init(s_pio, s_sm, s_offset, PIN_TAPE_EMU_OUT);
        s_is_pwm_mode = false;
    }
}

bool virtual_deck_start(const char *filename) {
    if (!filename) return false;

    virtual_deck_stop();

    if (!fat_open_read(filename, &s_active_file)) {
        s_deck_status.state = DECK_STATE_ERROR;
        return false;
    }

    strncpy(s_deck_status.filename, filename, FAT_MAX_FILENAME - 1);
    s_deck_status.filename[FAT_MAX_FILENAME - 1] = '\0';
    s_deck_status.total_bytes = s_active_file.file_size;
    s_deck_status.bytes_processed = 0;
    s_deck_status.total_pulses = 0;
    s_deck_status.elapsed_seconds = 0;
    s_deck_status.progress_percent = 0;

    // Read first chunk to inspect header
    s_chunk_len = fat_read(&s_active_file, s_chunk_buffer, FILE_CHUNK_SIZE);
    if (s_chunk_len == 0) {
        fat_close(&s_active_file);
        s_deck_status.state = DECK_STATE_ERROR;
        return false;
    }

    // Determine format
    const char *ext = strrchr(filename, '.');
    if (ext && strcasecmp(ext, ".tap") == 0) {
        if (!tap_parser_init(&s_tap_parser, s_chunk_buffer, s_chunk_len)) {
            fat_close(&s_active_file);
            s_deck_status.state = DECK_STATE_ERROR;
            return false;
        }
        s_deck_status.format = DECK_FORMAT_TAP_C64;
        configure_pio_mode(false); // Active-low pulse generator
    } else if (ext && strcasecmp(ext, ".tzx") == 0) {
        if (!tzx_parser_init(&s_tzx_parser, s_chunk_buffer, s_chunk_len)) {
            fat_close(&s_active_file);
            s_deck_status.state = DECK_STATE_ERROR;
            return false;
        }
        s_deck_status.format = DECK_FORMAT_TZX_SPECTRUM;
        configure_pio_mode(true); // Audio half-period toggler
    } else if (ext && strcasecmp(ext, ".csw") == 0) {
        if (!csw_parser_init(&s_csw_parser, s_chunk_buffer, s_chunk_len)) {
            fat_close(&s_active_file);
            s_deck_status.state = DECK_STATE_ERROR;
            return false;
        }
        s_deck_status.format = DECK_FORMAT_CSW_RAW;
        configure_pio_mode(false);
    } else {
        fat_close(&s_active_file);
        s_deck_status.state = DECK_STATE_ERROR;
        return false;
    }

    s_ring_head = 0;
    s_ring_tail = 0;
    s_start_time = get_absolute_time();
    s_deck_status.state = DECK_STATE_PLAYING;

    // Turn ON PLAY LED
    led_set_status(STATUS_LED_PLAY, true);
    pio_sm_set_enabled(s_pio, s_sm, true);

    return true;
}

void virtual_deck_pause(void) {
    if (s_deck_status.state == DECK_STATE_PLAYING) {
        s_deck_status.state = DECK_STATE_PAUSED_USER;
        led_set_status(STATUS_LED_PLAY, false);
    }
}

void virtual_deck_resume(void) {
    if (s_deck_status.state == DECK_STATE_PAUSED_USER || s_deck_status.state == DECK_STATE_PAUSED_MOTOR) {
        s_deck_status.state = DECK_STATE_PLAYING;
        led_set_status(STATUS_LED_PLAY, true);
    }
}

void virtual_deck_stop(void) {
    pio_sm_set_enabled(s_pio, s_sm, false);
    if (s_active_file.is_open) {
        fat_close(&s_active_file);
    }
    s_deck_status.state = DECK_STATE_STOPPED;
    led_set_status(STATUS_LED_PLAY, false);
    led_set_status(STATUS_LED_SIGNAL, false);
}

void virtual_deck_update(void) {
    if (s_deck_status.state != DECK_STATE_PLAYING && s_deck_status.state != DECK_STATE_PAUSED_MOTOR) {
        return;
    }

    // Check host motor sense
    bool motor_on = motor_host_is_requesting_run() || motor_is_manual_override_active();
    led_set_status(STATUS_LED_MOTOR, motor_on);

    if (!s_deck_status.ignore_motor_sense) {
        if (!motor_on && s_deck_status.state == DECK_STATE_PLAYING) {
            s_deck_status.state = DECK_STATE_PAUSED_MOTOR;
            // Blink PLAY LED to indicate waiting for host motor line
            led_set_status(STATUS_LED_PLAY, (to_ms_since_boot(get_absolute_time()) / 500) % 2);
            return;
        } else if (motor_on && s_deck_status.state == DECK_STATE_PAUSED_MOTOR) {
            s_deck_status.state = DECK_STATE_PLAYING;
            led_set_status(STATUS_LED_PLAY, true);
        }
    }

    if (s_deck_status.state != DECK_STATE_PLAYING) return;

    // Decode pulses from active parser into ring buffer
    while (!ring_is_full()) {
        uint32_t pulse_val = 0;
        bool has_pulse = false;

        if (s_deck_status.format == DECK_FORMAT_TAP_C64) {
            has_pulse = tap_parser_next_pulse(&s_tap_parser, &pulse_val);
            s_deck_status.bytes_processed = s_tap_parser.cursor;
        } else if (s_deck_status.format == DECK_FORMAT_TZX_SPECTRUM) {
            bool level_toggle = true;
            has_pulse = tzx_parser_next_half_period(&s_tzx_parser, &pulse_val, &level_toggle);
            s_deck_status.bytes_processed = s_tzx_parser.cursor;
        } else if (s_deck_status.format == DECK_FORMAT_CSW_RAW) {
            bool polarity = false;
            has_pulse = csw_parser_next_pulse(&s_csw_parser, &pulse_val, &polarity);
            s_deck_status.bytes_processed = s_csw_parser.cursor;
        }

        if (has_pulse) {
            ring_push(pulse_val);
            s_deck_status.total_pulses++;
        } else {
            // EOF reached
            if (ring_is_empty()) {
                virtual_deck_stop();
                s_deck_status.state = DECK_STATE_COMPLETED;
            }
            break;
        }
    }

    // Update progress stats
    if (s_deck_status.total_bytes > 0) {
        s_deck_status.progress_percent = (uint8_t)((s_deck_status.bytes_processed * 100) / s_deck_status.total_bytes);
    }
    s_deck_status.elapsed_seconds = (uint32_t)(absolute_time_diff_us(s_start_time, get_absolute_time()) / 1000000);
}

void virtual_deck_core1_worker(void) {
    // High-priority loop running on Core 1
    if (s_deck_status.state != DECK_STATE_PLAYING) {
        return;
    }

    // Push pulses from ring buffer into PIO TX FIFO
    while (!pio_sm_is_tx_fifo_full(s_pio, s_sm) && !ring_is_empty()) {
        uint32_t pulse = ring_pop();
        pio_sm_put_blocking(s_pio, s_sm, pulse);

        // Flash SIGNAL LED momentarily during pulse burst
        if ((s_deck_status.total_pulses & 0x1F) == 0) {
            led_toggle_status(STATUS_LED_SIGNAL);
        }
    }
}

void virtual_deck_get_status(virtual_deck_status_t *out_status) {
    if (out_status) {
        memcpy(out_status, &s_deck_status, sizeof(virtual_deck_status_t));
    }
}
