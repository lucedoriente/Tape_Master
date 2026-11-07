/**
 * Tape Master v2 - OLED Display Driver (SSD1306 / SH1106 128x64 I2C)
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#ifndef OLED_DISPLAY_H
#define OLED_DISPLAY_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define OLED_WIDTH              128
#define OLED_HEIGHT              64

/**
 * Initialize I2C hardware and SSD1306/SH1106 controller.
 */
bool oled_init(void);

/**
 * Clear the internal RAM display buffer (all pixels black).
 */
void oled_clear(void);

/**
 * Push the internal 1024-byte RAM buffer to the physical OLED via I2C.
 */
void oled_update(void);

/**
 * Basic graphics primitives.
 */
void oled_draw_pixel(int16_t x, int16_t y, bool color);
void oled_draw_line(int16_t x0, int16_t y0, int16_t x1, int16_t y1, bool color);
void oled_draw_rect(int16_t x, int16_t y, int16_t w, int16_t h, bool filled, bool color);
void oled_draw_progress_bar(int16_t x, int16_t y, int16_t w, int16_t h, uint8_t percent);

/**
 * Text printing primitives.
 */
void oled_draw_char(int16_t x, int16_t y, char c, bool color);
void oled_draw_string(int16_t x, int16_t y, const char *str, bool color);
void oled_draw_string_formatted(int16_t x, int16_t y, bool color, const char *fmt, ...);

/**
 * Power management.
 */
void oled_set_contrast(uint8_t contrast);
void oled_set_display_on(bool on);

#ifdef __cplusplus
}
#endif

#endif // OLED_DISPLAY_H
