/**
 * Tape Master v2 - Motor Control & Sensing Driver
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#ifndef MOTOR_CONTROL_H
#define MOTOR_CONTROL_H

#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Initialize Motor Sense (GP12), Motor Control (GP13), and Tape Sense (GP14).
 */
void motor_control_init(void);

/**
 * Check if the host retrocomputer is commanding motor ON.
 * @return true if computer asserts motor line.
 */
bool motor_host_is_requesting_run(void);

/**
 * Enable or disable physical tape motor via relay / pass-FET.
 * 
 * @param enable true to energize motor, false to brake/stop.
 */
void motor_set_power(bool enable);

/**
 * Toggle manual motor override (force run mode).
 */
void motor_toggle_manual_override(void);

/**
 * Check if manual motor override is currently active.
 */
bool motor_is_manual_override_active(void);

/**
 * Check if the Datassette/deck 'Play' key sense switch is closed.
 */
bool motor_is_tape_sense_active(void);

/**
 * Assert or release the Sense line back to the host computer.
 * (e.g. telling Commodore PET/C64 that PLAY key has been pressed).
 */
void motor_set_tape_sense_to_host(bool play_pressed);

#ifdef __cplusplus
}
#endif

#endif // MOTOR_CONTROL_H
