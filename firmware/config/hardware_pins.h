/**
 * Tape / Cassette Master Exerciser & Signal Digitizer v2.0
 * Hardware Pin Definitions for Raspberry Pi Pico (RP2040)
 * 
 * Target Hardware: Tape Master v2 Mainboard & UI Panel (KiCad 9.0)
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#ifndef HARDWARE_PINS_H
#define HARDWARE_PINS_H

#include "pico/types.h"
#include "hardware/gpio.h"

#ifdef __cplusplus
extern "C" {
#endif

// ==============================================================================
// 1. CARTRIDGE SLOT BUS (40-PIN CONNECTOR J5) INTERFACE
// ==============================================================================
#define PIN_CART_IRQ_N          0   // GP0  - Cartridge Hardware Interrupt (Active LOW)
#define PIN_CART_DETECT_N       1   // GP1  - Cartridge Insertion Detect (GND on J1.26, Active LOW)
#define PIN_AUX_GPIO2          11   // GP11 - Auxiliary expansion line to cartridge bus
#define PIN_MOTOR_SENSE        12   // GP12 - Motor sense input from host computer/drive
#define PIN_MOTOR_CTRL         13   // GP13 - Motor drive control output (FET / Relay)
#define PIN_TAPE_SENSE         14   // GP14 - Sense key / play switch feedback line
#define PIN_TAPE_EMU_OUT       21   // GP21 - Virtual Tape pulse output to computer via PIO
#define PIN_TAPE_REC_IN        22   // GP22 - Capture input from computer write line via PIO

// ==============================================================================
// 2. ANALOG FRONT-END & COMPARATOR SIGNALS
// ==============================================================================
#define PIN_TAPE_DIGITIZED     15   // GP15 - Output of LM393 precision zero-crossing comparator
#define PIN_AZIMUTH_PEAK_ADC   26   // GP26 / ADC0 - Analog peak detector voltage for Azimuth VU-meter
#define PIN_TAPE_RAW_ADC       27   // GP27 / ADC1 - Direct raw analog signal from head pre-amp
#define PIN_AUX_GPIO_ADC       28   // GP28 / ADC2 - Auxiliary analog input

#define ADC_CHANNEL_AZIMUTH     0
#define ADC_CHANNEL_TAPE_RAW    1
#define ADC_CHANNEL_AUX         2

// ==============================================================================
// 3. I2C BUS (OLED DISPLAY 128x64 + CARTRIDGE AUTO-ID 24C02 EEPROM)
// ==============================================================================
#define I2C_PORT                i2c0
#define PIN_I2C_SDA             4   // GP4  - I2C0 Data (with 4.7k pull-up to +3.3V)
#define PIN_I2C_SCL             5   // GP5  - I2C0 Clock (with 4.7k pull-up to +3.3V)
#define I2C_BAUDRATE_HZ        400000 // 400 kHz Fast-Mode I2C

#define OLED_I2C_ADDR           0x3C  // Default SSD1306 / SH1106 7-bit I2C address
#define CART_EEPROM_I2C_ADDR    0x50  // 24C02 Smart Cartridge Auto-ID EEPROM

// ==============================================================================
// 4. FRONT PANEL UI CONTROLS (ROTARY ENCODER & TACTILE BUTTONS)
// ==============================================================================
#define PIN_ENC_A               2   // GP2  - Rotary Encoder Channel A (Active LOW)
#define PIN_ENC_B               3   // GP3  - Rotary Encoder Channel B (Active LOW)
#define PIN_ENC_SW              6   // GP6  - Rotary Encoder Push Switch (Active LOW)

#define PIN_BTN_PLAY            7   // GP7  - Tactile Button: PLAY / START (Active LOW)
#define PIN_BTN_REC             8   // GP8  - Tactile Button: REC / DUMP (Active LOW)
#define PIN_BTN_PREV            9   // GP9  - Tactile Button: REW / PREV (Active LOW)
#define PIN_BTN_NEXT           10   // GP10 - Tactile Button: FFWD / NEXT (Active LOW)

// ==============================================================================
// 5. MICROSD CARD SPI INTERFACE (SPI0)
// ==============================================================================
#define SPI_SD_PORT             spi0
#define PIN_SD_MISO            16   // GP16 - SPI0 RX (Data from MicroSD)
#define PIN_SD_CS              17   // GP17 - SPI0 CS (Chip Select, Active LOW)
#define PIN_SD_SCK             18   // GP18 - SPI0 SCK (Shared with LED Bar Shift Clock)
#define PIN_SD_MOSI            19   // GP19 - SPI0 TX (Shared with LED Bar Serial Data)

// ==============================================================================
// 6. UI PANEL LED DRIVERS (DUAL CASCADED TLC5916 SHIFT REGISTERS - 16 BITS)
// ==============================================================================
// Note: Shift Clock and Data lines are shared with SPI0 (GP18 SCK, GP19 MOSI)
#define PIN_LEDBAR_CLK         PIN_SD_SCK   // GP18 - TLC5916 Clock (Shift register)
#define PIN_LEDBAR_DATA        PIN_SD_MOSI  // GP19 - TLC5916 Serial Data In (SDI)
#define PIN_LEDBAR_LE          20           // GP20 - TLC5916 Latch Enable (Active HIGH strobe)

// Bitfield definitions for the 16 cascaded LED channels:
// U1 (Bits 0..7): Azimuth / VU-Meter Segments 1 to 8 (Green LEDs D10 to D17)
#define LED_AZIMUTH_SEG1_BIT    (1u << 0)   // D10 (Green)
#define LED_AZIMUTH_SEG2_BIT    (1u << 1)   // D11 (Green)
#define LED_AZIMUTH_SEG3_BIT    (1u << 2)   // D12 (Green)
#define LED_AZIMUTH_SEG4_BIT    (1u << 3)   // D13 (Green)
#define LED_AZIMUTH_SEG5_BIT    (1u << 4)   // D14 (Green)
#define LED_AZIMUTH_SEG6_BIT    (1u << 5)   // D15 (Green)
#define LED_AZIMUTH_SEG7_BIT    (1u << 6)   // D16 (Green)
#define LED_AZIMUTH_SEG8_BIT    (1u << 7)   // D17 (Green)

// U2 (Bits 8..15): Azimuth Segments 9..10 + Universal Individual Status LEDs
#define LED_AZIMUTH_SEG9_BIT    (1u << 8)   // D18 (Yellow - Near Peak)
#define LED_AZIMUTH_SEG10_BIT   (1u << 9)   // D19 (Red - Peak / Clip)
#define LED_STATUS_PLAY_BIT     (1u << 10)  // D2  (Green) - Playback / Emulation active
#define LED_STATUS_REC_BIT      (1u << 11)  // D3  (Red)   - Record / Signal Dump active
#define LED_STATUS_MOTOR_BIT    (1u << 12)  // D4  (Yellow)- Motor line enabled by host
#define LED_STATUS_SIGNAL_BIT   (1u << 13)  // D5  (Blue)  - FSK Carrier / Clock detected
#define LED_STATUS_PWR_BIT      (1u << 14)  // D6  (Green) - System Power OK
#define LED_UNUSED_BIT          (1u << 15)  // Unused channel

#ifdef __cplusplus
}
#endif

#endif // HARDWARE_PINS_H
