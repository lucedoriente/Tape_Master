/**
 * Tape Master v2 - MicroSD Low-Level SPI Block Driver
 * 
 * Hardware SPI driver for SD/SDHC/SDXC cards over SPI0.
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#ifndef SD_CARD_H
#define SD_CARD_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// SD Card Type Flags
#define SD_TYPE_UNKNOWN     0x00
#define SD_TYPE_MMC         0x01
#define SD_TYPE_V1          0x02
#define SD_TYPE_V2_SC       0x04
#define SD_TYPE_V2_HC       0x08

// Block size standard for FAT
#define SD_BLOCK_SIZE       512

/**
 * Initialize SD card SPI interface and configure hardware pins.
 * Performs CMD0, CMD8, ACMD41 power-up initialization sequence.
 * 
 * @return true if card successfully recognized and ready.
 */
bool sd_card_init(void);

/**
 * Check if SD card is present and initialized.
 */
bool sd_card_is_ready(void);

/**
 * Get detected SD card type (SD_TYPE_V2_HC, etc.).
 */
uint8_t sd_card_get_type(void);

/**
 * Read a single 512-byte block from sector address.
 * 
 * @param sector LBA sector number.
 * @param buffer Buffer to receive 512 bytes (must be at least 512 bytes).
 * @return true on success.
 */
bool sd_card_read_block(uint32_t sector, uint8_t *buffer);

/**
 * Read multiple 512-byte blocks.
 * 
 * @param sector Starting LBA sector number.
 * @param buffer Buffer to receive data.
 * @param count Number of 512-byte sectors to read.
 * @return true on success.
 */
bool sd_card_read_blocks(uint32_t sector, uint8_t *buffer, uint32_t count);

/**
 * Write a single 512-byte block to sector address.
 * 
 * @param sector LBA sector number.
 * @param buffer 512 bytes of data to write.
 * @return true on success.
 */
bool sd_card_write_block(uint32_t sector, const uint8_t *buffer);

/**
 * Write multiple 512-byte blocks.
 * 
 * @param sector Starting LBA sector number.
 * @param buffer Data to write.
 * @param count Number of 512-byte sectors to write.
 * @return true on success.
 */
bool sd_card_write_blocks(uint32_t sector, const uint8_t *buffer, uint32_t count);

#ifdef __cplusplus
}
#endif

#endif // SD_CARD_H
