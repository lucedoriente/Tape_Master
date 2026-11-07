/**
 * Tape Master v2 - Analog Front-End & Azimuth Peak ADC Implementation
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#include "analog_frontend.h"
#include "../config/hardware_pins.h"
#include "pico/stdlib.h"
#include "hardware/adc.h"

// Exponential moving average filter
static uint32_t s_filtered_azimuth = 0;

void analog_frontend_init(void) {
    adc_init();

    // Enable ADC input pin for Azimuth Peak Detector (GP26 / ADC0)
    adc_gpio_init(PIN_AZIMUTH_PEAK_ADC);

    // Enable ADC input pin for Raw Tape Input (GP27 / ADC1)
    adc_gpio_init(PIN_TAPE_RAW_ADC);

    s_filtered_azimuth = 0;
}

uint16_t analog_sample_azimuth_raw(void) {
    adc_select_input(ADC_CHANNEL_AZIMUTH);
    return adc_read();
}

uint8_t analog_get_azimuth_bar_level(void) {
    uint16_t raw = analog_sample_azimuth_raw();

    // Filter with attack/decay: fast attack, slow decay for peak meter effect
    if (raw > (s_filtered_azimuth >> 4)) {
        s_filtered_azimuth = (uint32_t)raw << 4; // Fast peak response
    } else {
        if (s_filtered_azimuth > 16) {
            s_filtered_azimuth -= 16;            // Smooth decay
        }
    }

    uint16_t val = s_filtered_azimuth >> 4;

    // Linear mapping with noise floor squelch:
    // Floor: < 150 counts (~120 mV) -> 0 LEDs
    // Full scale: ~3500 counts (~2.8 V) -> 10 LEDs
    if (val < 150) return 0;
    if (val >= 3500) return 10;

    uint32_t scaled = ((uint32_t)(val - 150) * 10) / (3500 - 150) + 1;
    if (scaled > 10) scaled = 10;
    return (uint8_t)scaled;
}

uint16_t analog_sample_raw_tape(void) {
    adc_select_input(ADC_CHANNEL_TAPE_RAW);
    return adc_read();
}
