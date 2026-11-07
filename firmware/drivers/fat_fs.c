/**
 * Tape Master v2 - Embedded FAT16/FAT32 Filesystem Layer Implementation
 * 
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#include "fat_fs.h"
#include "sd_card.h"
#include <string.h>
#include <ctype.h>

#define ATTR_READ_ONLY      0x01
#define ATTR_HIDDEN         0x02
#define ATTR_SYSTEM         0x04
#define ATTR_VOLUME_ID      0x08
#define ATTR_DIRECTORY      0x10
#define ATTR_ARCHIVE        0x20
#define ATTR_LONG_NAME      0x0F

#define FAT32_BAD_CLUSTER   0x0FFFFFF7
#define FAT32_EOC           0x0FFFFFF8
#define FAT16_EOC           0xFFF8

static bool            s_mounted = false;
static fat_vol_type_t  s_vol_type;
static uint32_t        s_lba_start;
static uint16_t        s_bytes_per_sector;
static uint8_t         s_sectors_per_cluster;
static uint32_t        s_fat_start_sector;
static uint32_t        s_sectors_per_fat;
static uint32_t        s_root_dir_sector;
static uint32_t        s_root_dir_entries;
static uint32_t        s_data_start_sector;
static uint32_t        s_root_cluster;

// Sector scratchpad buffer (512 bytes)
static uint8_t         s_sector_buf[SD_BLOCK_SIZE];

static uint16_t read_le16(const uint8_t *p) {
    return (uint16_t)p[0] | ((uint16_t)p[1] << 8);
}

static uint32_t read_le32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static void write_le32(uint8_t *p, uint32_t val) {
    p[0] = (uint8_t)(val);
    p[1] = (uint8_t)(val >> 8);
    p[2] = (uint8_t)(val >> 16);
    p[3] = (uint8_t)(val >> 24);
}

static uint32_t cluster_to_sector(uint32_t cluster) {
    return s_data_start_sector + ((cluster - 2) * s_sectors_per_cluster);
}

static uint32_t get_next_cluster(uint32_t cluster) {
    if (s_vol_type == FAT_TYPE_FAT32) {
        uint32_t fat_offset = cluster * 4;
        uint32_t fat_sector = s_fat_start_sector + (fat_offset / SD_BLOCK_SIZE);
        uint32_t fat_index  = fat_offset % SD_BLOCK_SIZE;

        if (!sd_card_read_block(fat_sector, s_sector_buf)) return FAT32_EOC;
        uint32_t next = read_le32(&s_sector_buf[fat_index]) & 0x0FFFFFFF;
        return (next >= FAT32_EOC) ? 0xFFFFFFFF : next;
    } else {
        uint32_t fat_offset = cluster * 2;
        uint32_t fat_sector = s_fat_start_sector + (fat_offset / SD_BLOCK_SIZE);
        uint32_t fat_index  = fat_offset % SD_BLOCK_SIZE;

        if (!sd_card_read_block(fat_sector, s_sector_buf)) return 0xFFFF;
        uint16_t next = read_le16(&s_sector_buf[fat_index]);
        return (next >= FAT16_EOC) ? 0xFFFFFFFF : next;
    }
}

bool fat_mount(void) {
    s_mounted = false;
    if (!sd_card_is_ready()) {
        if (!sd_card_init()) return false;
    }

    // Read Sector 0
    if (!sd_card_read_block(0, s_sector_buf)) return false;

    // Check boot signature 0x55, 0xAA
    if (s_sector_buf[510] != 0x55 || s_sector_buf[511] != 0xAA) return false;

    s_lba_start = 0;
    // Check if sector 0 is MBR (Partition 1 at offset 0x1BE)
    if (s_sector_buf[0x1BE + 4] == 0x0B || s_sector_buf[0x1BE + 4] == 0x0C || // FAT32
        s_sector_buf[0x1BE + 4] == 0x04 || s_sector_buf[0x1BE + 4] == 0x06 || // FAT16
        s_sector_buf[0x1BE + 4] == 0x0E) {
        s_lba_start = read_le32(&s_sector_buf[0x1BE + 8]);
        if (!sd_card_read_block(s_lba_start, s_sector_buf)) return false;
    }

    // Parse VBR / BPB
    s_bytes_per_sector = read_le16(&s_sector_buf[11]);
    if (s_bytes_per_sector != SD_BLOCK_SIZE) return false;

    s_sectors_per_cluster = s_sector_buf[13];
    uint16_t reserved_sectors = read_le16(&s_sector_buf[14]);
    uint8_t num_fats = s_sector_buf[16];
    s_root_dir_entries = read_le16(&s_sector_buf[17]);
    uint16_t total_sectors_16 = read_le16(&s_sector_buf[19]);
    s_sectors_per_fat = read_le16(&s_sector_buf[22]);

    uint32_t total_sectors = (total_sectors_16 != 0) ? total_sectors_16 : read_le32(&s_sector_buf[32]);

    if (s_sectors_per_fat == 0) {
        // FAT32
        s_sectors_per_fat = read_le32(&s_sector_buf[36]);
        s_root_cluster = read_le32(&s_sector_buf[44]);
        s_vol_type = FAT_TYPE_FAT32;
    } else {
        // FAT16
        s_root_cluster = 0;
        s_vol_type = FAT_TYPE_FAT16;
    }

    s_fat_start_sector = s_lba_start + reserved_sectors;
    s_root_dir_sector = s_fat_start_sector + (num_fats * s_sectors_per_fat);
    
    uint32_t root_dir_sectors = ((s_root_dir_entries * 32) + (s_bytes_per_sector - 1)) / s_bytes_per_sector;
    s_data_start_sector = s_root_dir_sector + root_dir_sectors;

    s_mounted = true;
    return true;
}

bool fat_is_mounted(void) {
    return s_mounted;
}

static bool match_extension(const char *name) {
    const char *dot = strrchr(name, '.');
    if (!dot) return false;
    if (strcasecmp(dot, ".tap") == 0) return true;
    if (strcasecmp(dot, ".tzx") == 0) return true;
    if (strcasecmp(dot, ".csw") == 0) return true;
    if (strcasecmp(dot, ".cas") == 0) return true;
    return false;
}

static void parse_short_name(const uint8_t *entry, char *out_name) {
    char name[9] = {0};
    char ext[4]  = {0};
    int ni = 0, ei = 0;

    for (int i = 0; i < 8; i++) {
        if (entry[i] != ' ') name[ni++] = (char)entry[i];
    }
    for (int i = 8; i < 11; i++) {
        if (entry[i] != ' ') ext[ei++] = (char)entry[i];
    }

    if (ei > 0) {
        snprintf(out_name, FAT_MAX_FILENAME, "%s.%s", name, ext);
    } else {
        snprintf(out_name, FAT_MAX_FILENAME, "%s", name);
    }
}

uint16_t fat_list_files(const char *dir_path, fat_file_info_t *out_files, uint16_t max_files) {
    if (!s_mounted || !out_files || max_files == 0) return 0;

    uint16_t found_count = 0;
    uint32_t current_sec = (s_vol_type == FAT_TYPE_FAT32) ? cluster_to_sector(s_root_cluster) : s_root_dir_sector;
    uint32_t total_sec   = (s_vol_type == FAT_TYPE_FAT32) ? s_sectors_per_cluster : (s_root_dir_entries * 32 / SD_BLOCK_SIZE);

    for (uint32_t s = 0; s < total_sec && found_count < max_files; s++) {
        if (!sd_card_read_block(current_sec + s, s_sector_buf)) break;

        for (int i = 0; i < SD_BLOCK_SIZE; i += 32) {
            uint8_t *e = &s_sector_buf[i];
            if (e[0] == 0x00) return found_count; // End of directory
            if (e[0] == 0xE5) continue;           // Deleted file
            if (e[11] == ATTR_LONG_NAME) continue;
            if (e[11] & (ATTR_VOLUME_ID | ATTR_HIDDEN | ATTR_SYSTEM)) continue;

            char fname[FAT_MAX_FILENAME];
            parse_short_name(e, fname);

            bool is_dir = (e[11] & ATTR_DIRECTORY) != 0;
            if (is_dir || match_extension(fname)) {
                strncpy(out_files[found_count].filename, fname, FAT_MAX_FILENAME - 1);
                out_files[found_count].filename[FAT_MAX_FILENAME - 1] = '\0';
                out_files[found_count].size = read_le32(&e[28]);
                
                uint32_t clus = read_le16(&e[26]);
                if (s_vol_type == FAT_TYPE_FAT32) {
                    clus |= ((uint32_t)read_le16(&e[20]) << 16);
                }
                out_files[found_count].first_cluster = clus;
                out_files[found_count].is_directory = is_dir;
                found_count++;
                if (found_count >= max_files) break;
            }
        }
    }
    return found_count;
}

bool fat_open_read(const char *path, fat_file_t *file) {
    if (!s_mounted || !path || !file) return false;
    memset(file, 0, sizeof(fat_file_t));

    // Strip leading slash
    const char *target = (path[0] == '/') ? &path[1] : path;

    uint32_t current_sec = (s_vol_type == FAT_TYPE_FAT32) ? cluster_to_sector(s_root_cluster) : s_root_dir_sector;
    uint32_t total_sec   = (s_vol_type == FAT_TYPE_FAT32) ? s_sectors_per_cluster : (s_root_dir_entries * 32 / SD_BLOCK_SIZE);

    for (uint32_t s = 0; s < total_sec; s++) {
        if (!sd_card_read_block(current_sec + s, s_sector_buf)) break;

        for (int i = 0; i < SD_BLOCK_SIZE; i += 32) {
            uint8_t *e = &s_sector_buf[i];
            if (e[0] == 0x00) return false;
            if (e[0] == 0xE5 || e[11] == ATTR_LONG_NAME) continue;

            char fname[FAT_MAX_FILENAME];
            parse_short_name(e, fname);

            if (strcasecmp(fname, target) == 0) {
                uint32_t clus = read_le16(&e[26]);
                if (s_vol_type == FAT_TYPE_FAT32) {
                    clus |= ((uint32_t)read_le16(&e[20]) << 16);
                }
                file->first_cluster   = clus;
                file->current_cluster = clus;
                file->current_sector  = cluster_to_sector(clus);
                file->file_size       = read_le32(&e[28]);
                file->file_pos        = 0;
                file->dir_sector      = current_sec + s;
                file->dir_offset      = (uint32_t)i;
                file->is_open         = true;
                file->is_write        = false;
                return true;
            }
        }
    }
    return false;
}

uint32_t fat_read(fat_file_t *file, uint8_t *buffer, uint32_t len) {
    if (!file || !file->is_open || !buffer || len == 0) return 0;

    if (file->file_pos + len > file->file_size) {
        len = file->file_size - file->file_pos;
    }

    uint32_t bytes_read = 0;
    while (bytes_read < len) {
        uint32_t sector_offset = file->file_pos % SD_BLOCK_SIZE;
        uint32_t chunk = SD_BLOCK_SIZE - sector_offset;
        if (chunk > (len - bytes_read)) chunk = (len - bytes_read);

        if (!sd_card_read_block(file->current_sector, s_sector_buf)) break;
        memcpy(buffer + bytes_read, s_sector_buf + sector_offset, chunk);

        bytes_read += chunk;
        file->file_pos += chunk;

        // If sector boundary reached, advance to next sector or next cluster
        if ((file->file_pos % SD_BLOCK_SIZE) == 0 && file->file_pos < file->file_size) {
            uint32_t cluster_sec_idx = ((file->file_pos / SD_BLOCK_SIZE) % s_sectors_per_cluster);
            if (cluster_sec_idx == 0) {
                // Advance cluster
                uint32_t next = get_next_cluster(file->current_cluster);
                if (next == 0xFFFFFFFF) break;
                file->current_cluster = next;
                file->current_sector  = cluster_to_sector(next);
            } else {
                file->current_sector++;
            }
        }
    }
    return bytes_read;
}

bool fat_seek(fat_file_t *file, uint32_t offset) {
    if (!file || !file->is_open || offset > file->file_size) return false;

    file->file_pos = 0;
    file->current_cluster = file->first_cluster;
    file->current_sector  = cluster_to_sector(file->first_cluster);

    uint32_t clusters_to_skip = offset / (s_sectors_per_cluster * SD_BLOCK_SIZE);
    for (uint32_t i = 0; i < clusters_to_skip; i++) {
        uint32_t next = get_next_cluster(file->current_cluster);
        if (next == 0xFFFFFFFF) return false;
        file->current_cluster = next;
    }

    uint32_t remainder_sectors = (offset % (s_sectors_per_cluster * SD_BLOCK_SIZE)) / SD_BLOCK_SIZE;
    file->current_sector = cluster_to_sector(file->current_cluster) + remainder_sectors;
    file->file_pos = offset;
    return true;
}

bool fat_open_write(const char *path, fat_file_t *file) {
    // Basic write stub for recording dump files into pre-allocated continuous sectors
    if (!s_mounted || !path || !file) return false;
    memset(file, 0, sizeof(fat_file_t));
    file->is_open = true;
    file->is_write = true;
    file->file_size = 0;
    file->file_pos = 0;
    return true;
}

uint32_t fat_write(fat_file_t *file, const uint8_t *buffer, uint32_t len) {
    if (!file || !file->is_open || !file->is_write || !buffer) return 0;
    file->file_pos += len;
    if (file->file_pos > file->file_size) file->file_size = file->file_pos;
    return len;
}

void fat_close(fat_file_t *file) {
    if (file) {
        file->is_open = false;
    }
}
