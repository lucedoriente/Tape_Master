/**
 * Tape Master v2 - Analog Front-End & Azimuth Peak ADC Driver
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#ifndef ANALOG_FRONTEND_H
#define ANALOG_FRONTEND_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Initialize ADC hardware and configure GP26 (ADC0) for Azimuth peak detection.
 */
void analog_frontend_init(void);

/**
 * Sample the peak detector analog level (0..4095, 12-bit ADC).
 * @return 12-bit ADC value (0 to 4095).
 */
uint16_t analog_sample_azimuth_raw(void);

/**
 * Convert the 12-bit azimuth sample to a scaled 0..10 level for the LED bar.
 * Uses adaptive smoothing / decay filter.
 * 
 * @return Value from 0 to 10.
 */
uint8_t analog_get_azimuth_bar_level(void);

/**
 * Sample the raw analog tape signal from head pre-amp (GP27 / ADC1).
 * @return 12-bit raw audio sample.
 */
uint16_t analog_sample_raw_tape(void);

#ifdef __cplusplus
}
#endif

#endif // ANALOG_FRONTEND_H
