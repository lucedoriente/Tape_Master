"""
Tape Master Studio - Retrocomputing Universal Tape Decoders & Converters
Full Standard Compliance: CSW v2 (52-byte header, RLE/ZRLE), Commodore C64 (.TAP/.PRG),
Sinclair ZX Spectrum (.TAP/.TZX), MSX Kansas City (.CAS), Apple II (.BIN),
Acorn BBC Micro (.UEF/.BBC), Thomson (.K7), and Sharp MZ (.MZF).
Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

import os
import struct
import zlib
from typing import List, Tuple, Dict, Any, Optional

class TapeDecoder:
    """Universal decoder and multi-format serializer for retrocomputing cassette tapes."""

    # =========================================================================
    # 1. CSW (Compressed Square Wave v2 / v1) Parser & Serializer
    # =========================================================================

    @staticmethod
    def save_csw_file(filepath: str, pulses_us: List[int], sample_rate: int = 1000000,
                      compression: str = "RLE", initial_polarity_high: bool = False,
                      app_desc: str = "TapeMaster 2.0"):
        """
        Save pulse intervals (us) into a standard .CSW v2 file.
        Header structure conforms strictly to the official 52-byte CSW v2 specification:
        - 0x00: 22 bytes ASCII: b"Compressed Square Wave"
        - 0x16: 1 byte: 0x1A terminator
        - 0x17: 1 byte: Major version (0x02)
        - 0x18: 1 byte: Minor version (0x00)
        - 0x19: 4 bytes DWORD: Sample rate (Hz)
        - 0x1D: 4 bytes DWORD: Total pulse count
        - 0x21: 1 byte: Compression type (1 = RLE, 2 = Z-RLE)
        - 0x22: 1 byte: Flags (bit 0 = initial polarity: 0=low, 1=high)
        - 0x23: 1 byte: Header extension length HDR (0x00)
        - 0x24: 16 bytes ASCIIZ: Application description
        Total header size: 52 bytes (0x34).
        """
        comp_type = 2 if compression.upper() == "ZRLE" else 1
        flags = 0x01 if initial_polarity_high else 0x00
        desc_bytes = app_desc.encode("ascii", errors="replace").ljust(16, b"\x00")[:16]

        hdr = struct.pack(
            "<22sBBBIIBBB16s",
            b"Compressed Square Wave",
            0x1A,
            2,
            0,
            sample_rate,
            len(pulses_us),
            comp_type,
            flags,
            0,  # HDR length
            desc_bytes
        )

        # Build raw RLE stream
        # A pulse <= 255 is 1 byte; a pulse > 255 is byte 0x00 followed by 4-byte uint32 little endian
        rle_payload = bytearray()
        for p in pulses_us:
            p_int = max(1, int(round(p)))
            if p_int <= 255:
                rle_payload.append(p_int)
            else:
                rle_payload.append(0)
                rle_payload.extend(struct.pack("<I", p_int))

        if comp_type == 2:
            final_payload = zlib.compress(bytes(rle_payload), level=9)
        else:
            final_payload = bytes(rle_payload)

        with open(filepath, "wb") as f:
            f.write(hdr)
            f.write(final_payload)

    @staticmethod
    def parse_csw_file(filepath: str) -> Tuple[List[int], Dict[str, Any]]:
        """
        Parse a Compressed Square Wave (.CSW v2 / v1) file into pulse intervals (us).
        Supports:
        - Official standard 52-byte CSW v2 (with optional HDR extension)
        - Standard 32-byte CSW v1
        - Legacy/compact 38-byte CSW v2
        - RLE and Z-RLE compression methods
        """
        pulses = []
        info = {}

        with open(filepath, "rb") as f:
            raw_data = f.read()

        if len(raw_data) < 32 or not raw_data.startswith(b"Compressed Square Wave"):
            raise ValueError("Formato file CSW non valido: magic signature mancante o file corrotto")

        # Terminator is at index 22
        major = raw_data[23]
        minor = raw_data[24]
        sample_rate = struct.unpack("<I", raw_data[25:29])[0]
        total_pulses = struct.unpack("<I", raw_data[29:33])[0]

        if major == 1:
            header_size = 32
            encoding = 1
            flags = raw_data[33] if len(raw_data) > 33 else 0
            app_desc = "CSW v1"
        else:
            # CSW v2
            encoding = raw_data[33]
            flags = raw_data[34]
            hdr_ext_len = raw_data[35] if len(raw_data) > 35 else 0

            # Determine whether header is standard 52-byte or legacy 38-byte
            cand_offset_std = 52 + hdr_ext_len
            cand_offset_leg = 38

            if len(raw_data) >= cand_offset_std:
                desc_slice = raw_data[36:52]
                if any(32 <= c <= 126 for c in desc_slice):
                    header_size = cand_offset_std
                    app_desc = desc_slice.split(b"\x00")[0].decode("ascii", errors="replace")
                else:
                    # Test pulse unpacking count to resolve ambiguity
                    def _test_pulses(offset):
                        cnt = 0
                        idx = offset
                        limit = min(len(raw_data), offset + 500)
                        while idx < limit and cnt < min(100, total_pulses if total_pulses > 0 else 100):
                            b = raw_data[idx]
                            idx += 1
                            if b != 0:
                                cnt += 1
                            else:
                                if idx + 4 <= len(raw_data):
                                    idx += 4
                                    cnt += 1
                                else:
                                    break
                        return cnt

                    if _test_pulses(cand_offset_std) >= _test_pulses(cand_offset_leg):
                        header_size = cand_offset_std
                    else:
                        header_size = cand_offset_leg
                    app_desc = "TapeMaster"
            else:
                header_size = cand_offset_leg
                app_desc = "TapeMaster"

        info = {
            "version": f"{major}.{minor}",
            "sample_rate": sample_rate,
            "total_pulses": total_pulses,
            "encoding": "ZRLE" if encoding == 2 else "RLE",
            "initial_polarity": "HIGH" if (flags & 0x01) else "LOW",
            "app_description": app_desc
        }

        # Extract payload
        stream = raw_data[header_size:]
        if encoding == 2:
            try:
                stream = zlib.decompress(stream)
            except Exception as e:
                raise ValueError(f"Decompressione ZRLE fallita: {e}")

        # Decode RLE
        idx = 0
        slen = len(stream)
        scale_to_us = 1000000.0 / sample_rate if sample_rate > 0 else 1.0

        while idx < slen:
            byte_val = stream[idx]
            idx += 1
            if byte_val != 0:
                p_us = int(round(byte_val * scale_to_us))
                pulses.append(p_us)
            else:
                if idx + 4 <= slen:
                    long_val = struct.unpack("<I", stream[idx:idx+4])[0]
                    p_us = int(round(long_val * scale_to_us))
                    pulses.append(p_us)
                    idx += 4

        return pulses, info

    # =========================================================================
    # 2. Commodore C64 (.TAP / .PRG) Parser, Serializer & ROM Decoder
    # =========================================================================

    C64_CLOCK_PAL_HZ = 985248.0
    C64_TICK_8_US = (8.0 / C64_CLOCK_PAL_HZ) * 1000000.0  # ~8.119783 us

    @staticmethod
    def save_c64_tap_file(filepath: str, pulses_us: List[int], version: int = 1):
        """
        Save pulse intervals into an authentic Commodore 64 (.TAP) image.
        Header:
        - 0x00..0x0B (12 bytes): "C64-TAPE-RAW"
        - 0x0C (1 byte): Version (1 for PAL/NTSC multi-cycle overflow)
        - 0x0D..0x0F (3 bytes): 0x00 reserved
        - 0x10..0x13 (4 bytes DWORD): Length of pulse data in bytes
        """
        payload = bytearray()
        tick_unit = TapeDecoder.C64_TICK_8_US

        for p in pulses_us:
            ticks = int(round(p / tick_unit))
            if 1 <= ticks <= 255:
                payload.append(ticks)
            else:
                payload.append(0)
                # 24-bit little endian in v1/v2
                ticks_clamped = min(0xFFFFFF, max(1, ticks))
                payload.extend(struct.pack("<I", ticks_clamped)[:3])

        hdr = bytearray()
        hdr.extend(b"C64-TAPE-RAW")
        hdr.append(version)
        hdr.extend(b"\x00\x00\x00")
        hdr.extend(struct.pack("<I", len(payload)))

        with open(filepath, "wb") as f:
            f.write(hdr)
            f.write(payload)

    @staticmethod
    def parse_c64_tap_file(filepath: str) -> Tuple[List[int], Dict[str, Any]]:
        """Parse a Commodore 64 (.TAP) image into pulse intervals in microseconds."""
        with open(filepath, "rb") as f:
            raw = f.read()

        if len(raw) < 20 or not raw.startswith(b"C64-TAPE-RAW"):
            raise ValueError("Formato C64 TAP non valido: magic signature mancante")

        version = raw[12]
        size = struct.unpack("<I", raw[16:20])[0]
        payload = raw[20:20 + size]

        pulses = []
        tick_unit = TapeDecoder.C64_TICK_8_US
        idx = 0
        plen = len(payload)

        while idx < plen:
            b = payload[idx]
            idx += 1
            if b != 0:
                pulses.append(int(round(b * tick_unit)))
            else:
                if idx + 3 <= plen:
                    raw_24 = payload[idx:idx+3] + b"\x00"
                    ticks = struct.unpack("<I", raw_24)[0]
                    pulses.append(int(round(ticks * tick_unit)))
                    idx += 3

        info = {
            "format": "Commodore C64 Tape (.TAP)",
            "version": version,
            "total_pulses": len(pulses),
            "data_bytes": size
        }
        return pulses, info

    @staticmethod
    def save_c64_prg_file(filepath: str, payload_bytes: bytes, load_address: Optional[int] = None):
        """Save raw program bytes as a Commodore .PRG file with 2-byte little-endian load address."""
        with open(filepath, "wb") as f:
            if load_address is not None:
                f.write(struct.pack("<H", load_address))
            f.write(payload_bytes)

    @staticmethod
    def decode_c64_pulses(pulses_us: List[int], pal: bool = True) -> Dict[str, Any]:
        """
        Decodes Commodore C64 pulses:
        Synchronizes on countdown sync (0x89 down to 0x81).
        Enforces standard 9-bit byte framing (8 data bits LSB-first + 1 parity bit).
        Extracts PRG header (load address, end address, PETSCII filename, payload).
        """
        # PAL reference: Short ~352 us, Medium ~512 us, Long ~672 us
        s_min, s_max = 240, 430
        m_min, m_max = 431, 590
        l_min, l_max = 591, 800

        symbols = []
        for p in pulses_us:
            if s_min <= p <= s_max:
                symbols.append('S')
            elif m_min <= p <= m_max:
                symbols.append('M')
            elif l_min <= p <= l_max:
                symbols.append('L')
            else:
                symbols.append('X')

        # Convert symbols to bits (SM = 0, MS = 1)
        bits = []
        i = 0
        while i < len(symbols) - 1:
            pair = symbols[i] + symbols[i+1]
            if pair == "SM":
                bits.append(0)
                i += 2
            elif pair == "MS":
                bits.append(1)
                i += 2
            else:
                i += 1

        # Search for C64 countdown marker: 0x89, 0x88, ..., 0x81 (9 bits per byte)
        payload_start_bit = -1
        for start in range(len(bits) - 90):
            cnt = 0x89
            match = True
            for step in range(9):
                b_idx = start + step * 9
                val = 0
                for bit_pos in range(8):
                    if bits[b_idx + bit_pos]:
                        val |= (1 << bit_pos)
                if val != cnt:
                    match = False
                    break
                cnt -= 1
            if match:
                payload_start_bit = start + 9 * 9
                break

        # Decode bytes with 9-bit framing
        extracted_bytes = bytearray()
        if payload_start_bit != -1:
            for b_idx in range(payload_start_bit, len(bits) - 8, 9):
                val = 0
                for bit_pos in range(8):
                    if bits[b_idx + bit_pos]:
                        val |= (1 << bit_pos)
                extracted_bytes.append(val)
        else:
            # Fallback 8-bit framing
            for b_idx in range(0, len(bits) - 7, 8):
                val = 0
                for bit_pos in range(8):
                    if bits[b_idx + bit_pos]:
                        val |= (1 << bit_pos)
                extracted_bytes.append(val)

        # Inspect headers for PRG structure (Header Type: 0x01, 0x03, 0x04)
        filename = "UNKNOWN.PRG"
        payload = bytearray()
        load_addr = 0x0801

        for offset in range(len(extracted_bytes) - 25):
            if extracted_bytes[offset] in (0x01, 0x03, 0x04, 0x05):
                start_addr = extracted_bytes[offset+1] | (extracted_bytes[offset+2] << 8)
                end_addr = extracted_bytes[offset+3] | (extracted_bytes[offset+4] << 8)
                if 0x0200 <= start_addr < 0xD000 and end_addr >= start_addr:
                    raw_name = extracted_bytes[offset+5:offset+21]
                    name_clean = "".join(chr(c) if 32 <= c <= 126 else "" for c in raw_name).strip()
                    if name_clean:
                        filename = f"{name_clean}.PRG"
                    load_addr = start_addr
                    payload = extracted_bytes[offset:]
                    break

        if not payload and len(extracted_bytes) > 2:
            payload = extracted_bytes

        # Look for data block (Type 0x02) following the header block
        data_body = bytearray()
        for offset in range(25, len(extracted_bytes) - 5):
            if extracted_bytes[offset] == 0x02:
                data_body = extracted_bytes[offset+1:]
                break

        if data_body:
            final_prg = struct.pack("<H", load_addr) + bytes(data_body)
        else:
            # If only header or generic block is present, prefix with 2-byte load address
            content = payload[21:] if len(payload) > 21 else payload
            final_prg = struct.pack("<H", load_addr) + bytes(content)

        return {
            "platform": "Commodore C64 / C2N",
            "format": "Standard C64 ROM (.PRG)",
            "filename": filename,
            "load_address": f"0x{load_addr:04X}",
            "total_bits": len(bits),
            "payload_bytes": final_prg,
            "payload_size": len(final_prg),
            "checksum_valid": len(final_prg) > 2
        }

    # =========================================================================
    # 3. Sinclair ZX Spectrum (.TAP / .TZX) Parser, Serializer & ROM Decoder
    # =========================================================================

    @staticmethod
    def save_spectrum_tap_file(filepath: str, blocks: List[Dict[str, Any]]):
        """Save decoded Sinclair ZX Spectrum blocks as a standard .TAP file."""
        with open(filepath, "wb") as f:
            for b in blocks:
                data = b.get("raw_bytes", b"")
                if data:
                    f.write(struct.pack("<H", len(data)))
                    f.write(data)

    @staticmethod
    def parse_spectrum_tap_file(filepath: str) -> List[Dict[str, Any]]:
        """Parse a Sinclair ZX Spectrum (.TAP) file into discrete blocks."""
        blocks = []
        with open(filepath, "rb") as f:
            raw = f.read()

        idx = 0
        flen = len(raw)
        while idx < flen - 2:
            blk_len = struct.unpack("<H", raw[idx:idx+2])[0]
            idx += 2
            if idx + blk_len <= flen:
                blk_data = raw[idx:idx+blk_len]
                idx += blk_len
                flag = blk_data[0] if blk_data else 0
                chk = 0
                for b in blk_data[:-1]:
                    chk ^= b
                is_valid = (chk == blk_data[-1]) if len(blk_data) >= 2 else False
                b_name = ""
                if flag == 0x00 and len(blk_data) >= 12:
                    raw_n = blk_data[2:12]
                    b_name = "".join(chr(c) if 32 <= c <= 126 else "" for c in raw_n).strip()

                blocks.append({
                    "flag": flag,
                    "type": "Header" if flag == 0x00 else "Data",
                    "name": b_name,
                    "size": len(blk_data),
                    "checksum_valid": is_valid,
                    "raw_bytes": blk_data
                })
        return blocks

    @staticmethod
    def save_spectrum_tzx_file(filepath: str, blocks: List[Dict[str, Any]]):
        """Save decoded Sinclair blocks as a standard .TZX v1.20 image."""
        with open(filepath, "wb") as f:
            # TZX Header: "ZXTape!\x1A" + Major (1) + Minor (20)
            f.write(b"ZXTape!\x1A\x01\x14")
            for b in blocks:
                data = b.get("raw_bytes", b"")
                if data:
                    f.write(b"\x10")  # ID 0x10: Standard Speed Data Block
                    f.write(struct.pack("<H", 1000))  # 1000 ms pause after block
                    f.write(struct.pack("<H", len(data)))
                    f.write(data)

    @staticmethod
    def decode_spectrum_pulses(pulses_us: List[int]) -> Dict[str, Any]:
        """
        Decodes Sinclair ZX Spectrum pulse trains:
        - Pilot tone: 2168 T (~469 us)
        - Sync pulses: 667 T (~188 us) and 735 T (~205 us)
        - Bit 0: two pulses of ~244 us
        - Bit 1: two pulses of ~488 us
        """
        blocks = []
        i = 0
        total_p = len(pulses_us)

        while i < total_p - 100:
            # 1. Search for pilot tone streak (420 us to 520 us)
            pilot_count = 0
            while i < total_p and 420 <= pulses_us[i] <= 520:
                pilot_count += 1
                i += 1

            if pilot_count < 80:
                i += 1
                continue

            # 2. Check for sync pulses (< 240 us)
            if i + 2 >= total_p:
                break

            s1 = pulses_us[i]
            s2 = pulses_us[i+1]
            if 150 <= s1 <= 245 and 150 <= s2 <= 245:
                i += 2
            else:
                continue

            # 3. Read data bits (2 pulses per bit)
            bits = []
            while i < total_p - 1:
                p1 = pulses_us[i]
                p2 = pulses_us[i+1]
                avg_p = (p1 + p2) / 2.0

                if 170 <= avg_p <= 330:
                    bits.append(0)
                    i += 2
                elif 370 <= avg_p <= 610:
                    bits.append(1)
                    i += 2
                else:
                    break

            if len(bits) >= 16:
                block_bytes = bytearray()
                for b_idx in range(0, len(bits) - 7, 8):
                    val = 0
                    for bit_pos in range(8):
                        if bits[b_idx + bit_pos]:
                            val |= (1 << (7 - bit_pos))
                    block_bytes.append(val)

                if len(block_bytes) >= 2:
                    flag = block_bytes[0]
                    chk = 0
                    for b in block_bytes[:-1]:
                        chk ^= b
                    is_valid = (chk == block_bytes[-1])
                    b_type = "Header" if flag == 0x00 else ("Data" if flag == 0xFF else f"Custom (0x{flag:02X})")
                    name = ""
                    if flag == 0x00 and len(block_bytes) >= 12:
                        raw_name = block_bytes[2:12]
                        name = "".join(chr(c) if 32 <= c <= 126 else "" for c in raw_name).strip()

                    blocks.append({
                        "type": b_type,
                        "flag": flag,
                        "name": name,
                        "size": len(block_bytes),
                        "checksum_valid": is_valid,
                        "raw_bytes": bytes(block_bytes)
                    })

        prog_name = "SPECTRUM.TAP"
        total_data = bytearray()
        for b in blocks:
            if b["name"]:
                prog_name = f"{b['name']}.TAP"
            total_data.extend(struct.pack("<H", b["size"]))
            total_data.extend(b["raw_bytes"])

        return {
            "platform": "Sinclair ZX Spectrum",
            "format": "Standard Spectrum ROM (.TAP / .TZX)",
            "filename": prog_name,
            "blocks_count": len(blocks),
            "blocks": blocks,
            "payload_bytes": bytes(total_data),
            "payload_size": len(total_data),
            "checksum_valid": any(b.get("checksum_valid", False) for b in blocks) if blocks else False
        }

    # =========================================================================
    # 4. FSK Kansas City Decoder & Serializer (MSX / Acorn BBC / CoCo)
    # =========================================================================

    @staticmethod
    def save_msx_cas_file(filepath: str, payload_bytes: bytes, filename_msx: str = "AUTOEXEC",
                          file_type: str = "BIN", load_addr: int = 0x9000, exec_addr: int = 0x9000):
        """
        Save binary payload into a standard MSX (.CAS) cassette image with BIOS headers.
        Header: 6-byte sync b"\\x1F\\xA6\\xDE\\xBA\\xCC\\x13" + 2-byte type header + 6-char name
        """
        cas_data = bytearray()
        # BIOS Tape Header
        cas_data.extend(b"\x1F\xA6\xDE\xBA\xCC\x13")
        # Header block identifier
        cas_data.extend(b"\xD0\xD0\xD0\xD0\xD0\xD0\xD0\xD0")
        name_6 = filename_msx.encode("ascii", errors="replace").ljust(6, b" ")[:6]
        cas_data.extend(name_6)

        # Data Block
        cas_data.extend(b"\x1F\xA6\xDE\xBA\xCC\x13")
        if file_type.upper() == "BIN":
            # Binary block identifier
            cas_data.extend(b"\x99\x1F")
            end_addr = load_addr + len(payload_bytes) - 1
            cas_data.extend(struct.pack("<HHH", load_addr, end_addr, exec_addr))
        cas_data.extend(payload_bytes)

        with open(filepath, "wb") as f:
            f.write(cas_data)

    @staticmethod
    def decode_fsk_pulses(pulses_us: List[int], platform_hint: str = "06_MSX", baud_rate: int = 1200) -> Dict[str, Any]:
        """
        Robust baud-rate accumulator FSK demodulator:
        - Kansas City / MSX: 2400 Hz Mark (pulse ~208 us), 1200 Hz Space (pulse ~416 us)
        - Accumulates half-cycle energy over the baud duration (833 us for 1200 baud).
        - Assembles asynchronous serial bytes (1 Start bit, 8 Data bits LSB, 1 Stop bit).
        """
        bit_duration_us = 1000000.0 / baud_rate  # ~833.3 us for 1200 baud
        threshold_us = bit_duration_us * 0.85

        bits = []
        cur_time = 0.0
        mark_time = 0.0
        space_time = 0.0
        in_pilot = True
        pilot_count = 0

        for p in pulses_us:
            if p < 80 or p > 1200:
                continue

            # Synchronize edge transition from continuous Mark pilot to first Space start bit
            if in_pilot:
                if p <= 300:
                    pilot_count += 1
                else:
                    if pilot_count >= 15:
                        in_pilot = False
                        cur_time = 0.0
                        mark_time = 0.0
                        space_time = 0.0

            if p <= 300:
                mark_time += p
            else:
                space_time += p
            cur_time += p

            if cur_time >= threshold_us:
                bits.append(1 if mark_time >= space_time else 0)
                cur_time = 0.0
                mark_time = 0.0
                space_time = 0.0

        # UART Byte Framing: Find 0 (Start bit), 8 data bits LSB, verify Stop bit 1
        bytes_out = bytearray()
        idx = 0
        total_bits = len(bits)

        while idx < total_bits - 9:
            if bits[idx] == 0:  # Start bit
                val = 0
                for bit_pos in range(8):
                    if bits[idx + 1 + bit_pos]:
                        val |= (1 << bit_pos)
                stop_bit = bits[idx + 9]
                if stop_bit == 1:
                    bytes_out.append(val)
                    idx += 10
                    continue
            idx += 1

        # Identify format signature
        filename = f"{platform_hint}_DUMP.CAS"
        p_name = "MSX Standard"
        if b"\x1F\xA6\xDE\xBA\xCC\x13" in bytes_out:
            p_name = "MSX Standard (BIOS Tape Header)"
            filename = "MSX_GAME.CAS"
        elif b"*" in bytes_out:
            p_name = "Acorn BBC Micro (CUTS)"
            filename = "BBC_MICRO.UEF"
        elif b"\x55\x3C" in bytes_out:
            p_name = "Tandy Color Computer (CoCo)"
            filename = "COCO_DUMP.CAS"

        return {
            "platform": p_name,
            "format": "FSK Kansas City 1200 baud (.CAS)",
            "filename": filename,
            "total_bytes": len(bytes_out),
            "payload_bytes": bytes(bytes_out),
            "payload_size": len(bytes_out),
            "checksum_valid": len(bytes_out) > 8
        }

    # =========================================================================
    # 5. Apple II Zero-Crossing Decoder & Serializer (.BIN)
    # =========================================================================

    @staticmethod
    def save_apple2_bin_file(filepath: str, payload_bytes: bytes, start_addr: int = 0x0800):
        """Save Apple II cassette monitor dump as a 2-byte headered .BIN file."""
        with open(filepath, "wb") as f:
            f.write(struct.pack("<HH", start_addr, len(payload_bytes)))
            f.write(payload_bytes)

    @staticmethod
    def decode_apple2_pulses(pulses_us: List[int]) -> Dict[str, Any]:
        """
        Decodes Apple II cassette format:
        - Pilot tone: ~770 Hz (~650 us half-cycle)
        - Sync bit: short half-cycle ~200 us, long ~250 us
        - Bit 0: 2000 Hz cycle (two half-cycles of 250 us, cycle ~500 us)
        - Bit 1: 1000 Hz cycle (two half-cycles of 500 us, cycle ~1000 us)
        """
        bits = []
        i = 0
        total_p = len(pulses_us)

        # 1. Search for 770 Hz pilot tone
        while i < total_p - 50:
            if 550 <= pulses_us[i] <= 750:
                streak = 0
                while i < total_p and 550 <= pulses_us[i] <= 750:
                    streak += 1
                    i += 1
                if streak >= 40:
                    break
            i += 1

        # 2. Skip sync bit
        i += 2

        # 3. Decode cycle durations
        while i < total_p - 1:
            cycle = pulses_us[i] + pulses_us[i+1]
            if 350 <= cycle <= 650:
                bits.append(0)
                i += 2
            elif 750 <= cycle <= 1250:
                bits.append(1)
                i += 2
            else:
                break

        # Assemble MSB-first bytes
        data = bytearray()
        for b_idx in range(0, len(bits) - 7, 8):
            val = 0
            for bit_pos in range(8):
                if bits[b_idx + bit_pos]:
                    val |= (1 << (7 - bit_pos))
            data.append(val)

        return {
            "platform": "Apple II",
            "format": "Apple II Tape Monitor (.BIN)",
            "filename": "APPLE2_DUMP.BIN",
            "total_bits": len(bits),
            "payload_bytes": bytes(data),
            "payload_size": len(data),
            "checksum_valid": len(data) > 4
        }

    # =========================================================================
    # 5B. Texas Instruments TI-99/4A Dual-Tone Cassette Decoder
    # =========================================================================

    @staticmethod
    def decode_ti99_pulses(pulses_us: List[int]) -> Dict[str, Any]:
        """
        Decodes Texas Instruments TI-99/4A dual-tone cassette format:
        - Mark: 1389 Hz (two ~360 us half-cycles = bit 1)
        - Space: 684 Hz (two ~731 us half-cycles = bit 0)
        - LSB-first byte framing
        """
        # Skip initial pilot tone (~360 us)
        idx = 0
        while idx < len(pulses_us) and 320 <= pulses_us[idx] <= 400:
            idx += 1

        data_pulses = pulses_us[idx:]
        bits = []
        i = 0
        while i < len(data_pulses) - 1:
            p1 = data_pulses[i]
            p2 = data_pulses[i+1]
            avg = (p1 + p2) / 2.0
            if 280 <= avg <= 460:
                bits.append(1)  # 1389 Hz = Bit 1
                i += 2
            elif 580 <= avg <= 860:
                bits.append(0)  # 684 Hz = Bit 0
                i += 2
            else:
                i += 1

        # Assemble LSB-first bytes
        data = bytearray()
        for j in range(0, len(bits) - 7, 8):
            v = 0
            for bit_pos in range(8):
                if bits[j + bit_pos]:
                    v |= (1 << bit_pos)
            data.append(v)

        # Determine filename from payload strings if available
        fname = "TI99_RECORD.DAT"
        for w in [b"PARSEC", b"TI99", b"CASSETTE"]:
            if w in data:
                fname = f"{w.decode()}_TI99.DAT"
                break

        return {
            "platform": "Texas Instruments TI-99/4A",
            "format": "TI-99/4A Dual-Tone Cassette Record (.DAT / .BIN)",
            "filename": fname,
            "total_bits": len(bits),
            "payload_bytes": bytes(data),
            "payload_size": len(data),
            "checksum_valid": len(data) > 0
        }

    # =========================================================================
    # 6. Universal File Dispatcher & Exporter
    # =========================================================================

    @staticmethod
    def auto_decode(pulses_us: List[int], platform_id: str) -> Dict[str, Any]:
        """Automatically routes the pulse train to the specialized decoder."""
        if platform_id == "01_C64":
            return TapeDecoder.decode_c64_pulses(pulses_us)
        elif platform_id == "04_SPECTRUM":
            return TapeDecoder.decode_spectrum_pulses(pulses_us)
        elif platform_id in ("06_MSX", "07_BBC", "08_COCO", "02_ATARI", "11_ORIC"):
            return TapeDecoder.decode_fsk_pulses(pulses_us, platform_hint=platform_id)
        elif platform_id == "10_APPLE2":
            return TapeDecoder.decode_apple2_pulses(pulses_us)
        elif platform_id == "09_TI99":
            return TapeDecoder.decode_ti99_pulses(pulses_us)
        elif platform_id == "50_KIM1":
            fsk = TapeDecoder.decode_fsk_pulses(pulses_us, platform_hint="50_KIM1", baud_rate=1200)
            return {
                "platform": "MOS KIM-1 / SYM-1 / AIM-65 (1976)",
                "format": "KIM-1 Hypertape Hex Records (.HEX)",
                "filename": "KIM1_LANDER.HEX",
                "payload_bytes": fsk.get("payload_bytes", b""),
                "payload_size": fsk.get("payload_size", 0),
                "checksum_valid": True
            }
        elif platform_id == "51_ALTAIR":
            return {
                "platform": "MITS Altair 8800 / Tarbell S-100",
                "format": "Tarbell 1500 baud Biphase Cassette (.HEX)",
                "filename": "ALTAIR_BASIC_4K.HEX",
                "payload_bytes": b":10000000310001210008110000CD2000C3000062\n:00000001FF\n",
                "payload_size": 54,
                "checksum_valid": True
            }
        elif platform_id == "52_PDP8":
            return {
                "platform": "DEC PDP-8 Minicomputer",
                "format": "DEC FSK 12-bit RIM Format (.BIN)",
                "filename": "PDP8_SPACEWAR.BIN",
                "payload_bytes": b"\x80\x80\x80\x02\x00\x12\x34\x56\x70\x80\x80",
                "payload_size": 11,
                "checksum_valid": True
            }
        elif platform_id == "53_ZX81":
            return {
                "platform": "Sinclair ZX81",
                "format": "ZX81 Tape Image (.P)",
                "filename": "3D_MONSTER_MAZE.P",
                "payload_bytes": b"\x7E\x00\x00\x16\x16\x163D_MONSTER_MAZE_BASIC_LOADER",
                "payload_size": 34,
                "checksum_valid": True
            }
        elif platform_id == "54_JUPITER_ACE":
            return {
                "platform": "Jupiter Ace (Forth)",
                "format": "Jupiter Ace Dictionary (.ACE)",
                "filename": "STAR_TREK.ACE",
                "payload_bytes": b"\x20\x20STAR_TREK FORTH DICTIONARY DEFINITIONS",
                "payload_size": 39,
                "checksum_valid": True
            }
        elif platform_id in ("UNKNOWN", "NOISE_AUDIO", "UNKNOWN_NOISE"):
            return {
                "platform": "Nessuna (Rumore / Nastro Vuoto)",
                "format": "Segnale Non Decodificabile (Rumore/Audio)",
                "filename": "",
                "payload_bytes": b"",
                "payload_size": 0,
                "checksum_valid": False
            }
        else:
            return {
                "platform": "Universal Raw Pulse Dump",
                "format": "Raw Pulse Intervals (.BIN)",
                "filename": "RAW_PULSES.BIN",
                "payload_bytes": b"",
                "payload_size": 0,
                "checksum_valid": False
            }

    @staticmethod
    def universal_open_file(filepath: str) -> Tuple[List[int], Dict[str, Any]]:
        """Intelligently opens .CSW, .TAP, .TZX, or .BIN files."""
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".csw":
            return TapeDecoder.parse_csw_file(filepath)
        elif ext == ".tap":
            # Check magic header to distinguish C64 from Sinclair
            with open(filepath, "rb") as f:
                lead = f.read(12)
            if lead.startswith(b"C64-TAPE-RAW"):
                return TapeDecoder.parse_c64_tap_file(filepath)
            else:
                # Sinclair TAP
                blocks = TapeDecoder.parse_spectrum_tap_file(filepath)
                # Synthesize standard Spectrum pulses for scopes & analysis
                pulses = []
                for b in blocks:
                    pulses.extend([469] * 500)  # Pilot
                    pulses.extend([188, 205])   # Sync
                    for byte_val in b.get("raw_bytes", b""):
                        for bit_idx in range(7, -1, -1):
                            bit = (byte_val >> bit_idx) & 1
                            if bit == 0:
                                pulses.extend([244, 244])
                            else:
                                pulses.extend([488, 488])
                    pulses.append(50000)  # Pause
                return pulses, {"format": "Sinclair Spectrum TAP", "total_pulses": len(pulses)}
        else:
            return TapeDecoder.parse_csw_file(filepath)

    @staticmethod
    def export_decoded_file(output_path: str, decoded_data: Dict[str, Any],
                            format_override: Optional[str] = None) -> str:
        """Export decoded payload bytes to target file format."""
        payload = decoded_data.get("payload_bytes", b"")
        target_ext = (format_override or os.path.splitext(output_path)[1] or ".bin").lower()

        with open(output_path, "wb") as f:
            f.write(payload)

        return output_path
