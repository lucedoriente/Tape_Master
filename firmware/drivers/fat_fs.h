/**
 * Tape Master v2 - Embedded FAT16/FAT32 Filesystem Layer
 * 
 * Lightweight FAT driver supporting directory browsing, file streaming,
 * and dump creation for Tape Master Virtual Deck & Digitizer.
 * Author: Alessio Iodice <alessio67@gmail.com>
 * License: CC BY-NC-SA 4.0
 */

#ifndef FAT_FS_H
#define FAT_FS_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define FAT_MAX_FILENAME    64
#define FAT_MAX_FILES_LIST  32

typedef enum {
    FAT_TYPE_FAT16,
    FAT_TYPE_FAT32
} fat_vol_type_t;

typedef struct {
    char     filename[FAT_MAX_FILENAME];
    uint32_t size;
    uint32_t first_cluster;
    bool     is_directory;
} fat_file_info_t;

typedef struct {
    uint32_t first_cluster;
    uint32_t current_cluster;
    uint32_t current_sector;
    uint32_t file_size;
    uint32_t file_pos;
    uint32_t dir_sector;
    uint32_t dir_offset;
    bool     is_open;
    bool     is_write;
} fat_file_t;

/**
 * Mount FAT volume from initialized SD card.
 * Detects MBR or superfloppy layout, determines FAT16/FAT32 parameters.
 * 
 * @return true if valid FAT16 or FAT32 partition successfully mounted.
 */
bool fat_mount(void);

/**
 * Check if a volume is currently mounted.
 */
bool fat_is_mounted(void);

/**
 * List files matching allowed extensions (.TAP, .TZX, .CSW, .CAS).
 * 
 * @param dir_path Directory path (e.g. "/" or "/TAPES").
 * @param out_files Array to hold file entries.
 * @param max_files Maximum number of entries to return.
 * @return Number of matching files found.
 */
uint16_t fat_list_files(const char *dir_path, fat_file_info_t *out_files, uint16_t max_files);

/**
 * Open an existing file for reading.
 * 
 * @param path Full file path (e.g. "/TAPES/GianaSisters.tap").
 * @param file File handle structure to populate.
 * @return true if opened successfully.
 */
bool fat_open_read(const char *path, fat_file_t *file);

/**
 * Read data from currently open file.
 * 
 * @param file Active file handle.
 * @param buffer Output buffer.
 * @param len Number of bytes to read.
 * @return Actual bytes read.
 */
uint32_t fat_read(fat_file_t *file, uint8_t *buffer, uint32_t len);

/**
 * Seek to byte offset within open file.
 */
bool fat_seek(fat_file_t *file, uint32_t offset);

/**
 * Create a new file for writing (e.g. for signal capture dump).
 * 
 * @param path Target path (e.g. "/DUMPS/REC_0001.CSW").
 * @param file File handle to initialize.
 * @return true on success.
 */
bool fat_open_write(const char *path, fat_file_t *file);

/**
 * Write data to an open write file handle.
 */
uint32_t fat_write(fat_file_t *file, const uint8_t *buffer, uint32_t len);

/**
 * Close an open file, flushing directory size updates to SD card.
 */
void fat_close(fat_file_t *file);

#ifdef __cplusplus
}
#endif

#endif // FAT_FS_H
