/**
 * Tape Master v2 - Signal Digitizer & Tape Ingestion Engine Implementation
 * 
 * Captures sub-microsecond pulse intervals from physical tape deck via PIO RX,
 * performs real-time RLE compression into Compressed Square Wave (.CSW v2),
 * monitors Azimuth peak level and writes dump to MicroSD.
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#include "signal_digitizer.h"
#include "host_protocol.h"
#include "../config/hardware_pins.h"
#include "../drivers/analog_frontend.h"
#include "../drivers/tlc5916_leds.h"
#include "../drivers/motor_control.h"
#include "../formats/csw_raw.h"

#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "pulse_timer_rx.pio.h"
#include <string.h>

#define CAP_RING_SIZE       1024
#define DUMP_SECTOR_SIZE    512

// PIO RX state machine
static PIO                  s_pio = pio1;
static uint                 s_sm = 0;
static uint                 s_offset = 0;

// Lockless capture ring buffer (Core 1 pushes intervals, Core 0 pops & writes to SD)
static volatile uint32_t    s_cap_ring[CAP_RING_SIZE];
static volatile uint32_t    s_cap_head = 0; // Core 1 writes
static volatile uint32_t    s_cap_tail = 0; // Core 0 reads

static fat_file_t           s_dump_file;
static uint8_t              s_sector_buf[DUMP_SECTOR_SIZE];
static size_t               s_sector_fill = 0;

static digitizer_status_t   s_digitizer_status;
static absolute_time_t      s_rec_start_time;

static inline bool cap_ring_is_full(void) {
    return ((s_cap_head + 1) % CAP_RING_SIZE) == s_cap_tail;
}

static inline bool cap_ring_is_empty(void) {
    return s_cap_head == s_cap_tail;
}

static inline void cap_ring_push(uint32_t val) {
    s_cap_ring[s_cap_head] = val;
    s_cap_head = (s_cap_head + 1) % CAP_RING_SIZE;
}

static inline uint32_t cap_ring_pop(void) {
    uint32_t val = s_cap_ring[s_cap_tail];
    s_cap_tail = (s_cap_tail + 1) % CAP_RING_SIZE;
    return val;
}

void digitizer_init(void) {
    memset(&s_digitizer_status, 0, sizeof(s_digitizer_status));
    s_digitizer_status.state = DIGITIZER_STATE_IDLE;
    s_digitizer_status.min_pulse_us = 0xFFFF;
    s_digitizer_status.max_pulse_us = 0;

    s_cap_head = 0;
    s_cap_tail = 0;

    // Load pulse_timer_rx program onto PIO1
    s_offset = pio_add_program(s_pio, &pulse_timer_rx_program);
    pulse_timer_rx_program_init(s_pio, s_sm, s_offset, PIN_TAPE_DIGITIZED);
}

bool digitizer_start(const char *output_filename) {
    if (!output_filename) return false;

    digitizer_stop();

    if (!fat_open_write(output_filename, &s_dump_file)) {
        s_digitizer_status.state = DIGITIZER_STATE_ERROR;
        return false;
    }

    strncpy(s_digitizer_status.filename, output_filename, FAT_MAX_FILENAME - 1);
    s_digitizer_status.filename[FAT_MAX_FILENAME - 1] = '\0';
    s_digitizer_status.total_pulses = 0;
    s_digitizer_status.bytes_written = 0;
    s_digitizer_status.elapsed_seconds = 0;
    s_digitizer_status.min_pulse_us = 0xFFFF;
    s_digitizer_status.max_pulse_us = 0;
    s_digitizer_status.fifo_overruns = 0;

    // Write placeholder CSW Header (32 bytes)
    csw_header_t header;
    csw_create_header(&header, 1000000, 0, false);
    memcpy(s_sector_buf, &header, sizeof(csw_header_t));
    s_sector_fill = sizeof(csw_header_t);

    s_cap_head = 0;
    s_cap_tail = 0;
    s_rec_start_time = get_absolute_time();
    s_digitizer_status.state = DIGITIZER_STATE_RECORDING;

    // Turn ON REC LED
    led_set_status(STATUS_LED_REC, true);
    pio_sm_set_enabled(s_pio, s_sm, true);

    return true;
}

void digitizer_stop(void) {
    pio_sm_set_enabled(s_pio, s_sm, false);

    if (s_dump_file.is_open) {
        // Flush remaining buffer
        if (s_sector_fill > 0) {
            fat_write(&s_dump_file, s_sector_buf, s_sector_fill);
            s_digitizer_status.bytes_written += s_sector_fill;
            s_sector_fill = 0;
        }

        // Rewind and patch CSW header with total pulse count
        csw_header_t header;
        csw_create_header(&header, 1000000, s_digitizer_status.total_pulses, false);
        fat_seek(&s_dump_file, 0);
        fat_write(&s_dump_file, (const uint8_t *)&header, sizeof(csw_header_t));

        fat_close(&s_dump_file);
    }

    s_digitizer_status.state = DIGITIZER_STATE_STOPPED;
    led_set_status(STATUS_LED_REC, false);
    led_set_status(STATUS_LED_SIGNAL, false);
}

void digitizer_update(void) {
    if (s_digitizer_status.state != DIGITIZER_STATE_RECORDING) {
        return;
    }

    // Monitor Azimuth level via ADC0
    uint8_t az_level = analog_get_azimuth_bar_level();
    s_digitizer_status.azimuth_level = az_level;
    led_set_azimuth_level(az_level, false);

    // Drain capture ring buffer and encode into CSW RLE format
    while (!cap_ring_is_empty()) {
        uint32_t interval_us = cap_ring_pop();
        s_digitizer_status.total_pulses++;

        if (host_protocol_is_streaming()) {
            host_protocol_stream_pulse(interval_us);
        }

        if (interval_us < s_digitizer_status.min_pulse_us) {
            s_digitizer_status.min_pulse_us = (uint16_t)interval_us;
        }
        if (interval_us > s_digitizer_status.max_pulse_us) {
            s_digitizer_status.max_pulse_us = (uint16_t)interval_us;
        }

        // CSW RLE encoding:
        // If interval 1..255: single byte [1..255]
        // If interval >= 256: 0x00 followed by 4-byte little-endian 32-bit integer
        if (interval_us <= 255) {
            s_sector_buf[s_sector_fill++] = (uint8_t)interval_us;
        } else {
            s_sector_buf[s_sector_fill++] = 0x00;
            s_sector_buf[s_sector_fill++] = (uint8_t)(interval_us);
            s_sector_buf[s_sector_fill++] = (uint8_t)(interval_us >> 8);
            s_sector_buf[s_sector_fill++] = (uint8_t)(interval_us >> 16);
            s_sector_buf[s_sector_fill++] = (uint8_t)(interval_us >> 24);
        }

        // Write full 512-byte sector to SD card
        if (s_sector_fill >= DUMP_SECTOR_SIZE) {
            fat_write(&s_dump_file, s_sector_buf, DUMP_SECTOR_SIZE);
            s_digitizer_status.bytes_written += DUMP_SECTOR_SIZE;
            s_sector_fill = 0;
        }
    }

    s_digitizer_status.elapsed_seconds = (uint32_t)(absolute_time_diff_us(s_rec_start_time, get_absolute_time()) / 1000000);
}

void digitizer_core1_worker(void) {
    if (s_digitizer_status.state != DIGITIZER_STATE_RECORDING) {
        return;
    }

    // Pull intervals from PIO RX FIFO
    while (!pio_sm_is_rx_fifo_empty(s_pio, s_sm)) {
        uint32_t ticks = pio_sm_get_blocking(s_pio, s_sm);
        
        // Convert PIO clock ticks to microseconds (calibrated for 10 MHz PIO clock = divide by 10)
        uint32_t interval_us = ticks / 10;
        if (interval_us == 0) interval_us = 1;

        if (!cap_ring_is_full()) {
            cap_ring_push(interval_us);
        } else {
            s_digitizer_status.fifo_overruns++;
        }

        // Signal LED pulse feedback
        if ((s_digitizer_status.total_pulses & 0x1F) == 0) {
            led_toggle_status(STATUS_LED_SIGNAL);
        }
    }
}

void digitizer_get_status(digitizer_status_t *out_status) {
    if (out_status) {
        memcpy(out_status, &s_digitizer_status, sizeof(digitizer_status_t));
    }
}
