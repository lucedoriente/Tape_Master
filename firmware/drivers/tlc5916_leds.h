/**
 * Tape Master v2 - TLC5916 Dual Cascaded LED Driver
 * Drives 10-segment Azimuth VU-Meter + 5 Universal Status LEDs (16 channels)
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#ifndef TLC5916_LEDS_H
#define TLC5916_LEDS_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Status LED Identifiers
typedef enum {
    STATUS_LED_PLAY   = (1u << 0),  // Green D2
    STATUS_LED_REC    = (1u << 1),  // Red D3
    STATUS_LED_MOTOR  = (1u << 2),  // Yellow D4
    STATUS_LED_SIGNAL = (1u << 3),  // Blue D5
    STATUS_LED_PWR    = (1u << 4)   // Green D6
} status_led_t;

/**
 * Initialize GPIOs for TLC5916 shift registers.
 */
void led_panel_init(void);

/**
 * Set the Azimuth / VU-Meter bar level (0 = all off, 1..10 active segments).
 * Segments 1..8: Green (D10..D17)
 * Segment 9: Yellow (D18)
 * Segment 10: Red (D19)
 * 
 * @param level Value from 0 to 10.
 * @param peak_dot If true, displays single peak dot instead of solid bar.
 */
void led_set_azimuth_level(uint8_t level, bool peak_dot);

/**
 * Turn on, off or toggle individual status LEDs.
 * 
 * @param led One or more OR-ed flags from status_led_t.
 * @param state true to turn on, false to turn off.
 */
void led_set_status(status_led_t led, bool state);
void led_toggle_status(status_led_t led);

/**
 * Commit the cached 16-bit pattern to the physical TLC5916 shift registers.
 * Uses hardware SPI0 or fast bit-banging and pulses Latch Enable (LE).
 */
void led_panel_update(void);

/**
 * Test pattern / animation for power-on self test (POST).
 */
void led_panel_self_test(void);

#ifdef __cplusplus
}
#endif

#endif // TLC5916_LEDS_H
