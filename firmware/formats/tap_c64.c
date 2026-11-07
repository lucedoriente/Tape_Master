/**
 * Tape Master v2 - Commodore .TAP Format Parser Implementation
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#include "tap_c64.h"
#include <string.h>

// PAL clock: 985248 Hz -> ~1.01497 us per clock cycle
// In standard TAP files, 1 TAP tick = 8 C64 clock cycles (~8.12 us)
#define TAP_PAL_CYCLE_US_NUM    812   // 8.1197 us * 100
#define TAP_PAL_CYCLE_US_DEN    100

bool tap_parser_init(tap_parser_t *parser, const uint8_t *buffer, size_t file_len) {
    if (!parser || !buffer || file_len < sizeof(tap_header_t)) {
        return false;
    }

    const tap_header_t *hdr = (const tap_header_t*)buffer;

    // Check magic signature "C64-TAPE-RAW"
    if (memcmp(hdr->magic, TAP_MAGIC_STRING, TAP_MAGIC_LEN) != 0) {
        return false;
    }

    if (hdr->version > 1) {
        return false; // Unsupported TAP version
    }

    parser->version = hdr->version;
    parser->is_pal = (hdr->video_standard == 0);
    parser->data = buffer + sizeof(tap_header_t);
    parser->total_size = hdr->data_size;

    // Verify buffer contains full claimed payload
    if (file_len < sizeof(tap_header_t) + parser->total_size) {
        parser->total_size = file_len - sizeof(tap_header_t);
    }

    parser->cursor = 0;
    parser->eof = (parser->total_size == 0);
    return true;
}

bool tap_parser_next_pulse(tap_parser_t *parser, uint32_t *out_us) {
    if (!parser || !out_us || parser->eof) {
        return false;
    }

    if (parser->cursor >= parser->total_size) {
        parser->eof = true;
        return false;
    }

    uint8_t byte_val = parser->data[parser->cursor++];

    if (byte_val != 0) {
        // Standard pulse: byte_val * 8 clock cycles
        // Convert to microseconds
        uint32_t ticks = (uint32_t)byte_val * 8;
        // In PAL, 1 tick is ~1.015 us
        *out_us = (ticks * TAP_PAL_CYCLE_US_NUM) / (TAP_PAL_CYCLE_US_DEN * 8);
        if (*out_us == 0) *out_us = 1;
        return true;
    }

    // Extended pulse (version 1): byte 0x00 is followed by 3 little-endian bytes
    // representing full clock cycles (24-bit integer)
    if (parser->version == 1) {
        if (parser->cursor + 3 > parser->total_size) {
            parser->eof = true;
            return false;
        }

        uint32_t cycles = (uint32_t)parser->data[parser->cursor] |
                          ((uint32_t)parser->data[parser->cursor + 1] << 8) |
                          ((uint32_t)parser->data[parser->cursor + 2] << 16);
        parser->cursor += 3;

        // Convert cycles directly to microseconds (~1 us per cycle)
        *out_us = (cycles * 1000) / 985;
        if (*out_us == 0) *out_us = 1;
        return true;
    }

    // In version 0, byte 0x00 is invalid or represents overflow (~2048 us)
    *out_us = 2048;
    return true;
}

void tap_parser_rewind(tap_parser_t *parser) {
    if (!parser) return;
    parser->cursor = 0;
    parser->eof = (parser->total_size == 0);
}

uint8_t tap_parser_get_progress(const tap_parser_t *parser) {
    if (!parser || parser->total_size == 0) return 0;
    return (uint8_t)(((uint64_t)parser->cursor * 100) / parser->total_size);
}
