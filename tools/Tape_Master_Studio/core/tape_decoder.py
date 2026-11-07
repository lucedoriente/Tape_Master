"""
Tape Master Studio - Retrocomputing Tape Decoders & Converters
Supports .TAP, .TZX, .CSW, .PRG, and Kansas City standard decoding.
Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

import struct
from typing import List, Tuple, Dict, Any, Optional

class TapeDecoder:
    @staticmethod
    def parse_csw_file(filepath: str) -> Tuple[List[int], Dict[str, Any]]:
        """Parse a Compressed Square Wave (.CSW v2) file into pulse intervals (us)."""
        pulses = []
        info = {}

        with open(filepath, "rb") as f:
            magic = f.read(23)
            if not magic.startswith(b"Compressed Square Wave"):
                raise ValueError("Formato file CSW non valido")

            f.read(1) # 0x1A terminator
            major = struct.unpack("B", f.read(1))[0]
            minor = struct.unpack("B", f.read(1))[0]
            sample_rate = struct.unpack("<I", f.read(4))[0]
            total_pulses = struct.unpack("<I", f.read(4))[0]
            encoding = struct.unpack("B", f.read(1))[0]
            flags = struct.unpack("B", f.read(1))[0]
            f.read(3) # Reserved

            info = {
                "version": f"{major}.{minor}",
                "sample_rate": sample_rate,
                "total_pulses": total_pulses,
                "encoding": "RLE" if encoding == 1 else "ZRLE"
            }

            # Read RLE payload
            data = f.read()
            idx = 0
            dlen = len(data)

            while idx < dlen:
                byte_val = data[idx]
                idx += 1

                if byte_val != 0:
                    pulses.append(byte_val)
                else:
                    if idx + 4 <= dlen:
                        long_val = struct.unpack("<I", data[idx:idx+4])[0]
                        pulses.append(long_val)
                        idx += 4

        return pulses, info

    @staticmethod
    def save_csw_file(filepath: str, pulses_us: List[int], sample_rate: int = 1000000):
        """Save a list of pulse intervals in microseconds into a .CSW v2 file."""
        with open(filepath, "wb") as f:
            # Header (32 bytes)
            header = bytearray()
            header.extend(b"Compressed Square Wave\x1A")
            header.append(2)  # Major
            header.append(0)  # Minor
            header.extend(struct.pack("<I", sample_rate))
            header.extend(struct.pack("<I", len(pulses_us)))
            header.append(1)  # RLE
            header.append(0)  # Flags (start LOW)
            header.extend(b"\x00\x00\x00") # Reserved
            f.write(header)

            # RLE Data
            payload = bytearray()
            for p in pulses_us:
                if 1 <= p <= 255:
                    payload.append(p)
                else:
                    payload.append(0)
                    payload.extend(struct.pack("<I", p))
            f.write(payload)

    @staticmethod
    def decode_c64_pulses_to_bits(pulses_us: List[int], pal: bool = True) -> List[int]:
        """
        Decode raw pulse durations into Commodore C64 bits (Short/Medium/Long):
        - Short pulse + Medium pulse = Bit 0
        - Medium pulse + Short pulse = Bit 1
        """
        # PAL base ticks: Short ~352 us, Medium ~512 us, Long ~672 us
        s_min, s_max = 240, 430
        m_min, m_max = 431, 590

        symbols = []
        for p in pulses_us:
            if s_min <= p <= s_max:
                symbols.append('S')
            elif m_min <= p <= m_max:
                symbols.append('M')
            else:
                symbols.append('L')

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

        return bits

    @staticmethod
    def bits_to_bytes(bits: List[int]) -> bytes:
        """Convert list of 0/1 bits to bytes (LSB-first standard)."""
        out = bytearray()
        for i in range(0, len(bits) - 7, 8):
            byte = 0
            for b in range(8):
                if bits[i + b]:
                    byte |= (1 << b)
            out.append(byte)
        return bytes(out)
