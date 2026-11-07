/**
 * Tape Master v2 - Hardware Exerciser & Diagnostics Engine Implementation
 * 
 * Standalone calibration tones (1 kHz / 2 kHz), motor burn-in cycle,
 * loopback pulse timing verification and real-time Azimuth head alignment.
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#include "exerciser_engine.h"
#include "../config/hardware_pins.h"
#include "../drivers/motor_control.h"
#include "../drivers/analog_frontend.h"
#include "../drivers/tlc5916_leds.h"

#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include <string.h>

static exerciser_status_t s_status;
static absolute_time_t    s_start_time;
static uint32_t           s_tone_half_period_us = 500; // 500 us = 1000 Hz
static bool               s_pin_toggle = false;

void exerciser_init(void) {
    memset(&s_status, 0, sizeof(s_status));
    s_status.mode = EXERCISER_IDLE;
    s_status.active = false;
}

void exerciser_start(exerciser_mode_t mode) {
    exerciser_stop();

    s_status.mode = mode;
    s_status.active = true;
    s_status.duration_seconds = 0;
    s_status.loopback_sent = 0;
    s_status.loopback_received = 0;
    s_status.loopback_errors = 0;
    s_status.loopback_passed = false;
    s_start_time = get_absolute_time();

    switch (mode) {
        case EXERCISER_CAL_TONE_1KHZ:
            s_tone_half_period_us = 500; // 1000 Hz (T = 1000 us, half = 500 us)
            gpio_set_function(PIN_TAPE_EMU_OUT, GPIO_FUNC_SIO);
            gpio_set_dir(PIN_TAPE_EMU_OUT, GPIO_OUT);
            led_set_status(STATUS_LED_SIGNAL, true);
            break;

        case EXERCISER_CAL_TONE_2KHZ:
            s_tone_half_period_us = 250; // 2000 Hz (T = 500 us, half = 250 us)
            gpio_set_function(PIN_TAPE_EMU_OUT, GPIO_FUNC_SIO);
            gpio_set_dir(PIN_TAPE_EMU_OUT, GPIO_OUT);
            led_set_status(STATUS_LED_SIGNAL, true);
            break;

        case EXERCISER_MOTOR_RUN:
            motor_set_control(true);
            led_set_status(STATUS_LED_MOTOR, true);
            break;

        case EXERCISER_LOOPBACK_TEST:
            gpio_set_function(PIN_TAPE_EMU_OUT, GPIO_FUNC_SIO);
            gpio_set_dir(PIN_TAPE_EMU_OUT, GPIO_OUT);
            gpio_set_function(PIN_TAPE_DIGITIZED, GPIO_FUNC_SIO);
            gpio_set_dir(PIN_TAPE_DIGITIZED, GPIO_IN);
            break;

        case EXERCISER_AZIMUTH_MONITOR:
            // Continuous ADC monitoring with peak dot
            break;

        default:
            break;
    }
}

void exerciser_stop(void) {
    if (!s_status.active) return;

    motor_set_control(false);
    led_set_status(STATUS_LED_MOTOR, false);
    led_set_status(STATUS_LED_SIGNAL, false);
    led_set_azimuth_level(0, false);

    gpio_put(PIN_TAPE_EMU_OUT, 1);

    s_status.active = false;
    s_status.mode = EXERCISER_IDLE;
}

void exerciser_update(void) {
    if (!s_status.active) return;

    s_status.duration_seconds = (uint32_t)(absolute_time_diff_us(s_start_time, get_absolute_time()) / 1000000);

    if (s_status.mode == EXERCISER_AZIMUTH_MONITOR || s_status.mode == EXERCISER_MOTOR_RUN) {
        uint8_t lvl = analog_read_azimuth_level();
        s_status.azimuth_peak_level = lvl;
        led_set_azimuth_level(lvl, false);
    }

    if (s_status.mode == EXERCISER_LOOPBACK_TEST) {
        // Run 100 test pulse iterations
        for (int i = 0; i < 20; i++) {
            s_status.loopback_sent++;

            // Emit 25 us pulse
            gpio_put(PIN_TAPE_EMU_OUT, 0);
            sleep_us(25);
            bool rx_val_low = (gpio_get(PIN_TAPE_DIGITIZED) == 0);

            gpio_put(PIN_TAPE_EMU_OUT, 1);
            sleep_us(25);
            bool rx_val_high = (gpio_get(PIN_TAPE_DIGITIZED) == 1);

            if (rx_val_low && rx_val_high) {
                s_status.loopback_received++;
            } else {
                s_status.loopback_errors++;
            }
        }

        if (s_status.loopback_sent >= 1000) {
            s_status.loopback_passed = (s_status.loopback_errors == 0);
            exerciser_stop();
        }
    }
}

void exerciser_core1_worker(void) {
    if (!s_status.active) return;

    if (s_status.mode == EXERCISER_CAL_TONE_1KHZ || s_status.mode == EXERCISER_CAL_TONE_2KHZ) {
        s_pin_toggle = !s_pin_toggle;
        gpio_put(PIN_TAPE_EMU_OUT, s_pin_toggle);
        sleep_us(s_tone_half_period_us);
    }
}

void exerciser_get_status(exerciser_status_t *out_status) {
    if (out_status) {
        memcpy(out_status, &s_status, sizeof(exerciser_status_t));
    }
}
