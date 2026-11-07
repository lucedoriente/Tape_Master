/**
 * Tape Master v2 - User Interface & Menu Implementation
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#include "ui_menu.h"
#include "../drivers/oled_display.h"
#include "../drivers/buttons.h"
#include "../drivers/encoder.h"
#include "../drivers/tlc5916_leds.h"
#include "../drivers/analog_frontend.h"
#include "../drivers/motor_control.h"
#include "../drivers/fat_fs.h"
#include "../drivers/sd_card.h"
#include "../engine/virtual_deck.h"
#include "../engine/signal_digitizer.h"
#include "../engine/exerciser_engine.h"
#include "../config/version.h"

#include <stdio.h>
#include <string.h>

static ui_screen_t            s_current_screen = UI_SCREEN_HOME;
static op_mode_t              s_current_op_mode = OP_MODE_STANDBY;
static cartridge_descriptor_t s_active_cartridge;

// File browser state
static fat_file_info_t        s_file_list[FAT_MAX_FILES_LIST];
static uint16_t               s_file_count = 0;
static int16_t                s_selected_file_idx = 0;
static int16_t                s_scroll_offset = 0;
static char                   s_current_loaded_file[FAT_MAX_FILENAME] = "Nessun File";

// Exerciser menu options
static const char *s_exerciser_modes[] = {
    "1. Cal Tone 1000 Hz",
    "2. Cal Tone 2000 Hz",
    "3. Motor Burn-in Run",
    "4. Bus Loopback Test",
    "5. Live Azimuth Peak"
};
static int16_t s_exerciser_selected = 0;

void ui_menu_init(void) {
    s_current_screen = UI_SCREEN_HOME;
    s_current_op_mode = OP_MODE_STANDBY;
    memset(&s_active_cartridge, 0, sizeof(s_active_cartridge));
    s_active_cartridge.id = CART_ID_NONE;
    strncpy(s_active_cartridge.platform_name, "In attesa cartuccia", sizeof(s_active_cartridge.platform_name) - 1);

    s_file_count = 0;
    s_selected_file_idx = 0;
    s_scroll_offset = 0;
}

void ui_notify_cartridge_changed(const cartridge_descriptor_t *desc) {
    if (desc) {
        memcpy(&s_active_cartridge, desc, sizeof(cartridge_descriptor_t));
    } else {
        s_active_cartridge.id = CART_ID_NONE;
        strncpy(s_active_cartridge.platform_name, "Nessuna Cartuccia", sizeof(s_active_cartridge.platform_name) - 1);
    }
}

void ui_set_op_mode(op_mode_t mode) {
    s_current_op_mode = mode;
}

op_mode_t ui_get_op_mode(void) {
    return s_current_op_mode;
}

void ui_set_screen(ui_screen_t screen) {
    s_current_screen = screen;
}

// -----------------------------------------------------------------------------
// Screen Renderers
// -----------------------------------------------------------------------------

static void render_status_bar(void) {
    oled_draw_rect(0, 0, 128, 10, true, true);
    oled_draw_string(2, 1, "TAPE MASTER v2", false);

    bool mot = motor_host_is_requesting_run() || motor_is_manual_override_active();
    if (mot) {
        oled_draw_string(88, 1, "[MTR]", false);
    }
}

static void render_screen_home(void) {
    render_status_bar();

    // Slot info
    oled_draw_string(0, 13, "SLOT:", true);
    oled_draw_string(32, 13, s_active_cartridge.platform_name, true);

    // Current File loaded
    oled_draw_string(0, 24, "FILE:", true);
    oled_draw_string(32, 24, s_current_loaded_file, true);

    // Engine Status
    if (s_current_op_mode == OP_MODE_VIRTUAL_PLAY) {
        virtual_deck_status_t deck;
        virtual_deck_get_status(&deck);

        uint32_t mins = deck.elapsed_seconds / 60;
        uint32_t secs = deck.elapsed_seconds % 60;
        oled_draw_string_formatted(0, 36, true, "PLAY %02lu:%02lu [%3u%%]", mins, secs, deck.progress_percent);
        oled_draw_progress_bar(0, 46, 128, 6, deck.progress_percent);
    } else if (s_current_op_mode == OP_MODE_SIGNAL_DUMP) {
        digitizer_status_t dig;
        digitizer_get_status(&dig);

        uint32_t mins = dig.elapsed_seconds / 60;
        uint32_t secs = dig.elapsed_seconds % 60;
        oled_draw_string_formatted(0, 36, true, "REC  %02lu:%02lu P:%lu", mins, secs, dig.total_pulses);
        oled_draw_progress_bar(0, 46, 128, 6, dig.azimuth_level * 10);
    } else {
        oled_draw_string(0, 36, "STATO: STANDBY", true);
        oled_draw_string(0, 46, "Pronto ad operare", true);
    }

    // Navigation hints
    oled_draw_line(0, 53, 127, 53, true);
    oled_draw_string(0, 55, "ENC:Browser PLAY:Avvio", true);
}

static void render_screen_file_browser(void) {
    render_status_bar();

    oled_draw_string(0, 12, "--- SD CARD BROWSER ---", true);

    if (s_file_count == 0) {
        oled_draw_string(10, 28, "Nessun file trovato", true);
        oled_draw_string(10, 40, "su MicroSD (.tap/.tzx)", true);
    } else {
        // Display 3 visible files
        for (int i = 0; i < 3; i++) {
            int idx = s_scroll_offset + i;
            if (idx >= s_file_count) break;

            int y = 24 + (i * 10);
            bool is_selected = (idx == s_selected_file_idx);

            if (is_selected) {
                oled_draw_rect(0, y - 1, 128, 9, true, true);
                oled_draw_string(2, y, s_file_list[idx].filename, false);
            } else {
                oled_draw_string(2, y, s_file_list[idx].filename, true);
            }
        }
    }

    oled_draw_line(0, 54, 127, 54, true);
    oled_draw_string(0, 56, "ENC:Scorri  PREV:Indietro", true);
}

static void render_screen_azimuth_tune(void) {
    render_status_bar();

    oled_draw_string(0, 13, "--- ALLIN. AZIMUT ---", true);

    uint8_t bar_lvl = analog_get_azimuth_bar_level();
    led_set_azimuth_level(bar_lvl, false);
    led_panel_update();

    oled_draw_progress_bar(10, 25, 108, 12, bar_lvl * 10);

    uint16_t raw_adc = analog_sample_azimuth_raw();
    uint32_t millivolts = (raw_adc * 3300) / 4095;
    oled_draw_string_formatted(12, 40, true, "Picco: %lu mV (%d/10)", millivolts, bar_lvl);

    oled_draw_line(0, 53, 127, 53, true);
    bool ovr = motor_is_manual_override_active();
    oled_draw_string_formatted(0, 55, true, "REC:Mot %s  ENC:Exit", ovr ? "ON" : "OFF");
}

static void render_screen_exerciser(void) {
    render_status_bar();

    oled_draw_string(0, 12, "--- BANCO TEST & CAL ---", true);

    exerciser_status_t ex;
    exerciser_get_status(&ex);

    if (ex.active) {
        oled_draw_string_formatted(0, 25, true, "TEST ATTIVO (%lu s)", ex.duration_seconds);
        if (ex.mode == EXERCISER_LOOPBACK_TEST) {
            oled_draw_string_formatted(0, 36, true, "RX:%lu ERR:%lu", ex.loopback_received, ex.loopback_errors);
        } else {
            oled_draw_string_formatted(0, 36, true, "Modo: %d", ex.mode);
        }
    } else {
        for (int i = 0; i < 3; i++) {
            int idx = (s_exerciser_selected / 3) * 3 + i;
            if (idx >= 5) break;

            int y = 24 + (i * 9);
            if (idx == s_exerciser_selected) {
                oled_draw_rect(0, y - 1, 128, 9, true, true);
                oled_draw_string(2, y, s_exerciser_modes[idx], false);
            } else {
                oled_draw_string(2, y, s_exerciser_modes[idx], true);
            }
        }
    }

    oled_draw_line(0, 54, 127, 54, true);
    oled_draw_string(0, 56, "PLAY:Start  ENC:Cambia", true);
}

static void render_screen_diagnostics(void) {
    render_status_bar();

    oled_draw_string(0, 12, "--- DIAGNOSTICA BUS ---", true);
    oled_draw_string_formatted(0, 22, true, "Cart Inserita: %s", cartridge_is_inserted() ? "SI" : "NO");
    oled_draw_string_formatted(0, 31, true, "Sensore Tasto: %s", motor_is_tape_sense_active() ? "PLAY" : "STOP");
    oled_draw_string_formatted(0, 40, true, "Host Motore  : %s", motor_host_is_requesting_run() ? "RUN" : "HALT");
    oled_draw_string_formatted(0, 49, true, "SD Card Type : %s", sd_card_is_ready() ? "SDHC/FAT" : "ERR/NONE");

    oled_draw_line(0, 56, 127, 56, true);
    oled_draw_string(0, 58, "FW: " FW_VERSION_STRING " (KiCad 9)", true);
}

// -----------------------------------------------------------------------------
// UI Navigation and Input Dispatch
// -----------------------------------------------------------------------------

void ui_menu_update(void) {
    // Process Rotary Encoder
    int32_t enc_delta = encoder_get_delta();

    if (enc_delta != 0) {
        if (s_current_screen == UI_SCREEN_FILE_BROWSER) {
            s_selected_file_idx += enc_delta;
            if (s_selected_file_idx < 0) s_selected_file_idx = 0;
            if (s_selected_file_idx >= s_file_count) s_selected_file_idx = s_file_count - 1;

            if (s_selected_file_idx < s_scroll_offset) {
                s_scroll_offset = s_selected_file_idx;
            } else if (s_selected_file_idx >= s_scroll_offset + 3) {
                s_scroll_offset = s_selected_file_idx - 2;
            }
        } else if (s_current_screen == UI_SCREEN_EXERCISER) {
            s_exerciser_selected += enc_delta;
            if (s_exerciser_selected < 0) s_exerciser_selected = 0;
            if (s_exerciser_selected >= 5) s_exerciser_selected = 4;
        } else if (s_current_screen == UI_SCREEN_HOME) {
            if (enc_delta > 0) {
                // Refresh SD file list
                s_file_count = fat_list_files("/", s_file_list, FAT_MAX_FILES_LIST);
                s_current_screen = UI_SCREEN_FILE_BROWSER;
            } else {
                s_current_screen = UI_SCREEN_AZIMUTH_TUNE;
            }
        }
    }

    // Process Encoder Push Switch
    if (buttons_get_event(BTN_ID_ENC_SW) == BTN_EVENT_SHORT_PRESS) {
        if (s_current_screen == UI_SCREEN_FILE_BROWSER) {
            if (s_file_count > 0) {
                strncpy(s_current_loaded_file, s_file_list[s_selected_file_idx].filename, FAT_MAX_FILENAME - 1);
            }
            s_current_screen = UI_SCREEN_HOME;
        } else if (s_current_screen == UI_SCREEN_HOME) {
            s_current_screen = UI_SCREEN_EXERCISER;
        } else {
            s_current_screen = UI_SCREEN_HOME;
        }
    }

    // Process PREV Button
    if (buttons_get_event(BTN_ID_PREV) == BTN_EVENT_SHORT_PRESS) {
        s_current_screen = UI_SCREEN_HOME;
    }

    // Process NEXT Button
    if (buttons_get_event(BTN_ID_NEXT) == BTN_EVENT_SHORT_PRESS) {
        s_current_screen = UI_SCREEN_DIAGNOSTICS;
    }

    // Process PLAY Button
    if (buttons_get_event(BTN_ID_PLAY) == BTN_EVENT_SHORT_PRESS) {
        if (s_current_screen == UI_SCREEN_FILE_BROWSER) {
            if (s_file_count > 0) {
                strncpy(s_current_loaded_file, s_file_list[s_selected_file_idx].filename, FAT_MAX_FILENAME - 1);
                virtual_deck_start(s_current_loaded_file);
                ui_set_op_mode(OP_MODE_VIRTUAL_PLAY);
                s_current_screen = UI_SCREEN_HOME;
            }
        } else if (s_current_screen == UI_SCREEN_EXERCISER) {
            exerciser_status_t ex;
            exerciser_get_status(&ex);
            if (ex.active) {
                exerciser_stop();
            } else {
                exerciser_start((exerciser_mode_t)(s_exerciser_selected + 1));
            }
        } else {
            // Home screen PLAY toggle
            if (s_current_op_mode == OP_MODE_STANDBY) {
                if (strcmp(s_current_loaded_file, "Nessun File") != 0) {
                    virtual_deck_start(s_current_loaded_file);
                    ui_set_op_mode(OP_MODE_VIRTUAL_PLAY);
                } else {
                    // Open browser
                    s_file_count = fat_list_files("/", s_file_list, FAT_MAX_FILES_LIST);
                    s_current_screen = UI_SCREEN_FILE_BROWSER;
                }
            } else if (s_current_op_mode == OP_MODE_VIRTUAL_PLAY) {
                virtual_deck_stop();
                ui_set_op_mode(OP_MODE_STANDBY);
            }
        }
    }

    // Process REC Button
    if (buttons_get_event(BTN_ID_REC) == BTN_EVENT_SHORT_PRESS) {
        if (s_current_screen == UI_SCREEN_AZIMUTH_TUNE) {
            motor_toggle_manual_override();
        } else {
            if (s_current_op_mode == OP_MODE_STANDBY) {
                digitizer_start("DUMP0001.CSW");
                ui_set_op_mode(OP_MODE_SIGNAL_DUMP);
            } else if (s_current_op_mode == OP_MODE_SIGNAL_DUMP) {
                digitizer_stop();
                ui_set_op_mode(OP_MODE_STANDBY);
            }
        }
    }

    // Render active screen
    oled_clear();
    switch (s_current_screen) {
        case UI_SCREEN_HOME:
            render_screen_home();
            break;
        case UI_SCREEN_FILE_BROWSER:
            render_screen_file_browser();
            break;
        case UI_SCREEN_AZIMUTH_TUNE:
            render_screen_azimuth_tune();
            break;
        case UI_SCREEN_EXERCISER:
            render_screen_exerciser();
            break;
        case UI_SCREEN_DIAGNOSTICS:
            render_screen_diagnostics();
            break;
        default:
            s_current_screen = UI_SCREEN_HOME;
            render_screen_home();
            break;
    }
    oled_update();
}
