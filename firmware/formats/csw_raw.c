/**
 * Tape Master v2 - Compressed Square Wave (.CSW v2) Implementation
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#include "csw_raw.h"
#include <string.h>

bool csw_parser_init(csw_parser_t *parser, const uint8_t *buffer, size_t file_len) {
    if (!parser || !buffer || file_len < sizeof(csw_header_t)) {
        return false;
    }

    const csw_header_t *hdr = (const csw_header_t*)buffer;
    if (memcmp(hdr->magic, CSW_MAGIC_STRING, CSW_MAGIC_LEN) != 0) {
        return false;
    }

    if (hdr->major_version != 2 || hdr->encoding_type != CSW_ENCODING_RLE) {
        return false; // Unsupported version/compression
    }

    parser->data = buffer + sizeof(csw_header_t);
    parser->total_size = file_len - sizeof(csw_header_t);
    parser->cursor = 0;
    parser->sample_rate = hdr->sample_rate;
    parser->total_pulses = hdr->total_pulses;
    parser->pulses_read = 0;
    parser->current_polarity = (hdr->flags & 0x01) ? true : false;
    parser->eof = (parser->total_size == 0);
    return true;
}

bool csw_parser_next_pulse(csw_parser_t *parser, uint32_t *out_us, bool *out_polarity) {
    if (!parser || !out_us || !out_polarity || parser->eof) {
        return false;
    }

    if (parser->cursor >= parser->total_size) {
        parser->eof = true;
        return false;
    }

    uint8_t byte_val = parser->data[parser->cursor++];
    uint32_t ticks = 0;

    if (byte_val != 0) {
        ticks = byte_val;
    } else {
        // Extended pulse: 0x00 followed by 4 bytes LE
        if (parser->cursor + 4 > parser->total_size) {
            parser->eof = true;
            return false;
        }
        ticks = (uint32_t)parser->data[parser->cursor] |
                ((uint32_t)parser->data[parser->cursor + 1] << 8) |
                ((uint32_t)parser->data[parser->cursor + 2] << 16) |
                ((uint32_t)parser->data[parser->cursor + 3] << 24);
        parser->cursor += 4;
    }

    // Convert ticks to microseconds based on sample rate
    // If sample_rate is 1000000 Hz, 1 tick = 1 us
    if (parser->sample_rate == 1000000) {
        *out_us = ticks;
    } else if (parser->sample_rate > 0) {
        *out_us = (uint32_t)(((uint64_t)ticks * 1000000ULL) / parser->sample_rate);
    } else {
        *out_us = ticks;
    }

    if (*out_us == 0) *out_us = 1;

    *out_polarity = parser->current_polarity;
    parser->current_polarity = !parser->current_polarity; // Invert on next pulse
    parser->pulses_read++;
    return true;
}

void csw_create_header(csw_header_t *hdr, uint32_t sample_rate, uint32_t total_pulses, bool initial_polarity) {
    if (!hdr) return;
    memset(hdr, 0, sizeof(csw_header_t));
    memcpy(hdr->magic, CSW_MAGIC_STRING, CSW_MAGIC_LEN);
    hdr->major_version = 0x02;
    hdr->minor_version = 0x00;
    hdr->sample_rate = sample_rate;
    hdr->total_pulses = total_pulses;
    hdr->encoding_type = CSW_ENCODING_RLE;
    hdr->flags = initial_polarity ? 0x01 : 0x00;
}
