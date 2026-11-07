/**
 * Tape Master v2 - TLC5916 Dual Cascaded LED Driver Implementation
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#include "tlc5916_leds.h"
#include "../config/hardware_pins.h"
#include "pico/stdlib.h"
#include "hardware/spi.h"

// Cached 16-bit word to shift into U2 (bits 15..8) and U1 (bits 7..0)
static uint16_t s_led_register_cache = 0;

void led_panel_init(void) {
    // Configure Latch Enable pin as GPIO Output (normally LOW)
    gpio_init(PIN_LEDBAR_LE);
    gpio_set_dir(PIN_LEDBAR_LE, GPIO_OUT);
    gpio_put(PIN_LEDBAR_LE, 0);

    // Initial state: turn on PWR LED (D6), all others off
    s_led_register_cache = LED_STATUS_PWR_BIT;
    led_panel_update();
}

void led_set_azimuth_level(uint8_t level, bool peak_dot) {
    if (level > 10) level = 10;

    // Clear all azimuth bits (Bits 0..9)
    s_led_register_cache &= ~(0x03FFu);

    if (level == 0) return;

    if (peak_dot) {
        // Light only the single peak dot
        s_led_register_cache |= (1u << (level - 1));
    } else {
        // Solid bargraph up to 'level'
        uint16_t bar_mask = (1u << level) - 1;
        s_led_register_cache |= (bar_mask & 0x03FFu);
    }
}

void led_set_status(status_led_t led, bool state) {
    uint16_t bitmask = 0;
    if (led & STATUS_LED_PLAY)   bitmask |= LED_STATUS_PLAY_BIT;
    if (led & STATUS_LED_REC)    bitmask |= LED_STATUS_REC_BIT;
    if (led & STATUS_LED_MOTOR)  bitmask |= LED_STATUS_MOTOR_BIT;
    if (led & STATUS_LED_SIGNAL) bitmask |= LED_STATUS_SIGNAL_BIT;
    if (led & STATUS_LED_PWR)    bitmask |= LED_STATUS_PWR_BIT;

    if (state) {
        s_led_register_cache |= bitmask;
    } else {
        s_led_register_cache &= ~bitmask;
    }
}

void led_toggle_status(status_led_t led) {
    uint16_t bitmask = 0;
    if (led & STATUS_LED_PLAY)   bitmask |= LED_STATUS_PLAY_BIT;
    if (led & STATUS_LED_REC)    bitmask |= LED_STATUS_REC_BIT;
    if (led & STATUS_LED_MOTOR)  bitmask |= LED_STATUS_MOTOR_BIT;
    if (led & STATUS_LED_SIGNAL) bitmask |= LED_STATUS_SIGNAL_BIT;
    if (led & STATUS_LED_PWR)    bitmask |= LED_STATUS_PWR_BIT;

    s_led_register_cache ^= bitmask;
}

void led_panel_update(void) {
    // Fast bit-bang transfer or SPI transfer.
    // Since SPI0 is shared with SD card, bit-banging the 16 bits guarantees
    // zero conflict with active SPI transactions to SD card.
    gpio_set_function(PIN_LEDBAR_CLK, GPIO_FUNC_SIO);
    gpio_set_function(PIN_LEDBAR_DATA, GPIO_FUNC_SIO);
    gpio_set_dir(PIN_LEDBAR_CLK, GPIO_OUT);
    gpio_set_dir(PIN_LEDBAR_DATA, GPIO_OUT);

    gpio_put(PIN_LEDBAR_CLK, 0);

    // Shift 16 bits MSB first (Bit 15 first into U2, down to Bit 0 in U1)
    for (int i = 15; i >= 0; i--) {
        bool bit = (s_led_register_cache >> i) & 0x01;
        gpio_put(PIN_LEDBAR_DATA, bit);
        sleep_us(1);
        gpio_put(PIN_LEDBAR_CLK, 1);
        sleep_us(1);
        gpio_put(PIN_LEDBAR_CLK, 0);
        sleep_us(1);
    }

    // Pulse Latch Enable (LE) HIGH to latch outputs
    gpio_put(PIN_LEDBAR_LE, 1);
    sleep_us(2);
    gpio_put(PIN_LEDBAR_LE, 0);

    // Restore pins to SPI function if SD card is using them
    gpio_set_function(PIN_LEDBAR_CLK, GPIO_FUNC_SPI);
    gpio_set_function(PIN_LEDBAR_DATA, GPIO_FUNC_SPI);
}

void led_panel_self_test(void) {
    // Chasing animation on Azimuth bar
    for (uint8_t i = 1; i <= 10; i++) {
        led_set_azimuth_level(i, false);
        led_panel_update();
        sleep_ms(30);
    }
    for (int8_t i = 10; i >= 0; i--) {
        led_set_azimuth_level(i, false);
        led_panel_update();
        sleep_ms(30);
    }

    // Blink each status LED
    status_led_t leds[] = {STATUS_LED_PLAY, STATUS_LED_REC, STATUS_LED_MOTOR, STATUS_LED_SIGNAL, STATUS_LED_PWR};
    for (int i = 0; i < 5; i++) {
        led_set_status(leds[i], true);
        led_panel_update();
        sleep_ms(60);
        led_set_status(leds[i], false);
    }

    // Restore PWR LED
    led_set_status(STATUS_LED_PWR, true);
    led_panel_update();
}
