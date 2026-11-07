/**
 * Tape Master v2 - Virtual Deck Playback Engine
 * 
 * Streams pulse intervals from .TAP, .TZX, or .CSW files to the PIO TX FIFO
 * with zero-jitter real-time execution and host MOTOR_SENSE auto-pause/resume.
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#ifndef VIRTUAL_DECK_H
#define VIRTUAL_DECK_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "../drivers/fat_fs.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    DECK_STATE_STOPPED,
    DECK_STATE_PLAYING,
    DECK_STATE_PAUSED_MOTOR,    // Paused because host computer stopped deck motor
    DECK_STATE_PAUSED_USER,     // Paused by user pressing PLAY button again
    DECK_STATE_COMPLETED,
    DECK_STATE_ERROR
} deck_state_t;

typedef enum {
    DECK_FORMAT_UNKNOWN,
    DECK_FORMAT_TAP_C64,
    DECK_FORMAT_TZX_SPECTRUM,
    DECK_FORMAT_CSW_RAW
} deck_format_t;

typedef struct {
    deck_state_t  state;
    deck_format_t format;
    char          filename[FAT_MAX_FILENAME];
    uint32_t      total_bytes;
    uint32_t      bytes_processed;
    uint32_t      total_pulses;
    uint32_t      elapsed_seconds;
    uint8_t       progress_percent;
    bool          ignore_motor_sense; // Option to force playback even if host motor line is low
} virtual_deck_status_t;

/**
 * Initialize virtual deck hardware resources (PIO state machine, DMA, ring buffers).
 */
void virtual_deck_init(void);

/**
 * Load and start playback of a tape image from SD card.
 * 
 * @param filename File path on SD card (e.g. "GianaSisters.tap").
 * @return true if file valid and playback commenced.
 */
bool virtual_deck_start(const char *filename);

/**
 * Pause playback (User toggle).
 */
void virtual_deck_pause(void);

/**
 * Resume playback from paused state.
 */
void virtual_deck_resume(void);

/**
 * Stop playback and reset engine state.
 */
void virtual_deck_stop(void);

/**
 * Virtual deck main loop update (called periodically by Core 0).
 * Handles SD card streaming, double-buffer refill, progress tracking.
 */
void virtual_deck_update(void);

/**
 * Real-time PIO FIFO feeder (called continuously by Core 1).
 * High-priority zero-jitter loop.
 */
void virtual_deck_core1_worker(void);

/**
 * Get current playback status snapshot.
 */
void virtual_deck_get_status(virtual_deck_status_t *out_status);

#ifdef __cplusplus
}
#endif

#endif // VIRTUAL_DECK_H
