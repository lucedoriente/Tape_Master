/**
 * Tape Master v2 - Rotary Encoder Implementation
 * Quadrature decoding state machine with 4x resolution
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#include "encoder.h"
#include "../config/hardware_pins.h"
#include "pico/stdlib.h"

// Quadrature transition lookup table:
// Index: (old_state << 2) | new_state
// Values: +1 (CW), -1 (CCW), 0 (invalid/no change)
static const int8_t s_quad_table[16] = {
    0, -1,  1,  0,
    1,  0,  0, -1,
   -1,  0,  0,  1,
    0,  1, -1,  0
};

static uint8_t s_last_state = 0;
static int32_t s_sub_step_accum = 0;
static int32_t s_delta_accum = 0;

void encoder_init(void) {
    gpio_init(PIN_ENC_A);
    gpio_init(PIN_ENC_B);
    gpio_set_dir(PIN_ENC_A, GPIO_IN);
    gpio_set_dir(PIN_ENC_B, GPIO_IN);
    gpio_pull_up(PIN_ENC_A);
    gpio_pull_up(PIN_ENC_B);

    uint8_t a = gpio_get(PIN_ENC_A) ? 1 : 0;
    uint8_t b = gpio_get(PIN_ENC_B) ? 1 : 0;
    s_last_state = (a << 1) | b;
    s_sub_step_accum = 0;
    s_delta_accum = 0;
}

void encoder_update(void) {
    uint8_t a = gpio_get(PIN_ENC_A) ? 1 : 0;
    uint8_t b = gpio_get(PIN_ENC_B) ? 1 : 0;
    uint8_t current_state = (a << 1) | b;

    uint8_t index = (s_last_state << 2) | current_state;
    int8_t step = s_quad_table[index];

    if (step != 0) {
        s_sub_step_accum += step;
        // Standard mechanical encoders have detents every 4 transitions (or 2)
        if (s_sub_step_accum >= 4) {
            s_delta_accum++;
            s_sub_step_accum = 0;
        } else if (s_sub_step_accum <= -4) {
            s_delta_accum--;
            s_sub_step_accum = 0;
        }
    }
    s_last_state = current_state;
}

int32_t encoder_get_delta(void) {
    int32_t d = s_delta_accum;
    s_delta_accum = 0;
    return d;
}

void encoder_reset(void) {
    s_sub_step_accum = 0;
    s_delta_accum = 0;
}
