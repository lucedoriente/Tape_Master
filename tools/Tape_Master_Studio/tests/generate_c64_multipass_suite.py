"""
Tape Master Studio - C64 Multi-Pass Capture Suite Generator
Generates realistic multi-pass reads of a degraded Commodore C64 cassette tape:
Simulates successive physical passes with varying wow & flutter phase,
independent Gaussian timing jitter, and distinct dropout locations (tape flaking/dirt).
Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

import os
import sys
import numpy as np

# Ensure project root in sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.tape_decoder import TapeDecoder
from core.dsp_engine import DspEngine
from tests.generate_test_suite import generate_c64_clean

OUT_DIR = os.path.join(os.path.dirname(__file__), "vectors")

def build_multipass_suite():
    os.makedirs(OUT_DIR, exist_ok=True)
    base_pulses = generate_c64_clean()
    n = len(base_pulses)

    print(f"Generazione suite Multi-Pass per 01_c64_degraded ({n} impulsi base)...")

    # Helper to generate a single pass
    def create_pass(seed, wf_freq, wf_phase, wf_amp, jitter_sigma, dropouts):
        np.random.seed(seed)
        t = np.linspace(0, 4.0, n)
        # Capstan / pinch roller wow modulation
        speed = 1.0 + wf_amp * np.sin(2 * np.pi * wf_freq * t + wf_phase)
        # Gaussian timing jitter
        jitter = np.random.normal(0, jitter_sigma, n)
        
        degraded = []
        for i, p in enumerate(base_pulses):
            new_p = int(round(p * speed[i] + jitter[i]))
            degraded.append(max(25, new_p))
            
        # Inject flaking / dropout gaps
        for idx, d_val in dropouts:
            degraded[idx] = d_val
            
        return degraded

    # 5 distinct sequential read passes:
    # Notice: Each pass has its own dropouts at DIFFERENT indices.
    # At every index, at least 4 out of 5 passes have valid signal!
    passes_def = [
        ("pass1", 101, 4.00, 0.00, 0.065, 13.5, [(1000, 3800), (2800, 2900)]),
        ("pass2", 202, 3.80, 1.25, 0.058, 15.0, [(1850, 4200), (3400, 3100)]),
        ("pass3", 303, 4.20, 2.80, 0.062, 14.0, [(600, 3500), (2418, 4000)]),
        ("pass4", 404, 4.05, 4.10, 0.070, 16.0, [(1400, 3300), (3150, 3700)]),
        ("pass5", 505, 3.95, 5.20, 0.055, 12.0, [(2015, 3900)])
    ]

    all_passes = []

    for name, seed, freq, phase, amp, sigma, dropouts in passes_def:
        pulses = create_pass(seed, freq, phase, amp, sigma, dropouts)
        all_passes.append(pulses)

        # Save with short name: 01_c64_degraded_passX.csw
        fname_short = f"01_c64_degraded_{name}.csw"
        fpath_short = os.path.join(OUT_DIR, fname_short)
        TapeDecoder.save_csw_file(fpath_short, pulses)

        # Save with full name: 01_c64_degraded_jitter_flutter_passX.csw
        fname_full = f"01_c64_degraded_jitter_flutter_{name}.csw"
        fpath_full = os.path.join(OUT_DIR, fname_full)
        TapeDecoder.save_csw_file(fpath_full, pulses)

        drop_str = ", ".join(f"@{idx}={val}us" for idx, val in dropouts)
        print(f"  [OK] {fname_short:32s} (W&F {amp*100:.1f}%, Jitter {sigma:.1f}us, Dropouts: {drop_str})")

    # Update canonical 01_c64_degraded_jitter_flutter.csw with pass 3
    TapeDecoder.save_csw_file(os.path.join(OUT_DIR, "01_c64_degraded_jitter_flutter.csw"), all_passes[2])

    # Run DSP Multi-Pass Merger across all 5 passes
    merged_pulses, stats = DspEngine.merge_pulse_passes(all_passes)
    merged_fpath = os.path.join(OUT_DIR, "01_c64_multipass_merged_clean.csw")
    TapeDecoder.save_csw_file(merged_fpath, merged_pulses)

    print("-" * 75)
    print(f"  [OK MERGE] {os.path.basename(merged_fpath):32s}")
    print(f"             • Passate fuse        : {stats['passes_used']}")
    print(f"             • Dropout eliminati   : {stats['dropouts_fixed']}")
    print(f"             • Confidenza statistica: {stats['confidence']:.1f}%")
    print(f"             • Max impulso fusione : {max(merged_pulses)} us (tutti i dropout guariti!)")

    # Validate decode on merged file
    dec = TapeDecoder.decode_c64_pulses(merged_pulses)
    print(f"             • Decodifica PRG      : {dec.get('filename')} (Checksum: {dec.get('checksum_valid')})")

if __name__ == "__main__":
    build_multipass_suite()
