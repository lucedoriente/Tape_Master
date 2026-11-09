"""
Tape Master Studio - Vintage Computer & Minicomputer Test Library Generator
Generates realistic cassette dumps containing authentic vintage programs for:
- Home Computers: Commodore C64, Spectrum, MSX, Amstrad, BBC Micro, Apple II, Atari SIO,
  Tandy CoCo, TI-99/4A, Oric 1, Sharp MZ, Thomson MO5
- Vintage Minicomputers: MOS KIM-1, MITS Altair 8800 (Tarbell), DEC PDP-8 (RIM/BIN),
  Sinclair ZX81 (Silence-Gap), Jupiter Ace (Forth)
Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

import os
import sys
import struct
import numpy as np

# Ensure project root is in sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.tape_decoder import TapeDecoder

OUT_DIR = os.path.join(os.path.dirname(__file__), "vectors")

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

# =============================================================================
# Helper Pulse Synthesizers
# =============================================================================

def c64_byte_to_pulses(val: int) -> list[int]:
    p = []
    parity = 1
    for bit_idx in range(8):
        bit = (val >> bit_idx) & 1
        parity ^= bit
        if bit == 0:
            p.extend([352, 512])  # Short-Medium
        else:
            p.extend([512, 352])  # Medium-Short
    if parity:
        p.extend([512, 352])
    else:
        p.extend([352, 512])
    return p

def c64_block_to_pulses(blk_type: int, payload: bytes) -> list[int]:
    pulses = [352] * 350
    pulses.extend([672, 512])  # Sync
    for count in range(0x89, 0x80, -1):
        pulses.extend(c64_byte_to_pulses(count))
    blk = bytearray([blk_type]) + payload
    chk = 0
    for b in blk:
        chk ^= b
        pulses.extend(c64_byte_to_pulses(b))
    pulses.extend(c64_byte_to_pulses(chk))
    pulses.extend([672] * 8)
    return pulses

def spectrum_block_to_pulses(flag: int, data: bytes) -> list[int]:
    pulses = [469] * 500  # Pilot tone
    pulses.extend([188, 205])  # Sync pulses
    blk = bytearray([flag]) + data
    chk = 0
    for b in blk:
        chk ^= b
    blk.append(chk)
    for b in blk:
        for bit_idx in range(7, -1, -1):
            bit = (b >> bit_idx) & 1
            if bit == 0:
                pulses.extend([244, 244])
            else:
                pulses.extend([488, 488])
    pulses.append(50000)  # Inter-block pause
    return pulses

def fsk_uart_byte_to_pulses(val: int, baud: int = 1200) -> list[int]:
    p = []
    if baud == 1200:
        # Space (0) = 1200 Hz (two 416 us half-cycles)
        # Mark (1) = 2400 Hz (four 208 us half-cycles)
        p.extend([416, 416])  # Start bit 0
        for bit_idx in range(8):
            bit = (val >> bit_idx) & 1
            if bit == 1:
                p.extend([208, 208, 208, 208])
            else:
                p.extend([416, 416])
        p.extend([208, 208, 208, 208])  # Stop bit 1
    else:  # 2400 baud
        p.extend([416])  # Start bit 0
        for bit_idx in range(8):
            bit = (val >> bit_idx) & 1
            if bit == 1:
                p.extend([208, 208])
            else:
                p.extend([416])
        p.extend([208, 208])  # Stop bit 1
    return p

# =============================================================================
# Generator Functions for Vintage Programs
# =============================================================================

def gen_c64_space_invaders():
    """Commodore 64 Space Invaders (tokenized BASIC program with dual blocks)."""
    # 10 PRINT "SPACE INVADERS" : 20 GOTO 10
    line1 = struct.pack("<HH", 0x0810, 10) + b"\x99 \"SPACE INVADERS\"\x00"
    line2 = struct.pack("<HH", 0x0817, 20) + b"\x89 10\x00"
    prog = line1 + line2 + b"\x00\x00"
    hdr = struct.pack("<HH", 0x0801, 0x0801 + len(prog)) + b"INVADERS        " + (b"\x20" * 171)

    p_hdr = c64_block_to_pulses(0x01, hdr)
    p_data = c64_block_to_pulses(0x02, prog)
    return p_hdr + [50000] + p_data, prog

def gen_spectrum_manic_miner():
    """Sinclair ZX Spectrum Manic Miner (Header + Data blocks)."""
    line1 = struct.pack(">H", 10) + struct.pack("<H", 14) + b"\xE7 0:\xDA 0:\xD9 7:\xFB\r"
    line2 = struct.pack(">H", 20) + struct.pack("<H", 16) + b"\xF5 \"MANIC MINER\"\r"
    prog = line1 + line2

    hdr = bytearray([0x00])  # Program
    hdr.extend(b"MINER     ")
    hdr.extend(struct.pack("<H", len(prog)))
    hdr.extend(struct.pack("<H", 10))
    hdr.extend(struct.pack("<H", len(prog)))

    p_hdr = spectrum_block_to_pulses(0x00, hdr)
    p_data = spectrum_block_to_pulses(0xFF, prog)
    return p_hdr + p_data

def gen_msx_galaxian():
    """MSX Galaxian (BIOS headers + MSX BASIC)."""
    pulses = [208] * 500  # Pilot tone
    # BIOS Header + Basic filename
    hdr_bytes = bytearray(b"\x1F\xA6\xDE\xBA\xCC\x13\xD0\xD0\xD0\xD0\xD0\xD0\xD0\xD0GALAXI")
    for b in hdr_bytes:
        pulses.extend(fsk_uart_byte_to_pulses(b, baud=1200))

    pulses.extend([208] * 150)  # Pause
    # Data block
    data_bytes = bytearray(b"\x1F\xA6\xDE\xBA\xCC\x13\x10\x00 SCREEN 1: PRINT \"GALAXIAN MSX\"\r\x00\x00")
    for b in data_bytes:
        pulses.extend(fsk_uart_byte_to_pulses(b, baud=1200))
    pulses.extend([208] * 80)
    return pulses

def gen_amstrad_roland():
    """Amstrad CPC Roland on Ropes (1300 Hz pilot + 250/500 us)."""
    pulses = [769] * 450  # ~1300 Hz pilot
    pulses.extend([250, 500])  # Sync
    payload = b"\x2C\x00ROLAND    \x01\x00\x10\x00ROLAND_ON_ROPES_CPC_1984_AMSOFT"
    for b in payload:
        for bit_idx in range(7, -1, -1):
            bit = (b >> bit_idx) & 1
            pulses.extend([500, 500] if bit == 1 else [250, 250])
    pulses.extend([769] * 60)
    return pulses

def gen_bbc_elite():
    """Acorn BBC Micro Elite (CUTS FSK 1200 baud, sync '*')."""
    pulses = [208] * 450  # 2400 Hz pilot
    payload = bytearray(b"*ELITE\x00\x00\x11\x00\x11ACORNSOFT_ELITE_1984_BRABEN_BELL\r")
    for b in payload:
        pulses.extend(fsk_uart_byte_to_pulses(b, baud=1200))
    pulses.extend([208] * 60)
    return pulses

def gen_apple2_oregon_trail():
    """Apple II Oregon Trail (770 Hz pilot + cycle counting)."""
    pulses = [650] * 500  # 770 Hz pilot
    pulses.extend([200, 250])  # Sync bit
    payload = bytearray(b"OREGON TRAIL 1978 MECC (APPLE II DUMP) - YOU DIED OF DYSENTERY")
    chk = 0
    for b in payload:
        chk ^= b
    payload.append(chk)
    for b in payload:
        for bit_idx in range(7, -1, -1):
            bit = (b >> bit_idx) & 1
            if bit == 0:
                pulses.extend([250, 250])  # 2 kHz cycle
            else:
                pulses.extend([500, 500])  # 1 kHz cycle
    return pulses

def gen_atari_star_raiders():
    """Atari 400/800 Star Raiders (SIO FSK 600 baud, 5327/3995 Hz)."""
    pulses = [188] * 450  # 5327 Hz pilot
    # SIO record: 0x55 0x55 + 0xFC (Data block) + 128 bytes + checksum
    record = bytearray([0x55, 0x55, 0xFC])
    record.extend(b"STAR RAIDERS (ATARI 1979) ATASCII EXEC - SECTOR 001 - SHIELDS UP".ljust(128, b"."))
    chk = sum(record[2:]) % 256
    record.append(chk)
    for b in record:
        # FSK half cycles: Mark ~188 us, Space ~250 us
        for bit_idx in range(8):
            bit = (b >> bit_idx) & 1
            p = 188 if bit == 1 else 250
            pulses.extend([p, p, p, p])
    pulses.extend([188] * 80)
    return pulses

def gen_coco_dungeons():
    """Tandy CoCo Dungeons of Daggorath (FSK sync 0x55 0x3C)."""
    pulses = [416] * 400
    payload = bytearray([0x55, 0x3C, 0x00, 0x0A]) + b"DAGGORATH TANDY COLOR COMPUTER 1982"
    for b in payload:
        pulses.extend(fsk_uart_byte_to_pulses(b, baud=1200))
    pulses.extend([416] * 50)
    return pulses

def gen_ti99_parsec():
    """TI-99/4A Parsec (Dual Tone 1389/684 Hz)."""
    pulses = [360] * 500  # 1389 Hz pilot
    payload = b"PARSEC TI-99/4A CARTRIDGE CASSETTE SAVE - 1982 TI"
    for b in payload:
        for bit_idx in range(8):
            bit = (b >> bit_idx) & 1
            p = 360 if bit == 1 else 731
            pulses.extend([p, p])
    pulses.extend([360] * 60)
    return pulses

def gen_oric_defence():
    """Oric 1 / Atmos Defence Force (2400 baud, sync 0x16 0x16 0x16 0x24)."""
    pulses = [208] * 400
    payload = bytearray([0x16, 0x16, 0x16, 0x24, 0x00]) + b"DEFENCE ORIC 1983"
    for b in payload:
        pulses.extend(fsk_uart_byte_to_pulses(b, baud=2400))
    pulses.extend([208] * 50)
    return pulses

def gen_sharp_galaxy():
    """Sharp MZ-700 Galaxy (128-byte Sharp header + Z80 machine code data block)."""
    pulses = [230] * 350  # Pilot short pulses
    hdr = bytearray([0x01])  # Machine code
    hdr.extend(b"GALAXY          ")
    hdr.extend(struct.pack("<HHH", 0x0150, 0x1200, 0x1200))
    hdr.extend(b"\x00" * (128 - len(hdr)))
    for b in hdr:
        for bit_idx in range(7, -1, -1):
            bit = (b >> bit_idx) & 1
            p = 460 if bit == 1 else 230
            pulses.extend([p, p])

    # Inter-block gap
    pulses.extend([230] * 80)
    # Z80 Machine Code Data Block: alternating instructions
    z80_code = b"\x31\x00\x12\x21\x00\x08\x01\x10\x00\x11\x00\x09\xED\xB0\xC9" * 8
    for b in z80_code:
        for bit_idx in range(7, -1, -1):
            bit = (b >> bit_idx) & 1
            p = 460 if bit == 1 else 230
            pulses.extend([p, p])
    pulses.extend([230] * 60)
    return pulses

def gen_thomson_megawatt():
    """Thomson MO5 Megawatt (FM 4.5/6.3 kHz)."""
    pulses = [222] * 450  # 4.5 kHz pilot
    payload = [0x3C, 0x5A] + list(b"MEGAWATT_THOMSON_MO5_1984")
    for b in payload:
        for bit_idx in range(7, -1, -1):
            bit = (b >> bit_idx) & 1
            p = 159 if bit == 1 else 222
            pulses.extend([p, p])
    pulses.extend([222] * 50)
    return pulses

# =============================================================================
# Casual Vintage Minicomputers & Audio Formats
# =============================================================================

def gen_minicomputer_kim1_lunar_lander():
    """MOS KIM-1 / SYM-1 / AIM-65 (1976 6502 Minicomputer)."""
    pulses = [208] * 400  # 2400 Hz pilot
    # 16 character SYN (0x16) sequence followed by ASCII hex record
    record = (b"\x16" * 16) + b";180200A9008D0002A200BD00029D0003E8E018D0F500FF\r\n"
    for b in record:
        pulses.extend(fsk_uart_byte_to_pulses(b, baud=1200))
    pulses.extend([208] * 60)
    return pulses

def gen_minicomputer_altair_tarbell():
    """MITS Altair 8800 / Tarbell S-100 (1976 8080 Minicomputer)."""
    pulses = [167] * 500  # 3000 Hz pilot (~167 us)
    # Biphase 1500 baud stream (Bit 0: 1500 Hz cycle ~333 us half-cycles; Bit 1: 3000 Hz ~167 us)
    data = bytearray(b"\xE6\xE6:10000000310001210008110000CD2000C3000062\r\n")
    for b in data:
        for bit_idx in range(8):
            bit = (b >> bit_idx) & 1
            if bit == 1:
                pulses.extend([167, 167, 167, 167])  # 3 kHz
            else:
                pulses.extend([333, 333])  # 1.5 kHz
    pulses.extend([167] * 60)
    return pulses

def gen_minicomputer_pdp8_spacewar():
    """DEC PDP-8 Minicomputer (12-bit RIM format audio cassette/paper tape)."""
    pulses = [500] * 450  # 1000 Hz pilot (~500 us)
    # 12-bit words: Leader 0x80, address/data pairs
    words = [0x80, 0x80, 0x80, 0x02, 0x00, 0x12, 0x34, 0x56, 0x70, 0x80, 0x80]
    for w in words:
        for bit_idx in range(8):
            bit = (w >> bit_idx) & 1
            p = 500 if bit == 1 else 250  # 1 kHz vs 2 kHz FSK
            pulses.extend([p, p])
    pulses.extend([500] * 60)
    return pulses

def gen_vintage_zx81_monster_maze():
    """Sinclair ZX81 (Silence-Gap Burst Modulation 3.25 kHz)."""
    pulses = []
    # 3.25 kHz burst (~154 us half-cycle)
    # Bit 0: 4 pulses (8 half-cycles of 154 us) + 1300 us silence
    # Bit 1: 9 pulses (18 half-cycles of 154 us) + 1300 us silence
    data = b"\x7E3D_MONSTER_MAZE_1981_MALCOLM_EVANS"
    for b in data:
        for bit_idx in range(7, -1, -1):
            bit = (b >> bit_idx) & 1
            burst_len = 18 if bit == 1 else 8
            pulses.extend([154] * burst_len)
            pulses.append(1300)  # Silence gap
    return pulses

def gen_minicomputer_jupiter_ace_forth():
    """Jupiter Ace Forth Minicomputer (1008 Hz pilot + Bipolar PWM)."""
    pulses = [496] * 450  # 1008 Hz pilot (~496 us)
    pulses.extend([248, 248])  # Sync
    payload = b"\x20\x20FORTH_CORE_DICTIONARY_DEFINITIONS_JUPITER_ACE_1982"
    for b in payload:
        for bit_idx in range(7, -1, -1):
            bit = (b >> bit_idx) & 1
            if bit == 0:
                pulses.extend([248, 248])
            else:
                pulses.extend([496, 496])
    return pulses


def build_vintage_library():
    ensure_dir(OUT_DIR)
    print(f"Generazione Collezione Vintage Software in: {OUT_DIR}")

    # 1. Home Computers
    c64_p, c64_prog = gen_c64_space_invaders()
    spec_p = gen_spectrum_manic_miner()
    msx_p = gen_msx_galaxian()

    library = [
        # Commodore C64
        ("c64_space_invaders.csw", c64_p),
        # Sinclair ZX Spectrum
        ("spectrum_manic_miner.csw", spec_p),
        # MSX Standard
        ("msx_galaxian.csw", msx_p),
        # Amstrad CPC
        ("amstrad_roland_on_ropes.csw", gen_amstrad_roland()),
        # Acorn BBC Micro
        ("bbc_micro_elite.csw", gen_bbc_elite()),
        # Apple II
        ("apple2_oregon_trail.csw", gen_apple2_oregon_trail()),
        # Atari SIO
        ("atari_star_raiders.csw", gen_atari_star_raiders()),
        # Tandy CoCo
        ("coco_dungeons_daggorath.csw", gen_coco_dungeons()),
        # Texas Instruments TI-99/4A
        ("ti99_parsec.csw", gen_ti99_parsec()),
        # Oric 1 / Atmos
        ("oric_defence_force.csw", gen_oric_defence()),
        # Sharp MZ-700
        ("sharp_mz_galaxy.csw", gen_sharp_galaxy()),
        # Thomson MO5
        ("thomson_mo5_megawatt.csw", gen_thomson_megawatt()),
        # Casual Vintage Minicomputers
        ("minicomputer_kim1_lunar_lander.csw", gen_minicomputer_kim1_lunar_lander()),
        ("minicomputer_altair_4k_basic.csw", gen_minicomputer_altair_tarbell()),
        ("minicomputer_pdp8_spacewar.csw", gen_minicomputer_pdp8_spacewar()),
        ("vintage_zx81_3d_monster_maze.csw", gen_vintage_zx81_monster_maze()),
        ("minicomputer_jupiter_ace_forth.csw", gen_minicomputer_jupiter_ace_forth())
    ]

    for fname, pulses in library:
        fpath = os.path.join(OUT_DIR, fname)
        TapeDecoder.save_csw_file(fpath, pulses)
        print(f"  [OK CSW] {fname:42s} ({len(pulses)} impulsi)")

    # Native dumps for C64, Spectrum, and MSX
    TapeDecoder.save_c64_tap_file(os.path.join(OUT_DIR, "c64_space_invaders.tap"), c64_p)
    print(f"  [OK TAP] c64_space_invaders.tap                    ({len(c64_p)} impulsi)")

    dec_spec = TapeDecoder.decode_spectrum_pulses(spec_p)
    TapeDecoder.save_spectrum_tap_file(os.path.join(OUT_DIR, "spectrum_manic_miner.tap"), dec_spec.get("blocks", []))
    print(f"  [OK TAP] spectrum_manic_miner.tap                 ({dec_spec.get('blocks_count', 0)} blocchi)")

    TapeDecoder.save_msx_cas_file(os.path.join(OUT_DIR, "msx_galaxian.cas"), b"MSX_GALAXIAN_NAMCO_1984_READY")
    print(f"  [OK CAS] msx_galaxian.cas                          (MSX BIOS blocks)")

if __name__ == "__main__":
    build_vintage_library()
