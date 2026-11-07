/**
 * Tape Master v2 - Compressed Square Wave (.CSW v2) Raw Stream Format
 * 
 * Standard universal format for capturing and preserving digitized tape streams.
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#ifndef CSW_RAW_H
#define CSW_RAW_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define CSW_MAGIC_STRING        "Compressed Square Wave\x1A"
#define CSW_MAGIC_LEN           23

#define CSW_ENCODING_RLE        0x01
#define CSW_ENCODING_ZRLE       0x02

typedef struct __attribute__((packed)) {
    char     magic[CSW_MAGIC_LEN];  // "Compressed Square Wave\x1A"
    uint8_t  major_version;         // 0x02
    uint8_t  minor_version;         // 0x00
    uint32_t sample_rate;           // Typically 1000000 Hz (1 us resolution)
    uint32_t total_pulses;          // Total number of pulses in file
    uint8_t  encoding_type;         // 0x01 (RLE)
    uint8_t  flags;                 // Bit 0: Initial polarity (0 = Low, 1 = High)
    uint8_t  reserved[3];           // Padding
} csw_header_t;

typedef struct {
    const uint8_t *data;
    size_t         total_size;
    size_t         cursor;
    uint32_t       sample_rate;
    uint32_t       total_pulses;
    uint32_t       pulses_read;
    bool           current_polarity;
    bool           eof;
} csw_parser_t;

/**
 * Initialize CSW reader.
 */
bool csw_parser_init(csw_parser_t *parser, const uint8_t *buffer, size_t file_len);

/**
 * Read next pulse duration in microseconds.
 */
bool csw_parser_next_pulse(csw_parser_t *parser, uint32_t *out_us, bool *out_polarity);

/**
 * Helper to construct a CSW header for a newly digitized tape file.
 */
void csw_create_header(csw_header_t *hdr, uint32_t sample_rate, uint32_t total_pulses, bool initial_polarity);

#ifdef __cplusplus
}
#endif

#endif // CSW_RAW_H
