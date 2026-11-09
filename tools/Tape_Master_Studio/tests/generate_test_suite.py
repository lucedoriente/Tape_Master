"""
Tape Master Studio - Synthetic Test Suite Generator
Generates realistic .CSW, .TAP, .TZX, and .CAS test files for all retrocomputer families,
including clean reference vectors across all 13 Tape Master hardware cartridge profiles,
and degraded tapes with wow & flutter, phase jitter, and dropouts.
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

# -----------------------------------------------------------------------------
# 1. Commodore C64 Generator (PWM / Interval)
# -----------------------------------------------------------------------------
def generate_c64_clean() -> list[int]:
    """Generates standard C64 ROM tape pulses: Short ~352 us, Medium ~512 us, Long ~672 us."""
    pulses = []
    # Pilot tone: 400 Short pulses (~352 us)
    pulses.extend([352] * 400)
    # Sync: Long + Medium
    pulses.extend([672, 512])

    # Byte to C64 pulses (SM = 0, MS = 1, LSB first)
    def byte_to_c64(val: int):
        p = []
        for bit_idx in range(8):
            bit = (val >> bit_idx) & 1
            if bit == 0:
                p.extend([352, 512])  # SM
            else:
                p.extend([512, 352])  # MS
        # Parity bit (odd)
        p.extend([352, 512])
        return p

    # Countdown marker: 0x89 down to 0x81
    for count in range(0x89, 0x80, -1):
        pulses.extend(byte_to_c64(count))

    # Header block: Type 0x01 (PRG), Start 0x0801, End 0x0810, Name "TESTC64         "
    hdr_data = bytearray([0x01, 0x01, 0x08, 0x10, 0x08])
    hdr_data.extend(b"TESTC64         ")
    hdr_data.extend(b"\x20" * 171)  # Filler

    for b in hdr_data:
        pulses.extend(byte_to_c64(b))

    pulses.extend([672] * 10)
    return pulses

# -----------------------------------------------------------------------------
# 2. Atari SIO Generator (FSK 600 baud)
# -----------------------------------------------------------------------------
def generate_atari_sio_clean() -> list[int]:
    """Atari SIO tape: Mark 5327 Hz (~188 us), Space 3995 Hz (~250 us)."""
    pulses = []
    # Pilot Mark tone: 500 pulses of 188 us
    pulses.extend([188] * 500)
    # Dummy record with alternating Mark and Space pulses
    for _ in range(40):
        pulses.extend([188, 188, 250, 250, 188, 250, 188, 188])
    pulses.extend([188] * 100)
    return pulses

# -----------------------------------------------------------------------------
# 3. Thomson MO5/TO7 Generator (FM 4.5 / 6.3 kHz)
# -----------------------------------------------------------------------------
def generate_thomson_clean() -> list[int]:
    """Thomson FM: Pilot 4.5 kHz (~222 us), Bit 0 (222 us), Bit 1 (159 us)."""
    pulses = []
    # Pilot: 500 pulses of 222 us
    pulses.extend([222] * 500)
    # Sync byte 0x3C and 0x5A followed by data bits
    data = [0x3C, 0x5A, 0x01, 0x02, 0xAA, 0x55]
    for b in data:
        for bit_idx in range(7, -1, -1):
            bit = (b >> bit_idx) & 1
            p = 159 if bit == 1 else 222
            pulses.extend([p, p])
    pulses.extend([222] * 50)
    return pulses

# -----------------------------------------------------------------------------
# 4. Sinclair ZX Spectrum Generator (Bipolar PWM)
# -----------------------------------------------------------------------------
def generate_spectrum_clean() -> list[int]:
    """
    Standard Spectrum tape pulses:
    Pilot: 2168 T (~469 us), Sync: 667 T (~188 us) + 735 T (~205 us),
    Bit 0: two 855 T pulses (~244 us each), Bit 1: two 1710 T pulses (~488 us each).
    """
    pulses = []
    # Pilot: 800 pulses of 469 us
    pulses.extend([469] * 800)
    pulses.extend([188, 205])

    # Header block: Flag 0x00, Type 0x00 (Program), Name "SPECTRUM  ", Length 100, Start 10
    hdr = bytearray([0x00, 0x00])
    hdr.extend(b"SPECTRUM  ")
    hdr.extend(struct.pack("<H", 100))
    hdr.extend(struct.pack("<H", 10))
    hdr.extend(struct.pack("<H", 100))

    chk = 0
    for b in hdr:
        chk ^= b
    hdr.append(chk)

    for b in hdr:
        for bit_idx in range(7, -1, -1):
            bit = (b >> bit_idx) & 1
            if bit == 0:
                pulses.extend([244, 244])
            else:
                pulses.extend([488, 488])

    pulses.append(50000)
    return pulses

# -----------------------------------------------------------------------------
# 5. Amstrad CPC Generator (Cycle PWM)
# -----------------------------------------------------------------------------
def generate_amstrad_clean() -> list[int]:
    """Amstrad CPC: Pilot ~1300 Hz (~769 us), Bit 0 (250 us), Bit 1 (500 us)."""
    pulses = []
    pulses.extend([769] * 400)
    pulses.extend([250, 500])  # Sync
    for _ in range(30):
        pulses.extend([250, 250, 500, 500, 250, 500, 250, 250])
    pulses.extend([769] * 50)
    return pulses

# -----------------------------------------------------------------------------
# 6. MSX Standard / Kansas City FSK Generator (1200 baud)
# -----------------------------------------------------------------------------
def generate_msx_fsk_clean() -> list[int]:
    """
    Kansas City Standard FSK (1200 baud):
    Mark = 2400 Hz (half cycle ~208 us, 4 half cycles per bit)
    Space = 1200 Hz (half cycle ~416 us, 2 half cycles per bit)
    UART: 1 Start bit (Space), 8 Data bits (LSB), 1 Stop bit (Mark)
    """
    pulses = []
    # Pilot tone: 500 Mark half-cycles (~208 us)
    pulses.extend([208] * 500)

    payload = bytearray(b"\x1F\xA6\xDE\xBA\xCC\x13\x00\x00\x00\x00TESTMSX ")

    def byte_to_uart_fsk(val: int):
        p = []
        # Start bit: Space (0) -> 2 half cycles of 416 us
        p.extend([416, 416])
        # 8 Data bits (LSB first)
        for bit_idx in range(8):
            bit = (val >> bit_idx) & 1
            if bit == 1:
                p.extend([208, 208, 208, 208])
            else:
                p.extend([416, 416])
        # Stop bit: Mark (1) -> 4 half cycles of 208 us
        p.extend([208, 208, 208, 208])
        return p

    for b in payload:
        pulses.extend(byte_to_uart_fsk(b))

    pulses.extend([208] * 100)
    return pulses

# -----------------------------------------------------------------------------
# 7. Acorn BBC Micro Generator (CUTS FSK)
# -----------------------------------------------------------------------------
def generate_bbc_clean() -> list[int]:
    """Acorn BBC: 2400 Hz pilot (~208 us), sync byte '*' (0x2A), 1200/2400 Hz FSK."""
    pulses = []
    pulses.extend([208] * 500)
    payload = bytearray(b"*BBC_TEST_PROGRAM\r")
    for b in payload:
        # Start bit (0)
        pulses.extend([416, 416])
        for bit_idx in range(8):
            bit = (b >> bit_idx) & 1
            if bit == 1:
                pulses.extend([208, 208, 208, 208])
            else:
                pulses.extend([416, 416])
        # Stop bit (1)
        pulses.extend([208, 208, 208, 208])
    pulses.extend([208] * 60)
    return pulses

# -----------------------------------------------------------------------------
# 8. Tandy CoCo Generator (FSK Sine Crossing)
# -----------------------------------------------------------------------------
def generate_coco_clean() -> list[int]:
    """CoCo: 1200/2400 Hz FSK, sync 0x55 then 0x3C."""
    pulses = []
    pulses.extend([416] * 400)
    payload = bytearray([0x55, 0x3C, 0x00, 0x0F, 0x43, 0x4F, 0x43, 0x4F])
    for b in payload:
        pulses.extend([416, 416])  # Start
        for bit_idx in range(8):
            bit = (b >> bit_idx) & 1
            if bit == 1:
                pulses.extend([208, 208, 208, 208])
            else:
                pulses.extend([416, 416])
        pulses.extend([208, 208, 208, 208])  # Stop
    pulses.extend([416] * 50)
    return pulses

# -----------------------------------------------------------------------------
# 9. Texas Instruments TI-99/4A Generator (Dual Tone)
# -----------------------------------------------------------------------------
def generate_ti99_clean() -> list[int]:
    """TI-99/4A: 1389 Hz pilot (~360 us), low tone 684 Hz (~731 us)."""
    pulses = []
    pulses.extend([360] * 500)
    for _ in range(30):
        pulses.extend([360, 360, 731, 731, 360, 731, 360, 360])
    pulses.extend([360] * 60)
    return pulses

# -----------------------------------------------------------------------------
# 10. Apple II Generator (Zero-Crossing Cycle)
# -----------------------------------------------------------------------------
def generate_apple2_clean() -> list[int]:
    """
    Apple II: Pilot 770 Hz (~650 us), Sync bit (200 us, 250 us),
    Bit 0: two 250 us half-cycles (2 kHz), Bit 1: two 500 us half-cycles (1 kHz).
    """
    pulses = []
    pulses.extend([650] * 600)
    pulses.extend([200, 250])

    payload = bytearray(b"APPLE2 CASSETTE DUMP TEST PAYLOAD")
    chk = 0
    for b in payload:
        chk ^= b
    payload.append(chk)

    for b in payload:
        for bit_idx in range(7, -1, -1):
            bit = (b >> bit_idx) & 1
            if bit == 0:
                pulses.extend([250, 250])
            else:
                pulses.extend([500, 500])

    return pulses

# -----------------------------------------------------------------------------
# 11. Oric 1 / Atmos Generator (Fast FSK 2400 baud)
# -----------------------------------------------------------------------------
def generate_oric_clean() -> list[int]:
    """Oric 1: Fast FSK 2400 baud, sync 0x16 0x16 0x16 0x24."""
    pulses = []
    pulses.extend([208] * 400)
    payload = bytearray([0x16, 0x16, 0x16, 0x24, 0x00, 0x50, 0x52, 0x4F, 0x47])
    for b in payload:
        pulses.extend([416])
        for bit_idx in range(8):
            bit = (b >> bit_idx) & 1
            if bit == 1:
                pulses.extend([208, 208])
            else:
                pulses.extend([416])
        pulses.extend([208, 208])
    pulses.extend([208] * 50)
    return pulses

# -----------------------------------------------------------------------------
# 12. Sharp MZ Generator (Sharp PWM Fast)
# -----------------------------------------------------------------------------
def generate_sharp_clean() -> list[int]:
    """Sharp MZ: Pilot Short pulses (~230 us), Bit 0 (230 us), Bit 1 (460 us)."""
    pulses = []
    pulses.extend([230] * 500)
    for _ in range(40):
        pulses.extend([230, 460, 230, 230, 460, 460, 230, 460])
    pulses.extend([230] * 50)
    return pulses

# -----------------------------------------------------------------------------
# 13. Degraded Tape (C64 with Wow & Flutter, Jitter, and Dropout)
# -----------------------------------------------------------------------------
def generate_c64_degraded() -> list[int]:
    """Applies realistic tape wear: wow & flutter (WRMS ~4.5%), jitter, and a 4ms dropout."""
    base_pulses = generate_c64_clean()
    n = len(base_pulses)

    t = np.linspace(0, 4.0, n)
    speed_factor = 1.0 + 0.065 * np.sin(2 * np.pi * 4.0 * t)
    jitter = np.random.normal(0, 14.0, n)

    degraded = []
    for i, p in enumerate(base_pulses):
        new_p = int(round(p * speed_factor[i] + jitter[i]))
        degraded.append(max(25, new_p))

    drop_pos = int(n * 0.6)
    degraded[drop_pos] = 4000
    return degraded

# -----------------------------------------------------------------------------
# 14. Audio / Noise (Rejection Test)
# -----------------------------------------------------------------------------
def generate_audio_noise() -> list[int]:
    """Generates continuous chaotic random pulses to verify false-positive rejection."""
    np.random.seed(42)
    noise = np.random.exponential(scale=350, size=2000).astype(int)
    return [max(30, min(2400, p)) for p in noise]


def build_all_vectors():
    ensure_dir(OUT_DIR)
    print(f"Generazione vettori di test in: {OUT_DIR}")

    c64_p = generate_c64_clean()
    spec_p = generate_spectrum_clean()
    msx_p = generate_msx_fsk_clean()

    # CSW files across platforms
    tests_csw = [
        ("01_c64_clean.csw", c64_p),
        ("01_c64_degraded_jitter_flutter.csw", generate_c64_degraded()),
        ("02_atari_sio_clean.csw", generate_atari_sio_clean()),
        ("03_thomson_clean.csw", generate_thomson_clean()),
        ("04_spectrum_clean.csw", spec_p),
        ("05_amstrad_clean.csw", generate_amstrad_clean()),
        ("06_msx_fsk_clean.csw", msx_p),
        ("07_bbc_clean.csw", generate_bbc_clean()),
        ("08_coco_clean.csw", generate_coco_clean()),
        ("09_ti99_clean.csw", generate_ti99_clean()),
        ("10_apple2_clean.csw", generate_apple2_clean()),
        ("11_oric_clean.csw", generate_oric_clean()),
        ("12_sharp_clean.csw", generate_sharp_clean()),
        ("99_audio_noise_reject.csw", generate_audio_noise())
    ]

    for fname, pulses in tests_csw:
        fpath = os.path.join(OUT_DIR, fname)
        TapeDecoder.save_csw_file(fpath, pulses)
        print(f"  [OK CSW] {fname:38s} ({len(pulses)} impulsi)")

    # Native emulator format files
    c64_tap_path = os.path.join(OUT_DIR, "01_c64_clean.tap")
    TapeDecoder.save_c64_tap_file(c64_tap_path, c64_p)
    print(f"  [OK TAP] 01_c64_clean.tap                       ({len(c64_p)} impulsi)")

    spec_tap_path = os.path.join(OUT_DIR, "04_spectrum_clean.tap")
    dec_spec = TapeDecoder.decode_spectrum_pulses(spec_p)
    TapeDecoder.save_spectrum_tap_file(spec_tap_path, dec_spec.get("blocks", []))
    print(f"  [OK TAP] 04_spectrum_clean.tap                  ({dec_spec.get('blocks_count', 0)} blocchi)")

    spec_tzx_path = os.path.join(OUT_DIR, "04_spectrum_clean.tzx")
    TapeDecoder.save_spectrum_tzx_file(spec_tzx_path, dec_spec.get("blocks", []))
    print(f"  [OK TZX] 04_spectrum_clean.tzx                  ({dec_spec.get('blocks_count', 0)} blocchi)")

    msx_cas_path = os.path.join(OUT_DIR, "06_msx_clean.cas")
    TapeDecoder.save_msx_cas_file(msx_cas_path, b"TEST_MSX_BINARY_PAYLOAD_READY_FOR_EMULATOR")
    print(f"  [OK CAS] 06_msx_clean.cas                       (MSX BIOS blocks)")

if __name__ == "__main__":
    build_all_vectors()
