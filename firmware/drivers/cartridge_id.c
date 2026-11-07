/**
 * Tape Master v2 - Smart Cartridge Auto-ID Implementation
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#include "cartridge_id.h"
#include "../config/hardware_pins.h"
#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include <string.h>

static bool s_last_inserted_state = false;

static const char* s_cartridge_names[] = {
    [CART_ID_NONE]               = "Nessuna Cartuccia",
    [CART_ID_COMMODORE_C2N]      = "01: Commodore C2N",
    [CART_ID_ATARI_SIO]          = "02: Atari SIO",
    [CART_ID_THOMSON_PC128]      = "03: Thomson / PC128",
    [CART_ID_SINCLAIR_SPECTRUM]  = "04: Sinclair ZX Tape",
    [CART_ID_AMSTRAD_CPC]        = "05: Amstrad CPC",
    [CART_ID_MSX_STANDARD]       = "06: MSX Standard",
    [CART_ID_ACORN_BBC_MICRO]    = "07: Acorn BBC Micro",
    [CART_ID_TANDY_COCO_DRAGON]  = "08: Tandy CoCo/Dragon",
    [CART_ID_TI99_4A]            = "09: TI-99/4A",
    [CART_ID_APPLE_II]           = "10: Apple II Series",
    [CART_ID_ORIC_ATMOS]         = "11: Oric 1 / Atmos",
    [CART_ID_SHARP_MZ]           = "12: Sharp MZ Series",
    [CART_ID_RAW_HEAD_DIGITIZER] = "13: Raw Head Digitizer",
    [CART_ID_DEC_TU58_EXP]       = "14: DEC TU58 Emul."
};

void cartridge_manager_init(void) {
    // Configure /CART_DETECT_N pin with internal pull-up
    gpio_init(PIN_CART_DETECT_N);
    gpio_set_dir(PIN_CART_DETECT_N, GPIO_IN);
    gpio_pull_up(PIN_CART_DETECT_N);

    // Configure /CART_IRQ_N pin with internal pull-up
    gpio_init(PIN_CART_IRQ_N);
    gpio_set_dir(PIN_CART_IRQ_N, GPIO_IN);
    gpio_pull_up(PIN_CART_IRQ_N);

    s_last_inserted_state = cartridge_is_inserted();
}

bool cartridge_is_inserted(void) {
    // Pin 26 of J1 is hardwired to GND on every cartridge.
    // Active LOW: 0 = Inserted, 1 = Empty Slot
    return (gpio_get(PIN_CART_DETECT_N) == 0);
}

bool cartridge_poll_state_change(void) {
    bool current = cartridge_is_inserted();
    if (current != s_last_inserted_state) {
        s_last_inserted_state = current;
        return true;
    }
    return false;
}

static uint8_t calc_checksum(const uint8_t *data, size_t len) {
    uint8_t sum = 0;
    for (size_t i = 0; i < len; i++) {
        sum += data[i];
    }
    return sum;
}

bool cartridge_read_descriptor(cartridge_descriptor_t *out_desc) {
    if (!out_desc) return false;
    memset(out_desc, 0, sizeof(cartridge_descriptor_t));

    if (!cartridge_is_inserted()) {
        out_desc->id = CART_ID_NONE;
        strncpy(out_desc->platform_name, "Nessuna Cartuccia", sizeof(out_desc->platform_name) - 1);
        return false;
    }

    // Try reading 24C02 EEPROM at address 0x50 starting at word address 0x00
    uint8_t mem_addr = 0x00;
    int ret = i2c_write_blocking(I2C_PORT, CART_EEPROM_I2C_ADDR, &mem_addr, 1, true);
    if (ret < 0) {
        // I2C communication failed or no EEPROM response
        out_desc->id = CART_ID_UNKNOWN;
        strncpy(out_desc->platform_name, "Cartuccia Generica", sizeof(out_desc->platform_name) - 1);
        return false;
    }

    ret = i2c_read_blocking(I2C_PORT, CART_EEPROM_I2C_ADDR, (uint8_t*)out_desc, sizeof(cartridge_descriptor_t), false);
    if (ret != sizeof(cartridge_descriptor_t)) {
        out_desc->id = CART_ID_UNKNOWN;
        strncpy(out_desc->platform_name, "Errore Lettura EEPROM", sizeof(out_desc->platform_name) - 1);
        return false;
    }

    // Validate Magic bytes
    if (out_desc->magic[0] != CART_MAGIC_BYTE0 || out_desc->magic[1] != CART_MAGIC_BYTE1) {
        // Unprogrammed EEPROM; fallback to unknown
        out_desc->id = CART_ID_UNKNOWN;
        strncpy(out_desc->platform_name, "EEPROM non programmata", sizeof(out_desc->platform_name) - 1);
        return false;
    }

    // Validate Checksum (all bytes except checksum itself)
    uint8_t chk = calc_checksum((const uint8_t*)out_desc, sizeof(cartridge_descriptor_t) - 1);
    if (chk != out_desc->checksum) {
        out_desc->id = CART_ID_UNKNOWN;
        strncpy(out_desc->platform_name, "CRC EEPROM Errato", sizeof(out_desc->platform_name) - 1);
        return false;
    }

    return true;
}

const char* cartridge_get_name_by_id(cartridge_id_t id) {
    if (id < sizeof(s_cartridge_names) / sizeof(s_cartridge_names[0])) {
        return s_cartridge_names[id];
    }
    return "Cartuccia Sconosciuta";
}
