/**
 * Tape Master v2 - Rotary Encoder Driver
 * Quadrature decoder with transition state machine
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#ifndef ENCODER_H
#define ENCODER_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Initialize GPIOs for Rotary Encoder channels A & B with internal pull-ups.
 */
void encoder_init(void);

/**
 * Update encoder state machine (called periodically or on pin change).
 */
void encoder_update(void);

/**
 * Read the delta accumulated since last call (e.g. +1 for clockwise, -1 for counter-clockwise).
 */
int32_t encoder_get_delta(void);

/**
 * Reset accumulated position count.
 */
void encoder_reset(void);

#ifdef __cplusplus
}
#endif

#endif // ENCODER_H
