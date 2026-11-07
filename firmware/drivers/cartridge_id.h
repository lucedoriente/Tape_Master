/**
 * Tape Master v2 - Smart Cartridge Auto-ID Driver
 * Reads 24C02 I2C EEPROM on Cartridge bus and detects hot-plug insertion
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#ifndef CARTRIDGE_ID_H
#define CARTRIDGE_ID_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define CART_MAGIC_BYTE0        0x54  // 'T'
#define CART_MAGIC_BYTE1        0x4D  // 'M'
#define CART_STRUCT_VERSION     0x02  // Tape Master v2.0

typedef enum {
    CART_ID_NONE               = 0,
    CART_ID_COMMODORE_C2N      = 1,
    CART_ID_ATARI_SIO          = 2,
    CART_ID_THOMSON_PC128      = 3,
    CART_ID_SINCLAIR_SPECTRUM  = 4,
    CART_ID_AMSTRAD_CPC        = 5,
    CART_ID_MSX_STANDARD       = 6,
    CART_ID_ACORN_BBC_MICRO    = 7,
    CART_ID_TANDY_COCO_DRAGON  = 8,
    CART_ID_TI99_4A            = 9,
    CART_ID_APPLE_II           = 10,
    CART_ID_ORIC_ATMOS         = 11,
    CART_ID_SHARP_MZ           = 12,
    CART_ID_RAW_HEAD_DIGITIZER = 13,
    CART_ID_DEC_TU58_EXP       = 14,  // Future minicomputer expansion
    CART_ID_UNKNOWN            = 255
} cartridge_id_t;

typedef enum {
    SIGNAL_TYPE_PULSE_TTL      = 0,  // Active-low / active-high square wave logic (C2N, Sharp)
    SIGNAL_TYPE_AUDIO_ANALOG   = 1,  // AC-coupled analog FSK / tone (Spectrum, Apple II, CoCo)
    SIGNAL_TYPE_SERIAL_ASYNC   = 2,  // Asynchronous UART stream (Atari SIO, DEC TU58)
    SIGNAL_TYPE_RAW_MAGNETIC   = 3   // Direct low-level head signal (Raw Head Digitizer)
} cartridge_signal_type_t;

typedef struct __attribute__((packed)) {
    uint8_t magic[2];                // 'T', 'M'
    uint8_t struct_ver;              // 0x02
    uint8_t id;                      // 1..13
    char    platform_name[20];       // e.g. "Commodore C2N\0"
    uint8_t signal_type;             // cartridge_signal_type_t
    uint16_t default_baud_rate;      // e.g. 1200, 2400, 5327, 38400
    uint8_t flags;                   // Bit 0: Inverted logic, Bit 1: Motor active HIGH, etc.
    uint8_t checksum;                // CRC8 or simple additive checksum
} cartridge_descriptor_t;

/**
 * Initialize Cartridge detection GPIO and I2C subsystem.
 */
void cartridge_manager_init(void);

/**
 * Check if a physical cartridge is present in slot J5.
 * @return true if J1 is inserted (/CART_DETECT_N pulled LOW to GND).
 */
bool cartridge_is_inserted(void);

/**
 * Poll for cartridge insertion/removal events.
 * @return true if the insertion state changed since last call.
 */
bool cartridge_poll_state_change(void);

/**
 * Read the descriptor from the 24C02 EEPROM over I2C.
 * If reading fails or unformatted, falls back to default profile based on fallback ID.
 * 
 * @param out_desc Pointer to destination descriptor.
 * @return true if valid signature and checksum read.
 */
bool cartridge_read_descriptor(cartridge_descriptor_t *out_desc);

/**
 * Helper to get human-readable name of cartridge ID.
 */
const char* cartridge_get_name_by_id(cartridge_id_t id);

#ifdef __cplusplus
}
#endif

#endif // CARTRIDGE_ID_H
