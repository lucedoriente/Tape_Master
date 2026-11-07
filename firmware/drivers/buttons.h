/**
 * Tape Master v2 - Tactile Buttons Driver
 * Debounced polling for PLAY, REC, PREV, NEXT, and Encoder Switch
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#ifndef BUTTONS_H
#define BUTTONS_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    BTN_ID_PLAY   = 0,
    BTN_ID_REC    = 1,
    BTN_ID_PREV   = 2,
    BTN_ID_NEXT   = 3,
    BTN_ID_ENC_SW = 4,
    BTN_COUNT     = 5
} button_id_t;

typedef enum {
    BTN_EVENT_NONE        = 0,
    BTN_EVENT_SHORT_PRESS = 1,
    BTN_EVENT_LONG_PRESS  = 2,
    BTN_EVENT_HOLD        = 3
} button_event_t;

/**
 * Initialize all button GPIOs with internal pull-ups.
 */
void buttons_init(void);

/**
 * Update button state machine (call periodically, e.g. every 5 or 10 ms).
 */
void buttons_poll(void);

/**
 * Get and clear pending event for a given button.
 */
button_event_t buttons_get_event(button_id_t btn);

/**
 * Check if a button is currently held down.
 */
bool buttons_is_down(button_id_t btn);

#ifdef __cplusplus
}
#endif

#endif // BUTTONS_H
