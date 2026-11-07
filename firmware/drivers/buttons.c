/**
 * Tape Master v2 - Tactile Buttons Driver Implementation
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#include "buttons.h"
#include "../config/hardware_pins.h"
#include "pico/stdlib.h"

#define DEBOUNCE_TICKS          3    // ~30 ms at 10ms poll
#define LONG_PRESS_TICKS       70    // ~700 ms at 10ms poll

typedef struct {
    uint8_t  pin;
    uint8_t  debounce_count;
    uint16_t pressed_ticks;
    bool     stable_state;      // true if pressed (LOW)
    bool     long_press_fired;
    button_event_t pending_event;
} button_state_t;

static button_state_t s_buttons[BTN_COUNT] = {
    [BTN_ID_PLAY]   = { .pin = PIN_BTN_PLAY },
    [BTN_ID_REC]    = { .pin = PIN_BTN_REC },
    [BTN_ID_PREV]   = { .pin = PIN_BTN_PREV },
    [BTN_ID_NEXT]   = { .pin = PIN_BTN_NEXT },
    [BTN_ID_ENC_SW] = { .pin = PIN_ENC_SW }
};

void buttons_init(void) {
    for (int i = 0; i < BTN_COUNT; i++) {
        uint pin = s_buttons[i].pin;
        gpio_init(pin);
        gpio_set_dir(pin, GPIO_IN);
        gpio_pull_up(pin);
        s_buttons[i].debounce_count = 0;
        s_buttons[i].pressed_ticks = 0;
        s_buttons[i].stable_state = false;
        s_buttons[i].long_press_fired = false;
        s_buttons[i].pending_event = BTN_EVENT_NONE;
    }
}

void buttons_poll(void) {
    for (int i = 0; i < BTN_COUNT; i++) {
        button_state_t *b = &s_buttons[i];
        bool raw_pressed = (gpio_get(b->pin) == 0); // Active LOW

        if (raw_pressed != b->stable_state) {
            b->debounce_count++;
            if (b->debounce_count >= DEBOUNCE_TICKS) {
                b->stable_state = raw_pressed;
                b->debounce_count = 0;

                if (b->stable_state) {
                    // Button was just pressed down
                    b->pressed_ticks = 0;
                    b->long_press_fired = false;
                } else {
                    // Button was released
                    if (!b->long_press_fired && b->pressed_ticks > 0) {
                        b->pending_event = BTN_EVENT_SHORT_PRESS;
                    }
                    b->pressed_ticks = 0;
                }
            }
        } else {
            b->debounce_count = 0;
        }

        // If held down, track long press
        if (b->stable_state) {
            b->pressed_ticks++;
            if (b->pressed_ticks >= LONG_PRESS_TICKS && !b->long_press_fired) {
                b->pending_event = BTN_EVENT_LONG_PRESS;
                b->long_press_fired = true;
            }
        }
    }
}

button_event_t buttons_get_event(button_id_t btn) {
    if (btn >= BTN_COUNT) return BTN_EVENT_NONE;
    button_event_t ev = s_buttons[btn].pending_event;
    s_buttons[btn].pending_event = BTN_EVENT_NONE;
    return ev;
}

bool buttons_is_down(button_id_t btn) {
    if (btn >= BTN_COUNT) return false;
    return s_buttons[btn].stable_state;
}
