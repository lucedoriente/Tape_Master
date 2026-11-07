/**
 * Tape Master v2 - Commodore .TAP Format Parser & Streamer
 * 
 * Supports .TAP v0 (C64/VIC-20) and v1 (C16/Plus4 extended 24-bit pulses).
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#ifndef TAP_C64_H
#define TAP_C64_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define TAP_MAGIC_STRING        "C64-TAPE-RAW"
#define TAP_MAGIC_LEN           12

typedef struct __attribute__((packed)) {
    char     magic[TAP_MAGIC_LEN];  // "C64-TAPE-RAW"
    uint8_t  version;               // 0x00 or 0x01
    uint8_t  platform;              // 0 = C64, 1 = VIC-20, 2 = C16/Plus4
    uint8_t  video_standard;        // 0 = PAL, 1 = NTSC
    uint8_t  reserved;
    uint32_t data_size;             // Little-endian length of pulse data
} tap_header_t;

typedef struct {
    const uint8_t *data;            // Pointer to loaded TAP data buffer
    size_t         total_size;      // Total size of TAP data payload
    size_t         cursor;          // Current reading byte offset
    uint8_t        version;         // 0 or 1
    bool           is_pal;          // PAL (1.015 us/cycle) or NTSC (0.977 us/cycle)
    bool           eof;             // Reached end of file
} tap_parser_t;

/**
 * Initialize TAP parser with data in memory.
 * Validates header, extracts version and platform.
 * 
 * @param parser Pointer to parser structure.
 * @param buffer Pointer to full file content.
 * @param file_len Size of buffer in bytes.
 * @return true if valid .TAP file header found.
 */
bool tap_parser_init(tap_parser_t *parser, const uint8_t *buffer, size_t file_len);

/**
 * Extract the next pulse interval in microseconds.
 * Handles single-byte v0 pulses and 3-byte escaped v1 pulses.
 * 
 * @param parser Pointer to active parser.
 * @param out_us Pointer to receive interval duration in microseconds.
 * @return true if pulse successfully decoded, false if EOF.
 */
bool tap_parser_next_pulse(tap_parser_t *parser, uint32_t *out_us);

/**
 * Rewind parser back to start of pulse data.
 */
void tap_parser_rewind(tap_parser_t *parser);

/**
 * Get progress percentage (0..100).
 */
uint8_t tap_parser_get_progress(const tap_parser_t *parser);

#ifdef __cplusplus
}
#endif

#endif // TAP_C64_H
