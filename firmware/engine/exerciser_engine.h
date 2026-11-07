/**
 * Tape Master v2 - Hardware Exerciser & Diagnostics Engine
 * 
 * Standalone calibration tones (1 kHz / 2 kHz), motor burn-in cycle,
 * loopback pulse timing verification and real-time Azimuth head alignment.
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#ifndef EXERCISER_ENGINE_H
#define EXERCISER_ENGINE_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    EXERCISER_IDLE,
    EXERCISER_CAL_TONE_1KHZ,
    EXERCISER_CAL_TONE_2KHZ,
    EXERCISER_MOTOR_RUN,
    EXERCISER_LOOPBACK_TEST,
    EXERCISER_AZIMUTH_MONITOR
} exerciser_mode_t;

typedef struct {
    exerciser_mode_t mode;
    bool             active;
    uint32_t         duration_seconds;
    uint8_t          azimuth_peak_level;
    uint32_t         loopback_sent;
    uint32_t         loopback_received;
    uint32_t         loopback_errors;
    bool             loopback_passed;
} exerciser_status_t;

/**
 * Initialize exerciser subsystem.
 */
void exerciser_init(void);

/**
 * Set and start an exerciser test mode.
 */
void exerciser_start(exerciser_mode_t mode);

/**
 * Stop active exerciser test.
 */
void exerciser_stop(void);

/**
 * Periodic update loop (called from Core 0).
 */
void exerciser_update(void);

/**
 * High-precision tone / pulse generation loop (called from Core 1).
 */
void exerciser_core1_worker(void);

/**
 * Get current exerciser status and test results.
 */
void exerciser_get_status(exerciser_status_t *out_status);

#ifdef __cplusplus
}
#endif

#endif // EXERCISER_ENGINE_H
