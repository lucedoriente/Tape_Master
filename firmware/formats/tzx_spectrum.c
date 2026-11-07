/**
 * Tape Master v2 - Sinclair ZX Spectrum .TZX Format Parser Implementation
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#include "tzx_spectrum.h"
#include <string.h>

// Convert 3.5 MHz T-states to microseconds: us = (t_states * 10) / 35
#define TSTATES_TO_US(t)   (((uint32_t)(t) * 10) / 35)

bool tzx_parser_init(tzx_parser_t *parser, const uint8_t *buffer, size_t file_len) {
    if (!parser || !buffer || file_len < 10) {
        return false;
    }

    // Verify "ZXTape!\x1A"
    if (memcmp(buffer, TZX_MAGIC_STRING, TZX_MAGIC_LEN) != 0) {
        return false;
    }

    parser->data = buffer;
    parser->total_size = file_len;
    parser->cursor = 10; // Skip 8 bytes magic + 2 bytes version
    parser->state = TZX_STATE_NEXT_BLOCK;
    parser->sub_count = 0;
    return true;
}

static void setup_standard_block(tzx_parser_t *parser) {
    // ID 0x10: Standard Speed Data Block
    // Offset +1: Pause after block in ms (2 bytes LE)
    // Offset +3: Data length (2 bytes LE)
    // Offset +5: Data bytes
    if (parser->cursor + 5 > parser->total_size) {
        parser->state = TZX_STATE_EOF;
        return;
    }

    parser->pause_ms = (uint16_t)parser->data[parser->cursor + 1] |
                       ((uint16_t)parser->data[parser->cursor + 2] << 8);
    parser->data_len = (uint16_t)parser->data[parser->cursor + 3] |
                       ((uint16_t)parser->data[parser->cursor + 4] << 8);

    parser->data_offset = parser->cursor + 5;
    parser->cursor = parser->data_offset + parser->data_len;

    // Standard ROM timings
    parser->pilot_pulse_us = TSTATES_TO_US(2168); // ~619 us
    parser->sync1_us = TSTATES_TO_US(667);        // ~191 us
    parser->sync2_us = TSTATES_TO_US(735);        // ~210 us
    parser->bit0_pulse_us = TSTATES_TO_US(855);   // ~244 us
    parser->bit1_pulse_us = TSTATES_TO_US(1710);  // ~489 us

    // First byte determines if header (0x00) or data (0xFF)
    uint8_t first_byte = (parser->data_len > 0) ? parser->data[parser->data_offset] : 0xFF;
    parser->pilot_count = (first_byte < 128) ? 8063 : 3223;

    parser->bit_index = 7;
    parser->pulse_phase = 0;
    parser->sub_count = parser->pilot_count;
    parser->state = TZX_STATE_PILOT;
}

bool tzx_parser_next_half_period(tzx_parser_t *parser, uint32_t *out_us, bool *out_level_toggle) {
    if (!parser || !out_us || !out_level_toggle) return false;

    while (1) {
        switch (parser->state) {
            case TZX_STATE_NEXT_BLOCK: {
                if (parser->cursor >= parser->total_size) {
                    parser->state = TZX_STATE_EOF;
                    return false;
                }

                uint8_t block_id = parser->data[parser->cursor];
                switch (block_id) {
                    case TZX_ID_STANDARD_DATA:
                        setup_standard_block(parser);
                        break;
                    case TZX_ID_PAUSE_STOP: {
                        if (parser->cursor + 3 > parser->total_size) {
                            parser->state = TZX_STATE_EOF;
                            return false;
                        }
                        parser->pause_ms = (uint16_t)parser->data[parser->cursor + 1] |
                                           ((uint16_t)parser->data[parser->cursor + 2] << 8);
                        parser->cursor += 3;
                        parser->state = TZX_STATE_PAUSE;
                        break;
                    }
                    case TZX_ID_TEXT_DESCRIPTION: {
                        if (parser->cursor + 2 > parser->total_size) {
                            parser->state = TZX_STATE_EOF;
                            return false;
                        }
                        uint8_t txt_len = parser->data[parser->cursor + 1];
                        parser->cursor += 2 + txt_len; // Skip text metadata
                        break;
                    }
                    default:
                        // Unsupported or unknown block; skip to end
                        parser->state = TZX_STATE_EOF;
                        return false;
                }
                break;
            }

            case TZX_STATE_PILOT:
                if (parser->sub_count > 0) {
                    parser->sub_count--;
                    *out_us = parser->pilot_pulse_us;
                    *out_level_toggle = true;
                    return true;
                }
                parser->state = TZX_STATE_SYNC1;
                break;

            case TZX_STATE_SYNC1:
                *out_us = parser->sync1_us;
                *out_level_toggle = true;
                parser->state = TZX_STATE_SYNC2;
                return true;

            case TZX_STATE_SYNC2:
                *out_us = parser->sync2_us;
                *out_level_toggle = true;
                parser->current_byte = parser->data[parser->data_offset++];
                parser->bit_index = 7;
                parser->pulse_phase = 0;
                parser->state = TZX_STATE_DATA_BIT;
                return true;

            case TZX_STATE_DATA_BIT: {
                bool bit_val = (parser->current_byte >> parser->bit_index) & 0x01;
                *out_us = bit_val ? parser->bit1_pulse_us : parser->bit0_pulse_us;
                *out_level_toggle = true;

                // Each bit consists of two identical pulses
                if (parser->pulse_phase == 0) {
                    parser->pulse_phase = 1;
                } else {
                    parser->pulse_phase = 0;
                    parser->bit_index--;
                    if (parser->bit_index < 0) {
                        if (parser->data_offset < parser->cursor) {
                            parser->current_byte = parser->data[parser->data_offset++];
                            parser->bit_index = 7;
                        } else {
                            // Finished data payload of block
                            parser->state = (parser->pause_ms > 0) ? TZX_STATE_PAUSE : TZX_STATE_NEXT_BLOCK;
                        }
                    }
                }
                return true;
            }

            case TZX_STATE_PAUSE:
                if (parser->pause_ms > 0) {
                    *out_us = (uint32_t)parser->pause_ms * 1000;
                    *out_level_toggle = false; // Hold steady level
                    parser->pause_ms = 0;
                    parser->state = TZX_STATE_NEXT_BLOCK;
                    return true;
                }
                parser->state = TZX_STATE_NEXT_BLOCK;
                break;

            case TZX_STATE_EOF:
            default:
                return false;
        }
    }
}

void tzx_parser_rewind(tzx_parser_t *parser) {
    if (!parser) return;
    parser->cursor = 10;
    parser->state = TZX_STATE_NEXT_BLOCK;
    parser->sub_count = 0;
}

uint8_t tzx_parser_get_progress(const tzx_parser_t *parser) {
    if (!parser || parser->total_size == 0) return 0;
    return (uint8_t)(((uint64_t)parser->cursor * 100) / parser->total_size);
}
