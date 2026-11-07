/**
 * Tape Master v2 - Signal Digitizer & Tape Ingestion Engine
 * 
 * Captures sub-microsecond pulse intervals from physical tape deck via PIO RX,
 * performs real-time RLE compression into Compressed Square Wave (.CSW v2),
 * monitors Azimuth peak level and writes dump to MicroSD.
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#ifndef SIGNAL_DIGITIZER_H
#define SIGNAL_DIGITIZER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "../drivers/fat_fs.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    DIGITIZER_STATE_IDLE,
    DIGITIZER_STATE_ARMED,      // Waiting for first pulse or motor enable
    DIGITIZER_STATE_RECORDING,
    DIGITIZER_STATE_STOPPED,
    DIGITIZER_STATE_ERROR
} digitizer_state_t;

typedef struct {
    digitizer_state_t state;
    char              filename[FAT_MAX_FILENAME];
    uint32_t          total_pulses;
    uint32_t          bytes_written;
    uint32_t          elapsed_seconds;
    uint16_t          min_pulse_us;
    uint16_t          max_pulse_us;
    uint8_t           azimuth_level; // 0..10 for LED VU-meter
    uint32_t          fifo_overruns;
} digitizer_status_t;

/**
 * Initialize digitizer hardware (PIO RX state machine, ADC).
 */
void digitizer_init(void);

/**
 * Start digitization / recording session to file on SD card.
 * 
 * @param output_filename Target CSW filename (e.g. "DUMP0001.CSW").
 * @return true if armed/started successfully.
 */
bool digitizer_start(const char *output_filename);

/**
 * Stop active recording, finalize CSW header and flush to SD.
 */
void digitizer_stop(void);

/**
 * Digitizer Core 0 update (handles SD card block writing, metrics).
 */
void digitizer_update(void);

/**
 * Real-time PIO RX FIFO reader (called continuously by Core 1).
 */
void digitizer_core1_worker(void);

/**
 * Get current digitizer metrics snapshot.
 */
void digitizer_get_status(digitizer_status_t *out_status);

#ifdef __cplusplus
}
#endif

#endif // SIGNAL_DIGITIZER_H
