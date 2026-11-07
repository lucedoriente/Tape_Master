/**
 * Tape Master v2 - USB CDC Host Communication Protocol Implementation
 * 
 * High-speed bidirectional command & streaming protocol over USB Serial.
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#include "host_protocol.h"
#include "virtual_deck.h"
#include "signal_digitizer.h"
#include "exerciser_engine.h"
#include "../drivers/cartridge_id.h"
#include "../drivers/motor_control.h"
#include "../drivers/analog_frontend.h"
#include "../drivers/tlc5916_leds.h"
#include "../ui/ui_menu.h"
#include "../config/version.h"

#include <stdio.h>
#include <string.h>
#include <strings.h>
#include "pico/stdlib.h"

#define CMD_BUFFER_SIZE         256
#define STREAM_BUFFER_SIZE      64

static stream_mode_t s_stream_mode = STREAM_MODE_DISABLED;
static char          s_cmd_buf[CMD_BUFFER_SIZE];
static size_t        s_cmd_idx = 0;

void host_protocol_init(void) {
    s_stream_mode = STREAM_MODE_DISABLED;
    s_cmd_idx = 0;
    memset(s_cmd_buf, 0, sizeof(s_cmd_buf));
}

bool host_protocol_is_streaming(void) {
    return s_stream_mode != STREAM_MODE_DISABLED;
}

stream_mode_t host_protocol_get_stream_mode(void) {
    return s_stream_mode;
}

void host_protocol_send_event(const char *event_name, const char *arg) {
    if (!event_name) return;
    if (arg && strlen(arg) > 0) {
        printf("EVENT:%s %s\r\n", event_name, arg);
    } else {
        printf("EVENT:%s\r\n", event_name);
    }
}

void host_protocol_stream_pulse(uint32_t interval_us) {
    if (s_stream_mode != STREAM_MODE_PULSES) return;

    // Fast framed ASCII output: "P <us>\r\n"
    printf("P %lu\r\n", interval_us);
}

void host_protocol_stream_adc(uint16_t sample_raw) {
    if (s_stream_mode != STREAM_MODE_RAW_ADC) return;

    printf("A %u\r\n", sample_raw);
}

static void handle_command(char *cmd) {
    // Strip trailing CR/LF
    size_t len = strlen(cmd);
    while (len > 0 && (cmd[len - 1] == '\r' || cmd[len - 1] == '\n' || cmd[len - 1] == ' ')) {
        cmd[--len] = '\0';
    }
    if (len == 0) return;

    // 1. PING
    if (strcasecmp(cmd, "PING") == 0) {
        printf("PONG\r\n");
        return;
    }

    // 2. IDENT
    if (strcasecmp(cmd, "IDENT") == 0) {
        cartridge_descriptor_t desc;
        bool inserted = cartridge_is_inserted();
        if (inserted && cartridge_read_descriptor(&desc)) {
            printf("IDENT FW=" FW_VERSION_STRING " CART_INSERTED=1 CART_ID=%u PLATFORM=\"%s\" SIG_TYPE=%u BAUD=%u\r\n",
                   desc.id, desc.platform_name, desc.signal_type, desc.default_baud_rate);
        } else if (inserted) {
            printf("IDENT FW=" FW_VERSION_STRING " CART_INSERTED=1 CART_ID=255 PLATFORM=\"Unprogrammed Cartridge\" SIG_TYPE=0 BAUD=0\r\n");
        } else {
            printf("IDENT FW=" FW_VERSION_STRING " CART_INSERTED=0 CART_ID=0 PLATFORM=\"None\" SIG_TYPE=0 BAUD=0\r\n");
        }
        return;
    }

    // 3. STATUS
    if (strcasecmp(cmd, "STATUS") == 0) {
        uint8_t bar_lvl = analog_get_azimuth_bar_level();
        uint16_t raw_adc = analog_sample_azimuth_raw();
        bool mot = motor_host_is_requesting_run() || motor_is_manual_override_active();
        bool sense = motor_is_tape_sense_active();
        op_mode_t mode = ui_get_op_mode();

        printf("STATUS OP_MODE=%d MOTOR=%d SENSE=%d AZ_LVL=%u RAW_ADC=%u STREAM=%d\r\n",
               mode, mot ? 1 : 0, sense ? 1 : 0, bar_lvl, raw_adc, s_stream_mode);
        return;
    }

    // 4. STREAM START / STOP
    if (strncasecmp(cmd, "STREAM ", 7) == 0) {
        char *sub = cmd + 7;
        if (strcasecmp(sub, "STOP") == 0) {
            s_stream_mode = STREAM_MODE_DISABLED;
            printf("OK STREAM STOPPED\r\n");
        } else if (strcasecmp(sub, "PULSES") == 0) {
            s_stream_mode = STREAM_MODE_PULSES;
            printf("OK STREAM PULSES ACTIVE\r\n");
        } else if (strcasecmp(sub, "ADC") == 0) {
            s_stream_mode = STREAM_MODE_RAW_ADC;
            printf("OK STREAM RAW_ADC ACTIVE\r\n");
        } else if (strcasecmp(sub, "AZIMUTH") == 0) {
            s_stream_mode = STREAM_MODE_AZIMUTH;
            printf("OK STREAM AZIMUTH ACTIVE\r\n");
        } else {
            printf("ERR UNKNOWN STREAM TYPE\r\n");
        }
        return;
    }

    // 5. MOTOR CONTROL
    if (strncasecmp(cmd, "MOTOR ", 6) == 0) {
        char *val = cmd + 6;
        if (strcasecmp(val, "ON") == 0 || strcmp(val, "1") == 0) {
            motor_set_power(true);
            printf("OK MOTOR ON\r\n");
        } else {
            motor_set_power(false);
            printf("OK MOTOR OFF\r\n");
        }
        return;
    }

    // 6. DECK PLAY / STOP / PAUSE
    if (strncasecmp(cmd, "DECK ", 5) == 0) {
        char *sub = cmd + 5;
        if (strncasecmp(sub, "START ", 6) == 0) {
            char *fname = sub + 6;
            if (virtual_deck_start(fname)) {
                ui_set_op_mode(OP_MODE_VIRTUAL_PLAY);
                printf("OK DECK PLAYING %s\r\n", fname);
            } else {
                printf("ERR FAILED TO OPEN FILE\r\n");
            }
        } else if (strcasecmp(sub, "PAUSE") == 0) {
            virtual_deck_pause();
            printf("OK DECK PAUSED\r\n");
        } else if (strcasecmp(sub, "RESUME") == 0) {
            virtual_deck_resume();
            printf("OK DECK RESUMED\r\n");
        } else if (strcasecmp(sub, "STOP") == 0) {
            virtual_deck_stop();
            ui_set_op_mode(OP_MODE_STANDBY);
            printf("OK DECK STOPPED\r\n");
        }
        return;
    }

    // 7. REC START / STOP
    if (strncasecmp(cmd, "REC ", 4) == 0) {
        char *sub = cmd + 4;
        if (strncasecmp(sub, "START ", 6) == 0) {
            char *fname = sub + 6;
            if (digitizer_start(fname)) {
                ui_set_op_mode(OP_MODE_SIGNAL_DUMP);
                printf("OK REC STARTED %s\r\n", fname);
            } else {
                printf("ERR REC FAILED TO START\r\n");
            }
        } else if (strcasecmp(sub, "STOP") == 0) {
            digitizer_stop();
            ui_set_op_mode(OP_MODE_STANDBY);
            printf("OK REC STOPPED\r\n");
        }
        return;
    }

    // 8. EXERCISER MODES
    if (strncasecmp(cmd, "EXERCISER ", 10) == 0) {
        char *sub = cmd + 10;
        if (strcasecmp(sub, "1KHZ") == 0) {
            exerciser_start(EXERCISER_CAL_TONE_1KHZ);
            ui_set_op_mode(OP_MODE_EXERCISER);
            printf("OK EXERCISER TONE 1000HZ\r\n");
        } else if (strcasecmp(sub, "2KHZ") == 0) {
            exerciser_start(EXERCISER_CAL_TONE_2KHZ);
            ui_set_op_mode(OP_MODE_EXERCISER);
            printf("OK EXERCISER TONE 2000HZ\r\n");
        } else if (strcasecmp(sub, "MOTOR") == 0) {
            exerciser_start(EXERCISER_MOTOR_RUN);
            ui_set_op_mode(OP_MODE_EXERCISER);
            printf("OK EXERCISER MOTOR RUN\r\n");
        } else if (strcasecmp(sub, "LOOPBACK") == 0) {
            exerciser_start(EXERCISER_LOOPBACK_TEST);
            ui_set_op_mode(OP_MODE_EXERCISER);
            printf("OK EXERCISER LOOPBACK RUNNING\r\n");
        } else if (strcasecmp(sub, "STOP") == 0) {
            exerciser_stop();
            ui_set_op_mode(OP_MODE_STANDBY);
            printf("OK EXERCISER STOPPED\r\n");
        }
        return;
    }

    printf("ERR UNKNOWN COMMAND: %s\r\n", cmd);
}

void host_protocol_poll(void) {
    // Non-blocking read from USB CDC stdio
    int ch;
    while ((ch = getchar_timeout_us(0)) != PICO_ERROR_TIMEOUT) {
        if (ch == '\r' || ch == '\n') {
            if (s_cmd_idx > 0) {
                s_cmd_buf[s_cmd_idx] = '\0';
                handle_command(s_cmd_buf);
                s_cmd_idx = 0;
            }
        } else if (s_cmd_idx < (CMD_BUFFER_SIZE - 1)) {
            s_cmd_buf[s_cmd_idx++] = (char)ch;
        }
    }

    // Periodic Azimuth stream if requested
    if (s_stream_mode == STREAM_MODE_AZIMUTH) {
        static uint32_t s_last_az_ms = 0;
        uint32_t now = to_ms_since_boot(get_absolute_time());
        if (now - s_last_az_ms >= 50) { // 20 Hz update
            s_last_az_ms = now;
            printf("AZ %u %u\r\n", analog_get_azimuth_bar_level(), analog_sample_azimuth_raw());
        }
    }
}
