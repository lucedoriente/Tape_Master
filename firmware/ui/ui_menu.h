/**
 * Tape Master v2 - User Interface & Menu State Machine
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#ifndef UI_MENU_H
#define UI_MENU_H

#include <stdint.h>
#include <stdbool.h>
#include "../drivers/cartridge_id.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    UI_SCREEN_HOME          = 0,
    UI_SCREEN_FILE_BROWSER  = 1,
    UI_SCREEN_AZIMUTH_TUNE  = 2,
    UI_SCREEN_DIAGNOSTICS   = 3,
    UI_SCREEN_EXERCISER     = 4
} ui_screen_t;

typedef enum {
    OP_MODE_STANDBY         = 0,
    OP_MODE_VIRTUAL_PLAY    = 1,
    OP_MODE_SIGNAL_DUMP     = 2,
    OP_MODE_EXERCISER       = 3
} op_mode_t;

/**
 * Initialize UI subsystem, set default screen.
 */
void ui_menu_init(void);

/**
 * Periodic UI update loop (call every 20-50 ms from Core 0).
 */
void ui_menu_update(void);

/**
 * Notify UI that the active cartridge has changed.
 */
void ui_notify_cartridge_changed(const cartridge_descriptor_t *desc);

/**
 * Set current operational mode.
 */
void ui_set_op_mode(op_mode_t mode);

/**
 * Get current operational mode.
 */
op_mode_t ui_get_op_mode(void);

/**
 * Switch to a specific UI screen.
 */
void ui_set_screen(ui_screen_t screen);

#ifdef __cplusplus
}
#endif

#endif // UI_MENU_H
