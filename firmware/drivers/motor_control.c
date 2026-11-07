/**
 * Tape Master v2 - Motor Control & Sensing Implementation
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#include "motor_control.h"
#include "../config/hardware_pins.h"
#include "pico/stdlib.h"

static bool s_manual_override = false;
static bool s_motor_power_state = false;

void motor_control_init(void) {
    // GP12: Input - Motor sense from host computer
    gpio_init(PIN_MOTOR_SENSE);
    gpio_set_dir(PIN_MOTOR_SENSE, GPIO_IN);
    gpio_pull_down(PIN_MOTOR_SENSE);

    // GP13: Output - Motor power control (Relay / Pass-FET)
    gpio_init(PIN_MOTOR_CTRL);
    gpio_set_dir(PIN_MOTOR_CTRL, GPIO_OUT);
    gpio_put(PIN_MOTOR_CTRL, 0); // Initially OFF

    // GP14: Bidirectional / Open-Drain - Tape Sense line
    gpio_init(PIN_TAPE_SENSE);
    gpio_set_dir(PIN_TAPE_SENSE, GPIO_IN);
    gpio_pull_up(PIN_TAPE_SENSE);

    s_manual_override = false;
    s_motor_power_state = false;
}

bool motor_host_is_requesting_run(void) {
    // In Commodore C64, motor is controlled by active-low PNP pass transistor.
    // In Spectrum/MSX/Thomson, relay is closed.
    // Normalized in hardware conditioning: HIGH = Motor Run Request
    return gpio_get(PIN_MOTOR_SENSE);
}

void motor_set_power(bool enable) {
    s_motor_power_state = enable;
    gpio_put(PIN_MOTOR_CTRL, (s_motor_power_state || s_manual_override) ? 1 : 0);
}

void motor_toggle_manual_override(void) {
    s_manual_override = !s_manual_override;
    motor_set_power(s_motor_power_state);
}

bool motor_is_manual_override_active(void) {
    return s_manual_override;
}

bool motor_is_tape_sense_active(void) {
    // Active LOW: Sense switch grounded when PLAY key pressed
    return (gpio_get(PIN_TAPE_SENSE) == 0);
}

void motor_set_tape_sense_to_host(bool play_pressed) {
    if (play_pressed) {
        // Drive LOW to tell host PLAY key is pressed
        gpio_set_dir(PIN_TAPE_SENSE, GPIO_OUT);
        gpio_put(PIN_TAPE_SENSE, 0);
    } else {
        // Float HIGH (input with pull-up)
        gpio_set_dir(PIN_TAPE_SENSE, GPIO_IN);
        gpio_pull_up(PIN_TAPE_SENSE);
    }
}
