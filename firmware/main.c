/**
 * Tape / Cassette Master Exerciser & Signal Digitizer
 * Firmware for Raspberry Pi Pico (RP2040)
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 * 
 * Target Hardware: Tape Master PCB Rev 1.0 (KiCad 9.0)
 * Dual TLC5916 Constant-Current Shift Registers (10 Bargraph + 4 Status LEDs)
 * Precision Rail-to-Rail TLV2372 Analog Signal Chain & LM393 Digitizer
 */

#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include "pico/stdlib.h"
#include "pico/multicore.h"
#include "hardware/pio.h"
#include "hardware/dma.h"
#include "hardware/i2c.h"
#include "hardware/spi.h"
#include "hardware/adc.h"

// ==============================================================================
// Hardware Pin Definitions (strictly matching KiCad schematic Tape-Master)
// ==============================================================================
#define PIN_I2C_SDA            0   // GP0 (OLED SDA)
#define PIN_I2C_SCL            1   // GP1 (OLED SCL)
#define PIN_ENC_A              2   // GP2 (Rotary Encoder A)
#define PIN_ENC_B              3   // GP3 (Rotary Encoder B)
#define PIN_ENC_SW             4   // GP4 (Rotary Encoder Switch)

#define PIN_BTN_PLAY_STOP      5   // GP5 (SW2)
#define PIN_BTN_REC_DUMP       6   // GP6 (SW3)
#define PIN_BTN_REW_PREV       7   // GP7 (SW4)
#define PIN_BTN_FFWD_NEXT      8   // GP8 (SW5)

#define PIN_SPARE_GP9          9   // GP9 (Spare expansion GPIO)

#define PIN_LEDBAR_CLK         10  // GP10 (TLC5916 Shift Clock)
#define PIN_LEDBAR_DATA        11  // GP11 (TLC5916 Serial Data In - SDI)
#define PIN_LEDBAR_LE          12  // GP12 (TLC5916 Latch Enable - LE)

#define PIN_TAPE_DIGITIZED     13  // GP13 (Digitized square wave from LM393)
#define PIN_C64_MOTOR_SENSE    14  // GP14 (Sense motor line from C64/C2N)
#define PIN_C64_READ           15  // GP15 (Read pulses out to C64 via 74HCT06)

#define PIN_SD_MISO            16  // GP16 (SPI0 RX)
#define PIN_SD_CS              17  // GP17 (SPI0 CS)
#define PIN_SD_SCK             18  // GP18 (SPI0 SCK)
#define PIN_SD_MOSI            19  // GP19 (SPI0 TX)

#define PIN_C64_WRITE          20  // GP20 (Write pulses in from C64)
#define PIN_C64_SENSE_DRIVE    21  // GP21 (Sense switch drive out via 2N7002)
#define PIN_AUDIO_OUT_PWM      22  // GP22 (Sinclair ZX / Apple audio PWM out)

#define PIN_AZIMUTH_PEAK_ADC   26  // GP26 / ADC0 (Peak detector analog level)
#define PIN_REMOTE_DRIVE       27  // GP27 (Opto-isolated motor remote relay)
#define PIN_SPARE_GP28         28  // GP28 / ADC2 (Spare expansion GPIO/ADC)

// ==============================================================================
// TLC5916 Dual Shift Register Bitfield (16 channels total)
// ==============================================================================
// U7 (TLC5916 #1): bits 0..7 drive Bargraph LEDs D10..D17 (VU Green 1..8)
// U11 (TLC5916 #2): bits 8..9 drive Bargraph LEDs D18..D19 (VU Yellow 1, VU Red 1)
//                   bit 10: LED_READ (D2 Green)
//                   bit 11: LED_WRITE (D3 Red)
//                   bit 12: LED_MOTOR (D4 Yellow)
//                   bit 13: LED_SIGNAL (D5 Blue)
//                   bits 14..15: Unused / Spare
#define LED_VU_MASK            0x03FF  // 10 Bargraph LEDs (bits 0..9)
#define LED_STATUS_READ        (1 << 10)
#define LED_STATUS_WRITE       (1 << 11)
#define LED_STATUS_MOTOR       (1 << 12)
#define LED_STATUS_SIGNAL      (1 << 13)

static inline void tlc5916_init(void) {
    gpio_init(PIN_LEDBAR_CLK);
    gpio_set_dir(PIN_LEDBAR_CLK, GPIO_OUT);
    gpio_put(PIN_LEDBAR_CLK, 0);

    gpio_init(PIN_LEDBAR_DATA);
    gpio_set_dir(PIN_LEDBAR_DATA, GPIO_OUT);
    gpio_put(PIN_LEDBAR_DATA, 0);

    gpio_init(PIN_LEDBAR_LE);
    gpio_set_dir(PIN_LEDBAR_LE, GPIO_OUT);
    gpio_put(PIN_LEDBAR_LE, 0);
}

/**
 * Output 16-bit word to dual cascaded TLC5916 LED drivers.
 * Bit = 1 -> Constant-current sink active (LED ON).
 * Bit = 0 -> Constant-current sink disabled (LED OFF).
 */
