/**
 * Tape Master v2 - Sinclair ZX Spectrum .TZX Format Parser & Streamer
 * 
 * Supports TZX v1.20 specifications (Standard, Turbo, Pure Tone, Pulse Sequence, Pause).
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#ifndef TZX_SPECTRUM_H
#define TZX_SPECTRUM_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define TZX_MAGIC_STRING        "ZXTape!\x1A"
#define TZX_MAGIC_LEN           8

// TZX Block IDs
#define TZX_ID_STANDARD_DATA    0x10
#define TZX_ID_TURBO_DATA       0x11
#define TZX_ID_PURE_TONE        0x12
#define TZX_ID_PULSE_SEQ        0x13
#define TZX_ID_PURE_DATA        0x14
#define TZX_ID_DIRECT_RECORDING 0x15
#define TZX_ID_PAUSE_STOP       0x20
#define TZX_ID_GROUP_START      0x21
#define TZX_ID_GROUP_END        0x22
#define TZX_ID_TEXT_DESCRIPTION 0x30
#define TZX_ID_ARCHIVE_INFO     0x32

// State machine for block expansion into half-periods
typedef enum {
    TZX_STATE_NEXT_BLOCK,
    TZX_STATE_PILOT,
    TZX_STATE_SYNC1,
    TZX_STATE_SYNC2,
    TZX_STATE_DATA_BIT,
    TZX_STATE_PAUSE,
    TZX_STATE_PURE_TONE,
    TZX_STATE_PULSE_SEQ,
    TZX_STATE_EOF
} tzx_sub_state_t;

typedef struct {
    const uint8_t  *data;
    size_t          total_size;
    size_t          cursor;
    tzx_sub_state_t state;

    // Active block parameters
    uint16_t        pilot_pulse_us;
    uint16_t        pilot_count;
    uint16_t        sync1_us;
    uint16_t        sync2_us;
    uint16_t        bit0_pulse_us;
    uint16_t        bit1_pulse_us;
    uint16_t        pause_ms;

    // Data parsing state
    size_t          data_offset;
    size_t          data_len;
    uint8_t         current_byte;
    int8_t          bit_index;      // 7 down to 0
    uint8_t         pulse_phase;    // 0 or 1 (each bit has 2 half-periods)

    // Tone / Sequence state
    uint16_t        sub_count;
} tzx_parser_t;

/**
 * Initialize TZX parser with buffer in memory.
 */
bool tzx_parser_init(tzx_parser_t *parser, const uint8_t *buffer, size_t file_len);

/**
 * Extract next audio half-period duration in microseconds.
 * @param parser Pointer to parser.
 * @param out_us Duration of current half-period in us.
 * @param out_level_toggle true if pin should toggle, false if silence/pause.
 * @return true if tick generated, false if EOF or tape stopped.
 */
bool tzx_parser_next_half_period(tzx_parser_t *parser, uint32_t *out_us, bool *out_level_toggle);

/**
 * Rewind TZX parser to first block.
 */
void tzx_parser_rewind(tzx_parser_t *parser);

/**
 * Get progress percentage (0..100).
 */
uint8_t tzx_parser_get_progress(const tzx_parser_t *parser);

#ifdef __cplusplus
}
#endif

#endif // TZX_SPECTRUM_H
