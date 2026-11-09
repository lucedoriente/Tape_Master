"""
Tape Master Studio - File Subsystem & Decoder Unit Tests
Validates CSW v2, C64 (.TAP/.PRG), Spectrum (.TAP/.TZX), MSX (.CAS),
Apple II (.BIN), and the forensic Blind Classifier across all platforms.
Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

import os
import sys
import tempfile
import unittest

# Ensure project root in sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.tape_decoder import TapeDecoder
from core.tape_classifier import TapeClassifier, CARTRIDGE_PROFILES
from core.dsp_engine import DspEngine

VECTORS_DIR = os.path.join(os.path.dirname(__file__), "vectors")

class TestTapeFileSubsystem(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    # -------------------------------------------------------------------------
    # 1. CSW v2 Standard Compliance & Round-Trip Tests
    # -------------------------------------------------------------------------
    def test_csw_v2_standard_roundtrip_rle(self):
        """Verify CSW v2 RLE encoding, official 52-byte header, and pulse round-trip."""
        test_pulses = [352, 512, 672, 1000, 200, 50, 4000, 10000]
        out_file = os.path.join(self.temp_dir.name, "test_rle.csw")

        TapeDecoder.save_csw_file(out_file, test_pulses, compression="RLE")

        # Verify header length
        with open(out_file, "rb") as f:
            hdr = f.read(52)
            self.assertEqual(len(hdr), 52)
            self.assertTrue(hdr.startswith(b"Compressed Square Wave\x1a"))
            self.assertEqual(hdr[23], 2)  # Major
            self.assertEqual(hdr[24], 0)  # Minor

        # Parse and verify pulses
        read_pulses, info = TapeDecoder.parse_csw_file(out_file)
        self.assertEqual(read_pulses, test_pulses)
        self.assertEqual(info["version"], "2.0")
        self.assertEqual(info["encoding"], "RLE")
        self.assertEqual(info["total_pulses"], len(test_pulses))

    def test_csw_v2_standard_roundtrip_zrle(self):
        """Verify CSW v2 Z-RLE (DEFLATE compressed) encoding and round-trip."""
        test_pulses = [208] * 500 + [416] * 200 + [208] * 300
        out_file = os.path.join(self.temp_dir.name, "test_zrle.csw")

        TapeDecoder.save_csw_file(out_file, test_pulses, compression="ZRLE")
        read_pulses, info = TapeDecoder.parse_csw_file(out_file)

        self.assertEqual(read_pulses, test_pulses)
        self.assertEqual(info["encoding"], "ZRLE")

    # -------------------------------------------------------------------------
    # 2. Commodore 64 (.TAP / .PRG) Tests
    # -------------------------------------------------------------------------
    def test_c64_tap_roundtrip(self):
        """Verify Commodore 64 .TAP format generation and parsing."""
        c64_pulses = [352, 512, 672, 352, 512, 2400]
        out_tap = os.path.join(self.temp_dir.name, "c64_test.tap")

        TapeDecoder.save_c64_tap_file(out_tap, c64_pulses, version=1)
        parsed_pulses, info = TapeDecoder.parse_c64_tap_file(out_tap)

        self.assertEqual(len(parsed_pulses), len(c64_pulses))
        self.assertEqual(info["version"], 1)
        # Check pulse timings are preserved within 1 tick (~8 us)
        for orig, parsed in zip(c64_pulses, parsed_pulses):
            self.assertAlmostEqual(orig, parsed, delta=9)

    def test_c64_rom_decode_and_prg(self):
        """Verify C64 ROM pulse train decoding to .PRG with 9-bit countdown framing."""
        csw_path = os.path.join(VECTORS_DIR, "01_c64_clean.csw")
        if not os.path.exists(csw_path):
            self.skipTest("Vector file not found")

        pulses, _ = TapeDecoder.parse_csw_file(csw_path)
        dec = TapeDecoder.decode_c64_pulses(pulses)

        self.assertEqual(dec["filename"], "TESTC64.PRG")
        self.assertEqual(dec["load_address"], "0x0801")
        self.assertTrue(dec["checksum_valid"])
        # PRG must start with load address 0x01, 0x08
        self.assertEqual(dec["payload_bytes"][:2], b"\x01\x08")

    # -------------------------------------------------------------------------
    # 3. Sinclair ZX Spectrum (.TAP / .TZX) Tests
    # -------------------------------------------------------------------------
    def test_spectrum_decode_tap_tzx(self):
        """Verify Sinclair Spectrum pulse train decoding and .TAP/.TZX saving."""
        csw_path = os.path.join(VECTORS_DIR, "04_spectrum_clean.csw")
        if not os.path.exists(csw_path):
            self.skipTest("Vector file not found")

        pulses, _ = TapeDecoder.parse_csw_file(csw_path)
        dec = TapeDecoder.decode_spectrum_pulses(pulses)

        self.assertEqual(dec["platform"], "Sinclair ZX Spectrum")
        self.assertEqual(dec["filename"], "SPECTRUM.TAP")
        self.assertGreaterEqual(dec["blocks_count"], 1)

        # Test TAP save and parse
        out_tap = os.path.join(self.temp_dir.name, "spec.tap")
        TapeDecoder.save_spectrum_tap_file(out_tap, dec["blocks"])
        blocks = TapeDecoder.parse_spectrum_tap_file(out_tap)
        self.assertEqual(len(blocks), dec["blocks_count"])
        self.assertEqual(blocks[0]["name"], "SPECTRUM")
        self.assertTrue(blocks[0]["checksum_valid"])

        # Test TZX save
        out_tzx = os.path.join(self.temp_dir.name, "spec.tzx")
        TapeDecoder.save_spectrum_tzx_file(out_tzx, dec["blocks"])
        with open(out_tzx, "rb") as f:
            magic = f.read(10)
            self.assertEqual(magic, b"ZXTape!\x1A\x01\x14")

    # -------------------------------------------------------------------------
    # 4. MSX Kansas City FSK Tests
    # -------------------------------------------------------------------------
    def test_msx_fsk_decode_and_cas(self):
        """Verify Kansas City 1200 baud FSK demodulation and MSX BIOS headers."""
        csw_path = os.path.join(VECTORS_DIR, "06_msx_fsk_clean.csw")
        if not os.path.exists(csw_path):
            self.skipTest("Vector file not found")

        pulses, _ = TapeDecoder.parse_csw_file(csw_path)
        dec = TapeDecoder.decode_fsk_pulses(pulses, baud_rate=1200)

        self.assertIn("MSX Standard", dec["platform"])
        self.assertEqual(dec["filename"], "MSX_GAME.CAS")
        self.assertIn(b"\x1F\xA6\xDE\xBA\xCC\x13", dec["payload_bytes"])
        self.assertIn(b"TESTMSX", dec["payload_bytes"])

    # -------------------------------------------------------------------------
    # 5. Apple II Zero-Crossing Tests
    # -------------------------------------------------------------------------
    def test_apple2_decode(self):
        """Verify Apple II 770 Hz pilot and 1 kHz / 2 kHz cycle counting."""
        csw_path = os.path.join(VECTORS_DIR, "10_apple2_clean.csw")
        if not os.path.exists(csw_path):
            self.skipTest("Vector file not found")

        pulses, _ = TapeDecoder.parse_csw_file(csw_path)
        dec = TapeDecoder.decode_apple2_pulses(pulses)

        self.assertEqual(dec["platform"], "Apple II")
        self.assertEqual(dec["filename"], "APPLE2_DUMP.BIN")
        self.assertIn(b"APPLE2 CASSETTE DUMP", dec["payload_bytes"])

    # -------------------------------------------------------------------------
    # 6. Forensic Blind Ingestion & Degraded Signal Robustness
    # -------------------------------------------------------------------------
    def test_degraded_c64_tape_recovery(self):
        """Verify degraded C64 tape with +/- 6.5% Wow & Flutter is correctly recognized."""
        csw_path = os.path.join(VECTORS_DIR, "01_c64_degraded_jitter_flutter.csw")
        if not os.path.exists(csw_path):
            self.skipTest("Vector file not found")

        pulses, _ = TapeDecoder.parse_csw_file(csw_path)
        cls = TapeClassifier.classify_pulses(pulses)

        self.assertEqual(cls["primary_platform"], "01_C64")
        self.assertGreater(cls["confidence"], 60.0)
        self.assertGreater(cls["wow_flutter_wrms"], 3.0)

    def test_audio_noise_rejection(self):
        """Verify non-digital audio or random noise is rejected with UNKNOWN result."""
        csw_path = os.path.join(VECTORS_DIR, "99_audio_noise_reject.csw")
        if not os.path.exists(csw_path):
            self.skipTest("Vector file not found")

        pulses, _ = TapeDecoder.parse_csw_file(csw_path)
        cls = TapeClassifier.classify_pulses(pulses)

        self.assertEqual(cls["primary_platform"], "UNKNOWN")
        self.assertEqual(cls["confidence"], 0.0)

    # -------------------------------------------------------------------------
    # 7. Multi-Pass Forensic Recovery Tests
    # -------------------------------------------------------------------------
    def test_c64_multipass_recovery(self):
        """Verify merging multiple degraded passes heals all dropouts and recovers valid PRG."""
        pass_files = [
            os.path.join(VECTORS_DIR, f"01_c64_degraded_pass{i}.csw")
            for i in range(1, 6)
        ]
        passes = []
        for pth in pass_files:
            if not os.path.exists(pth):
                self.skipTest("Multi-pass vector file not found")
            p_list, _ = TapeDecoder.parse_csw_file(pth)
            passes.append(p_list)

        # Merge passes
        merged_pulses, stats = DspEngine.merge_pulse_passes(passes)
        self.assertEqual(stats["passes_used"], 5)
        self.assertGreater(stats["dropouts_fixed"], 0)

        # Max pulse in merged stream must be normal C64 Long pulse (< 750 us), not a dropout (> 2500 us)
        self.assertLess(max(merged_pulses), 800)

        # Decode reconstructed stream
        dec = TapeDecoder.decode_c64_pulses(merged_pulses)
        self.assertEqual(dec["filename"], "TESTC64.PRG")
        self.assertEqual(dec["load_address"], "0x0801")
        self.assertTrue(dec["checksum_valid"])

if __name__ == "__main__":
    unittest.main()