void tlc5916_update(uint16_t led_word) {
    // Clock MSB first so that bit 15 reaches the end of U11 and bit 0 ends in U7
    for (int i = 15; i >= 0; i--) {
        gpio_put(PIN_LEDBAR_CLK, 0);
        gpio_put(PIN_LEDBAR_DATA, (led_word >> i) & 1);
        gpio_put(PIN_LEDBAR_CLK, 1);
    }
    gpio_put(PIN_LEDBAR_CLK, 0);

    // Latch data into output registers
    gpio_put(PIN_LEDBAR_LE, 1);
    gpio_put(PIN_LEDBAR_LE, 0);
}

/**
 * Set VU-meter bargraph level (0 to 10 LEDs)
 */
void tlc5916_set_vu(uint8_t level, uint16_t status_flags) {
    if (level > 10) level = 10;
    uint16_t vu_bits = (level == 0) ? 0 : ((1U << level) - 1U);
    tlc5916_update((status_flags & ~LED_VU_MASK) | (vu_bits & LED_VU_MASK));
}

// Operating modes
typedef enum {
    MODE_IDLE = 0,
    MODE_C2N_PLAY,
    MODE_C2N_RECORD,
    MODE_ZX_PLAY,
    MODE_ANALOG_DIGITIZE,
    MODE_AZIMUTH_TUNE
} tape_mode_t;

volatile tape_mode_t current_mode = MODE_IDLE;
volatile bool motor_running = false;
volatile bool playback_paused = false;

/**
 * Core 1 Entry: Real-Time Engine, Motor Control & Bus Sync
 */
void core1_entry(void) {
    gpio_init(PIN_C64_MOTOR_SENSE);
    gpio_set_dir(PIN_C64_MOTOR_SENSE, GPIO_IN);
    gpio_pull_up(PIN_C64_MOTOR_SENSE);

    while (1) {
        // Active LOW from Q2: 0 means motor energized by vintage host
        bool motor_now = (gpio_get(PIN_C64_MOTOR_SENSE) == 0);

        if (motor_now != motor_running) {
            motor_running = motor_now;
            if (motor_running) {
                playback_paused = false;
            } else {
                playback_paused = true;
            }
        }
        tight_loop_contents();
    }
}

/**
 * Core 0 Entry: System Initialization, UI, Display & Ingest Processing
 */
int main(void) {
    stdio_init_all();

    // 1. Initialize UI Buttons
    uint ui_pins[] = {PIN_BTN_PLAY_STOP, PIN_BTN_REC_DUMP, PIN_BTN_REW_PREV, PIN_BTN_FFWD_NEXT, PIN_ENC_SW};
    for (int i = 0; i < 5; i++) {
        gpio_init(ui_pins[i]);
        gpio_set_dir(ui_pins[i], GPIO_IN);
        gpio_pull_up(ui_pins[i]);
    }

    // 2. Initialize Dual TLC5916 Constant-Current Shift Register Bus
    tlc5916_init();
    // Power-on self test: illuminate all 14 LEDs briefly, then clear
    tlc5916_update(0x3FFF);
    sleep_ms(250);
    tlc5916_update(0x0000);

    // 3. Initialize ADC for Azimuth Peak Detector Level (ADC0 / GP26)
    adc_init();
    adc_gpio_init(PIN_AZIMUTH_PEAK_ADC);
    adc_select_input(0);

    // 4. Initialize I2C for 128x64 OLED Display
    i2c_init(i2c0, 400 * 1000);
    gpio_set_function(PIN_I2C_SDA, GPIO_FUNC_I2C);
    gpio_set_function(PIN_I2C_SCL, GPIO_FUNC_I2C);
    gpio_pull_up(PIN_I2C_SDA);
    gpio_pull_up(PIN_I2C_SCL);

    // 5. Initialize SPI for MicroSD Card
    spi_init(spi0, 10 * 1000 * 1000);
    gpio_set_function(PIN_SD_SCK, GPIO_FUNC_SPI);
    gpio_set_function(PIN_SD_MOSI, GPIO_FUNC_SPI);
    gpio_set_function(PIN_SD_MISO, GPIO_FUNC_SPI);
    gpio_init(PIN_SD_CS);
    gpio_set_dir(PIN_SD_CS, GPIO_OUT);
    gpio_put(PIN_SD_CS, 1);

    // 6. Launch Core 1 for real-time motor and bus handling
    multicore_launch_core1(core1_entry);

    printf("Tape Master Exerciser v1.0 initialized successfully. Ready.\n");

    uint16_t status_flags = 0;
    while (1) {
        // Read peak signal for Azimuth Tuning (12-bit ADC: 0..4095)
        uint16_t raw_adc = adc_read();
        uint8_t vu_level = (raw_adc * 11) / 4096;
        if (vu_level > 10) vu_level = 10;

        if (motor_running) status_flags |= LED_STATUS_MOTOR;
        else status_flags &= ~LED_STATUS_MOTOR;

        tlc5916_set_vu(vu_level, status_flags);

        sleep_ms(20);
    }
}
