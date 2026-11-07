/**
 * Tape Master v2 - MicroSD Low-Level SPI Block Driver Implementation
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#include "sd_card.h"
#include "../config/hardware_pins.h"
#include "pico/stdlib.h"
#include "hardware/spi.h"

// SD SPI Commands
#define CMD0    0   // GO_IDLE_STATE
#define CMD1    1   // SEND_OP_COND (MMC)
#define CMD8    8   // SEND_IF_COND
#define CMD9    9   // SEND_CSD
#define CMD10   10  // SEND_CID
#define CMD12   12  // STOP_TRANSMISSION
#define CMD16   16  // SET_BLOCKLEN
#define CMD17   17  // READ_SINGLE_BLOCK
#define CMD18   18  // READ_MULTIPLE_BLOCK
#define CMD24   24  // WRITE_BLOCK
#define CMD25   25  // WRITE_MULTIPLE_BLOCK
#define CMD55   55  // APP_CMD
#define CMD58   58  // READ_OCR
#define ACMD41  41  // SD_SEND_OP_COND

// Tokens
#define TOKEN_START_BLOCK   0xFE
#define TOKEN_STOP_TRAN     0xFD
#define TOKEN_START_MULTI   0xFC

// SPI instance
#define SD_SPI_INST         spi0
#define SD_SPI_SLOW_HZ      300000      // 300 kHz for initialization
#define SD_SPI_FAST_HZ      12500000    // 12.5 MHz for bulk data transfer

static bool    s_initialized = false;
static uint8_t s_card_type   = SD_TYPE_UNKNOWN;

static inline void sd_select(void) {
    gpio_put(PIN_SD_CS, 0);
}

static inline void sd_deselect(void) {
    gpio_put(PIN_SD_CS, 1);
    uint8_t dummy = 0xFF;
    spi_write_blocking(SD_SPI_INST, &dummy, 1); // Send 8 trailing clock cycles
}

static inline uint8_t sd_spi_transfer_byte(uint8_t byte) {
    uint8_t rx = 0xFF;
    spi_write_read_blocking(SD_SPI_INST, &byte, &rx, 1);
    return rx;
}

static inline void sd_spi_write_bytes(const uint8_t *src, size_t len) {
    spi_write_blocking(SD_SPI_INST, src, len);
}

static inline void sd_spi_read_bytes(uint8_t *dst, size_t len) {
    spi_read_blocking(SD_SPI_INST, 0xFF, dst, len);
}

static uint8_t sd_wait_ready(uint32_t timeout_ms) {
    absolute_time_t deadline = make_timeout_time_ms(timeout_ms);
    uint8_t res;
    do {
        res = sd_spi_transfer_byte(0xFF);
        if (res == 0xFF) return 0xFF;
    } while (absolute_time_diff_us(get_absolute_time(), deadline) > 0);
    return 0; // Timeout
}

static uint8_t sd_send_cmd(uint8_t cmd, uint32_t arg) {
    uint8_t crc = 0x01; // Default dummy CRC for SPI mode
    if (cmd == CMD0) crc = 0x95; // Valid CRC for CMD0(0)
    if (cmd == CMD8) crc = 0x87; // Valid CRC for CMD8(0x1AA)

    // Wait for card to be ready before transmitting
    if (cmd != CMD0) {
        sd_deselect();
        sd_select();
        if (sd_wait_ready(300) != 0xFF) return 0xFF;
    }

    uint8_t pkt[6];
    pkt[0] = 0x40 | (cmd & 0x3F);
    pkt[1] = (uint8_t)(arg >> 24);
    pkt[2] = (uint8_t)(arg >> 16);
    pkt[3] = (uint8_t)(arg >> 8);
    pkt[4] = (uint8_t)(arg);
    pkt[5] = crc;

    sd_spi_write_bytes(pkt, 6);

    // Read R1 response (up to 10 attempts)
    uint8_t r1 = 0xFF;
    for (int i = 0; i < 10; i++) {
        r1 = sd_spi_transfer_byte(0xFF);
        if ((r1 & 0x80) == 0) break;
    }
    return r1;
}

static uint8_t sd_send_app_cmd(uint8_t cmd, uint32_t arg) {
    sd_send_cmd(CMD55, 0);
    return sd_send_cmd(cmd, arg);
}

bool sd_card_init(void) {
    s_initialized = false;
    s_card_type = SD_TYPE_UNKNOWN;

    // Configure GPIO pins
    gpio_init(PIN_SD_CS);
    gpio_set_dir(PIN_SD_CS, GPIO_OUT);
    gpio_put(PIN_SD_CS, 1); // Deselect

    gpio_set_function(PIN_SD_SCK,  GPIO_FUNC_SPI);
    gpio_set_function(PIN_SD_MOSI, GPIO_FUNC_SPI);
    gpio_set_function(PIN_SD_MISO, GPIO_FUNC_SPI);

    // Start with slow clock (300 kHz)
    spi_init(SD_SPI_INST, SD_SPI_SLOW_HZ);
    spi_set_format(SD_SPI_INST, 8, SPI_CPOL_0, SPI_CPHA_0, SPI_MSB_FIRST);

    // Send at least 74 dummy clock pulses with CS high
    sd_deselect();
    for (int i = 0; i < 10; i++) {
        sd_spi_transfer_byte(0xFF);
    }

    // Step 1: Send CMD0 to enter SPI mode
    sd_select();
    uint8_t r1 = 0xFF;
    for (int i = 0; i < 10; i++) {
        r1 = sd_send_cmd(CMD0, 0);
        if (r1 == 0x01) break; // In Idle State
        sleep_ms(2);
    }

    if (r1 != 0x01) {
        sd_deselect();
        return false; // No SD card detected
    }

    // Step 2: Send CMD8 (check voltage and v2 support)
    r1 = sd_send_cmd(CMD8, 0x000001AA);
    if (r1 == 0x01) {
        // SD v2.0+ card
        uint8_t ocr[4];
        sd_spi_read_bytes(ocr, 4);

        if (ocr[2] == 0x01 && ocr[3] == 0xAA) {
            // Card supports 2.7-3.6V. Send ACMD41 with HCS (High Capacity Support) bit
            absolute_time_t timeout = make_timeout_time_ms(1500);
            while (1) {
                r1 = sd_send_app_cmd(ACMD41, 0x40000000);
                if (r1 == 0x00) break; // Card ready
                if (absolute_time_diff_us(get_absolute_time(), timeout) <= 0) {
                    sd_deselect();
                    return false;
                }
                sleep_ms(10);
            }

            // Read OCR via CMD58 to check CCS (Card Capacity Status)
            if (sd_send_cmd(CMD58, 0) == 0x00) {
                sd_spi_read_bytes(ocr, 4);
                if (ocr[0] & 0x40) {
                    s_card_type = SD_TYPE_V2_HC; // Block addressing (SDHC/SDXC)
                } else {
                    s_card_type = SD_TYPE_V2_SC; // Byte addressing
                }
            }
        }
    } else {
        // SD v1 or MMC card
        r1 = sd_send_app_cmd(ACMD41, 0);
        uint8_t cmd = (r1 <= 0x01) ? ACMD41 : CMD1;
        s_card_type = (r1 <= 0x01) ? SD_TYPE_V1 : SD_TYPE_MMC;

        absolute_time_t timeout = make_timeout_time_ms(1500);
        while (1) {
            r1 = (cmd == ACMD41) ? sd_send_app_cmd(ACMD41, 0) : sd_send_cmd(CMD1, 0);
            if (r1 == 0x00) break;
            if (absolute_time_diff_us(get_absolute_time(), timeout) <= 0) {
                sd_deselect();
                return false;
            }
            sleep_ms(10);
        }
    }

    // Force block length to 512 bytes for Standard Capacity cards
    if (s_card_type != SD_TYPE_V2_HC) {
        sd_send_cmd(CMD16, SD_BLOCK_SIZE);
    }

    sd_deselect();

    // Switch SPI clock to full speed
    spi_set_baudrate(SD_SPI_INST, SD_SPI_FAST_HZ);
    s_initialized = true;
    return true;
}

bool sd_card_is_ready(void) {
    return s_initialized;
}

uint8_t sd_card_get_type(void) {
    return s_card_type;
}

bool sd_card_read_block(uint32_t sector, uint8_t *buffer) {
    if (!s_initialized || !buffer) return false;

    // Convert to byte address if standard capacity
    uint32_t addr = (s_card_type == SD_TYPE_V2_HC) ? sector : (sector * SD_BLOCK_SIZE);

    sd_select();
    if (sd_send_cmd(CMD17, addr) != 0x00) {
        sd_deselect();
        return false;
    }

    // Wait for data start token (0xFE)
    absolute_time_t timeout = make_timeout_time_ms(300);
    uint8_t token;
    do {
        token = sd_spi_transfer_byte(0xFF);
        if (token == TOKEN_START_BLOCK) break;
    } while (absolute_time_diff_us(get_absolute_time(), timeout) > 0);

    if (token != TOKEN_START_BLOCK) {
        sd_deselect();
        return false;
    }

    // Read 512 bytes
    sd_spi_read_bytes(buffer, SD_BLOCK_SIZE);

    // Read and discard 2 CRC bytes
    sd_spi_transfer_byte(0xFF);
    sd_spi_transfer_byte(0xFF);

    sd_deselect();
    return true;
}

bool sd_card_read_blocks(uint32_t sector, uint8_t *buffer, uint32_t count) {
    for (uint32_t i = 0; i < count; i++) {
        if (!sd_card_read_block(sector + i, buffer + (i * SD_BLOCK_SIZE))) {
            return false;
        }
    }
    return true;
}

bool sd_card_write_block(uint32_t sector, const uint8_t *buffer) {
    if (!s_initialized || !buffer) return false;

    uint32_t addr = (s_card_type == SD_TYPE_V2_HC) ? sector : (sector * SD_BLOCK_SIZE);

    sd_select();
    if (sd_send_cmd(CMD24, addr) != 0x00) {
        sd_deselect();
        return false;
    }

    // Send single dummy byte followed by start block token
    sd_spi_transfer_byte(0xFF);
    sd_spi_transfer_byte(TOKEN_START_BLOCK);

    // Write 512 bytes data payload
    sd_spi_write_bytes(buffer, SD_BLOCK_SIZE);

    // Send dummy 16-bit CRC
    sd_spi_transfer_byte(0xFF);
    sd_spi_transfer_byte(0xFF);

    // Read data response token: 0bxxx00101 means data accepted
    uint8_t resp = sd_spi_transfer_byte(0xFF);
    if ((resp & 0x1F) != 0x05) {
        sd_deselect();
        return false;
    }

    // Wait while card programs the flash (busy line low)
    if (sd_wait_ready(500) != 0xFF) {
        sd_deselect();
        return false;
    }

    sd_deselect();
    return true;
}

bool sd_card_write_blocks(uint32_t sector, const uint8_t *buffer, uint32_t count) {
    for (uint32_t i = 0; i < count; i++) {
        if (!sd_card_write_block(sector + i, buffer + (i * SD_BLOCK_SIZE))) {
            return false;
        }
    }
    return true;
}
