/**
 * Tape / Cassette Master Exerciser & Signal Digitizer v2.0
 * Firmware for Raspberry Pi Pico (RP2040 Dual-Core)
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 * 
 * Target Hardware: Tape Master v2 Mainboard & UI Panel (KiCad 9.0)
 * Dual TLC5916 Shift Registers (10 Bargraph + 5 Status LEDs)
 * Precision TLV2372 Analog Signal Chain & LM393 Zero-Crossing Digitizer
 * Smart Cartridge Auto-ID (24C02 I2C) & 40-Pin Universal Expansion Slot
 */

#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#include "pico/stdlib.h"
#include "pico/multicore.h"
#include "hardware/pio.h"
#include "hardware/dma.h"
#include "hardware/i2c.h"
#include "hardware/spi.h"
#include "hardware/adc.h"

#include "config/hardware_pins.h"
#include "config/version.h"

#include "drivers/tlc5916_leds.h"
#include "drivers/cartridge_id.h"
#include "drivers/buttons.h"
#include "drivers/encoder.h"
#include "drivers/oled_display.h"
#include "drivers/analog_frontend.h"
#include "drivers/motor_control.h"
#include "drivers/sd_card.h"
#include "drivers/fat_fs.h"

#include "engine/virtual_deck.h"
#include "engine/signal_digitizer.h"
#include "engine/exerciser_engine.h"
#include "engine/host_protocol.h"

#include "ui/ui_menu.h"

// ==============================================================================
// CORE 1: REAL-TIME TAPE ENGINE (ZERO JITTER EXECUTION)
// ==============================================================================
static void core1_entry(void) {
    // Core 1 is dedicated exclusively to hard real-time execution:
    // - Pushing pulse intervals to PIO TX FIFO (Virtual Deck)
    // - Pulling measured pulse intervals from PIO RX FIFO (Digitizer)
    // - Generating audio calibration frequencies (Exerciser)
    while (1) {
        op_mode_t mode = ui_get_op_mode();

        if (mode == OP_MODE_VIRTUAL_PLAY) {
            virtual_deck_core1_worker();
        } else if (mode == OP_MODE_SIGNAL_DUMP) {
            digitizer_core1_worker();
        } else if (mode == OP_MODE_EXERCISER) {
            exerciser_core1_worker();
        } else {
            sleep_us(100);
        }
    }
}

// ==============================================================================
// CORE 0: APPLICATION, USER INTERFACE & HOT-PLUG MANAGEMENT
// ==============================================================================
int main(void) {
    // 1. Initialize system clock and stdio USB
    stdio_init_all();
    sleep_ms(100);

    // 2. Initialize Hardware Subsystems
    led_panel_init();
    buttons_init();
    encoder_init();
    motor_control_init();
    analog_frontend_init();
    oled_init();
    cartridge_manager_init();

    // 3. Initialize Storage & Filesystem
    sd_card_init();
    fat_mount();

    // 4. Initialize Core Processing Engines
    virtual_deck_init();
    digitizer_init();
    exerciser_init();
    host_protocol_init();
    ui_menu_init();

    // 5. Power-On Self Test (POST) LED animation
    led_panel_self_test();

    // 6. Initial Cartridge Probe
    if (cartridge_is_inserted()) {
        cartridge_descriptor_t desc;
        if (cartridge_read_descriptor(&desc)) {
            ui_notify_cartridge_changed(&desc);
        } else {
            cartridge_descriptor_t fallback;
            memset(&fallback, 0, sizeof(fallback));
            fallback.id = CART_ID_UNKNOWN;
            strncpy(fallback.platform_name, "Cartuccia Inserita", sizeof(fallback.platform_name) - 1);
            ui_notify_cartridge_changed(&fallback);
        }
    } else {
        ui_notify_cartridge_changed(NULL);
    }

    // 7. Launch Core 1 for Real-Time Execution
    multicore_launch_core1(core1_entry);

    // 8. Core 0 Main Event Loop (~20 ms period / 50 Hz)
    while (1) {
        // Poll buttons and rotary encoder
        buttons_poll();
        encoder_update();

        // Check for Smart Cartridge Hot-Plug Events
        if (cartridge_poll_state_change()) {
            if (cartridge_is_inserted()) {
                sleep_ms(50); // Debounce cartridge insertion contacts
                cartridge_descriptor_t desc;
                if (cartridge_read_descriptor(&desc)) {
                    ui_notify_cartridge_changed(&desc);
                } else {
                    cartridge_descriptor_t fallback;
                    memset(&fallback, 0, sizeof(fallback));
                    fallback.id = CART_ID_UNKNOWN;
                    strncpy(fallback.platform_name, "Cartuccia Rilevata", sizeof(fallback.platform_name) - 1);
                    ui_notify_cartridge_changed(&fallback);
                }
            } else {
                ui_notify_cartridge_changed(NULL);
                ui_set_op_mode(OP_MODE_STANDBY);
            }
        }

        // Engine updates (SD buffering, state machines)
        op_mode_t mode = ui_get_op_mode();
        if (mode == OP_MODE_VIRTUAL_PLAY) {
            virtual_deck_update();
        } else if (mode == OP_MODE_SIGNAL_DUMP) {
            digitizer_update();
        } else if (mode == OP_MODE_EXERCISER) {
            exerciser_update();
        }

        // Update UI Menu and OLED Display
        ui_menu_update();

        // Process USB Serial host communication
        host_protocol_poll();

        // Commit LED panel shifts
        led_panel_update();

        // 20 ms loop delay (~50 Hz UI refresh)
        sleep_ms(20);
    }

    return 0;
}
