"""
Tape Master Studio - Blind Signal Analysis & Platform Classifier
Analyzes unknown pulse streams (.CSW / .TAP) to identify target retrocomputer platforms
across all 13 Tape Master hardware cartridge profiles.
Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

import numpy as np
from scipy.signal import find_peaks
from typing import List, Dict, Any, Tuple, Optional

# Definition of the 13 cartridge profiles and their acoustic/temporal signatures
CARTRIDGE_PROFILES = {
    "01_C64": {
        "name": "Commodore C64 / C2N Datassette",
        "family": "PWM / Interval",
        "cart_id": 1,
        "pilot_range": (330, 380),     # Short pulse continuous train
        "key_peaks": [352, 512, 672],  # Short, Medium, Long (PAL)
        "tolerance": 45,
        "description": "3 picchi distinti (~352 us, ~512 us, ~672 us), pilot train corto"
    },
    "02_ATARI": {
        "name": "Atari SIO (410 / 1010 / XC12)",
        "family": "FSK Tone / Serial",
        "cart_id": 2,
        "pilot_range": (170, 205),     # Mark tone 5327 Hz (~188 us)
        "key_peaks": [188, 250],       # Mark (5327 Hz) and Space (3995 Hz)
        "tolerance": 30,
        "description": "FSK bicanale (5327 Hz Mark / 3995 Hz Space), 600 baud"
    },
    "03_THOMSON": {
        "name": "Thomson MO5/TO7 / Olivetti PC128",
        "family": "FM (Frequency Modulation)",
        "cart_id": 3,
        "pilot_range": (210, 235),     # 4.5 kHz pilot (~222 us)
        "key_peaks": [159, 222],       # Bit 1 (6.3 kHz ~159 us) / Bit 0 (4.5 kHz ~222 us)
        "tolerance": 25,
        "description": "FM veloce a 4.5 kHz (bit 0) e 6.3 kHz (bit 1)"
    },
    "04_SPECTRUM": {
        "name": "Sinclair ZX Spectrum",
        "family": "Bipolar Zero-Crossing PWM",
        "cart_id": 4,
        "pilot_range": (450, 490),     # 2168 T-states (~469 us)
        "key_peaks": [244, 488],       # Bit 0 (855 T ~244 us) / Bit 1 (1710 T ~488 us)
        "tolerance": 35,
        "description": "Pilot lungo a 2168 T (~469 us), bit 0 (244 us), bit 1 (488 us)"
    },
    "05_AMSTRAD": {
        "name": "Amstrad CPC 464 / 664 / 6128",
        "family": "Pulse Width / Cycle",
        "cart_id": 5,
        "pilot_range": (730, 800),     # ~1300 Hz pilot (~769 us)
        "key_peaks": [250, 500],       # 1000/2000 baud half cycles
        "tolerance": 40,
        "description": "Pilot a ~1300 Hz, semionde da 250 us e 500 us"
    },
    "06_MSX": {
        "name": "MSX Standard (1200 / 2400 baud)",
        "family": "FSK Kansas City / Bell 202",
        "cart_id": 6,
        "pilot_range": (195, 220),     # Mark tone 2400 Hz (~208 us)
        "key_peaks": [208, 416],       # Mark (2400 Hz ~208 us) e Space (1200 Hz ~416 us)
        "tolerance": 35,
        "description": "FSK Kansas City: 2400 Hz Mark (2 cicli) / 1200 Hz Space (1 ciclo)"
    },
    "07_BBC": {
        "name": "Acorn BBC Micro / Electron",
        "family": "FSK CUTS / Kansas City",
        "cart_id": 7,
        "pilot_range": (195, 220),     # 2400 Hz pilot (~208 us)
        "key_peaks": [208, 416],       # 1200 Hz e 2400 Hz
        "tolerance": 35,
        "description": "CUTS 1200/300 baud FSK, preamble 2400 Hz con sync byte '*'"
    },
    "08_COCO": {
        "name": "Tandy TRS-80 Color Computer / Dragon 32",
        "family": "FSK Sine-Crossing",
        "cart_id": 8,
        "pilot_range": (390, 440),     # 1200 Hz / 2400 Hz
        "key_peaks": [208, 416],       # 1200 Hz / 2400 Hz
        "tolerance": 35,
        "description": "FSK a 1200/2400 Hz con sync byte 0x3C e alternanza 0x55"
    },
    "09_TI99": {
        "name": "Texas Instruments TI-99/4A",
        "family": "Dual Tone Audio",
        "cart_id": 9,
        "pilot_range": (340, 380),     # 1389 Hz pilot (~360 us)
        "key_peaks": [360, 731],       # Alta freq 1389 Hz (~360 us) / Bassa 684 Hz (~731 us)
        "tolerance": 50,
        "description": "Dual Tone a 684 Hz e 1389 Hz, blocchi fissi da 64/128 byte"
    },
    "10_APPLE2": {
        "name": "Apple II / II+ / IIe",
        "family": "Cycle Counting Zero-Crossing",
        "cart_id": 10,
        "pilot_range": (600, 700),     # ~770 Hz pilot (~650 us semionda)
        "key_peaks": [250, 500, 650],  # 2 kHz (250 us), 1 kHz (500 us), pilot (650 us)
        "tolerance": 45,
        "description": "Pilot 770 Hz (~650 us), semionda bit 0 (250 us), bit 1 (500 us)"
    },
    "11_ORIC": {
        "name": "Oric 1 / Atmos",
        "family": "FSK Fast/Slow",
        "cart_id": 11,
        "pilot_range": (195, 220),     # 2400 baud fast mode
        "key_peaks": [208, 416],       # 2400 baud (208 us / 416 us)
        "tolerance": 35,
        "description": "FSK veloce 2400 baud con firma di sincronismo 0x16 0x16 0x16 0x24"
    },
    "12_SHARP": {
        "name": "Sharp MZ-700 / MZ-800 / MZ-80K",
        "family": "Sharp PWM Fast",
        "cart_id": 12,
        "pilot_range": (210, 250),     # Short pulse pilot (~230 us)
        "key_peaks": [230, 460],       # Short pulse (230 us) / Long pulse (460 us)
        "tolerance": 35,
        "description": "PWM veloce 1200 baud, impulsi da 230 us (Short) e 460 us (Long)"
    },
    "13_RAW_HEAD": {
        "name": "Raw Head Stereo Digitizer",
        "family": "Direct Magnetic Flux",
        "cart_id": 13,
        "pilot_range": (0, 0),
        "key_peaks": [],
        "tolerance": 50,
        "description": "Cattura flusso magnetico grezzo senza filtraggio a monte"
    },
    "50_KIM1": {
        "name": "MOS KIM-1 / SYM-1 / AIM-65 (1976)",
        "family": "6502 Audio Cassette (Hypertape)",
        "cart_id": 50,
        "pilot_range": (195, 220),     # 2400 Hz pilot (~208 us)
        "key_peaks": [208, 416],
        "tolerance": 30,
        "description": "Formato KIM-1 1976: sync 0x16, record esadecimali ASCII a 2400/1200 Hz"
    },
    "51_ALTAIR": {
        "name": "MITS Altair 8800 / Tarbell S-100 (1976)",
        "family": "Biphase Cassette (8080)",
        "cart_id": 51,
        "pilot_range": (155, 180),     # 3000 Hz pilot (~167 us)
        "key_peaks": [167, 333],
        "tolerance": 25,
        "description": "Interfaccia Tarbell 1976 per Altair 8800 / IMSAI, 1500 baud biphase"
    },
    "52_PDP8": {
        "name": "DEC PDP-8 Minicomputer",
        "family": "DEC FSK Audio Cassette / RIM",
        "cart_id": 52,
        "pilot_range": (480, 520),     # 1000 Hz pilot (~500 us)
        "key_peaks": [250, 500],
        "tolerance": 30,
        "description": "Dump nastro/audio per minicomputer DEC PDP-8 a parole da 12 bit"
    },
    "53_ZX81": {
        "name": "Sinclair ZX81",
        "family": "Silence-Gap Burst PWM (Z80)",
        "cart_id": 53,
        "pilot_range": (145, 165),     # 3.25 kHz burst (~154 us)
        "key_peaks": [154],
        "tolerance": 25,
        "description": "Burst a 3.25 kHz con gap di silenzio da 1.3 ms, programmi BASIC ZX81"
    },
    "54_JUPITER_ACE": {
        "name": "Jupiter Ace (Forth)",
        "family": "Bipolar Ace PWM",
        "cart_id": 54,
        "pilot_range": (480, 515),     # 1008 Hz pilot (~496 us)
        "key_peaks": [248, 496],
        "tolerance": 30,
        "description": "Minicomputer Forth Jupiter Ace, pilot 1008 Hz, bit 0 (248 us), bit 1 (496 us)"
    }
}


class TapeClassifier:
    """
    Forensic classifier for digitized tape pulse streams.
    Detects platform, modulation family, wow/flutter, and polarity.
    """

    @staticmethod
    def classify_pulses(pulses_us: List[int], max_analyze: int = 50000) -> Dict[str, Any]:
        """
        Classify a sequence of pulse intervals in microseconds.
        
        Returns:
            Dict containing:
                - primary_platform: str (e.g. "04_SPECTRUM")
                - platform_name: str (e.g. "Sinclair ZX Spectrum")
                - family: str (e.g. "Bipolar Zero-Crossing PWM")
                - confidence: float (0.0 to 100.0)
                - detected_peaks: List[int] (pulse durations of histogram peaks)
                - pilot_pulse_us: Optional[int] (detected dominant pilot interval)
                - inverted_phase: bool (true if phase inversion detected)
                - wow_flutter_wrms: float (% speed drift)
                - all_matches: List[Tuple[str, float]]
        """
        if not pulses_us or len(pulses_us) < 100:
            return {
                "primary_platform": "UNKNOWN",
                "platform_name": "Segnale Insufficiente (< 100 impulsi)",
                "family": "Unknown",
                "confidence": 0.0,
                "detected_peaks": [],
                "pilot_pulse_us": None,
                "inverted_phase": False,
                "wow_flutter_wrms": 0.0,
                "all_matches": []
            }

        arr = np.array(pulses_us[:max_analyze], dtype=np.float32)
        
        # 1. Glitch and silence filter (valid tape pulses: 20 us to 2500 us)
        valid = arr[(arr >= 20.0) & (arr <= 2500.0)]
        if len(valid) < 80:
            return {
                "primary_platform": "NOISE_AUDIO",
                "platform_name": "Rumore o Traccia Audio non Digitale",
                "family": "Audio/Noise",
                "confidence": 0.0,
                "detected_peaks": [],
                "pilot_pulse_us": None,
                "inverted_phase": False,
                "wow_flutter_wrms": 0.0,
                "all_matches": []
            }

        # 2. Wow & Flutter calculation (WRMS %)
        w_size = min(300, len(valid) // 4)
        if w_size > 10:
            kernel = np.ones(w_size) / w_size
            m_avg = np.convolve(valid, kernel, mode='valid')
            mean_sp = np.mean(m_avg)
            dev = ((m_avg - mean_sp) / mean_sp) * 100.0 if mean_sp > 0 else np.zeros(1)
            wrms = float(np.sqrt(np.mean(dev ** 2)))
        else:
            wrms = 0.0

        # 3. Pulse Duration Histogram & Peak Detection with Flutter Smoothing
        hist_range = (20, 2000)
        bins = 396 # ~5 us resolution per bin
        counts, edges = np.histogram(valid, bins=bins, range=hist_range)
        bin_centers = (edges[:-1] + edges[1:]) / 2.0

        # Apply slight Gaussian smoothing to fuse split peaks caused by Wow & Flutter
        from scipy.ndimage import gaussian_filter1d
        counts_smooth = gaussian_filter1d(counts.astype(float), sigma=1.8)

        # Find significant peaks
        max_count = np.max(counts_smooth)
        min_height = max(12, int(max_count * 0.05)) # At least 5% of dominant peak
        peak_indices, properties = find_peaks(counts_smooth, height=min_height, distance=7, prominence=min_height * 0.3)
        
        detected_peaks = [int(round(bin_centers[idx])) for idx in peak_indices]
        detected_peaks.sort()

        # 4. Pilot Tone Detection (find longest continuous streak of nearly identical pulses)
        pilot_us, pilot_length = TapeClassifier._detect_pilot_tone(valid)

        # 5. Score Against All 13 Cartridge Profiles
        scores = {}
        for p_id, prof in CARTRIDGE_PROFILES.items():
            if p_id == "13_RAW_HEAD":
                continue # Generic profile, evaluated if others have low confidence
            score = TapeClassifier._evaluate_profile_score(
                prof, detected_peaks, pilot_us, pilot_length, valid
            )
            scores[p_id] = score

        # Kansas City / FSK Platform Disambiguation (MSX vs BBC vs Oric vs CoCo vs KIM-1)
        kc_group = ["06_MSX", "07_BBC", "11_ORIC", "08_COCO", "50_KIM1"]
        top_pre = max(scores.items(), key=lambda x: x[1])[0]
        if top_pre in kc_group and len(valid) > 200:
            # Check for signature bytes in FSK stream
            try:
                from core.tape_decoder import TapeDecoder
                # Test 1200 baud first
                d1200 = TapeDecoder.decode_fsk_pulses(valid[:2500].astype(int).tolist(), baud_rate=1200)
                pay1200 = d1200.get("payload_bytes", b"")
                detected_kc = None
                if b"\x1F\xA6\xDE\xBA\xCC\x13" in pay1200:
                    detected_kc = "06_MSX"
                elif b";" in pay1200:
                    detected_kc = "50_KIM1"
                elif b"*" in pay1200:
                    detected_kc = "07_BBC"
                elif b"\x55\x3C" in pay1200:
                    detected_kc = "08_COCO"
                else:
                    # Test 2400 baud (Oric 1)
                    d2400 = TapeDecoder.decode_fsk_pulses(valid[:2500].astype(int).tolist(), baud_rate=2400)
                    pay2400 = d2400.get("payload_bytes", b"")
                    if b"\x16\x16\x16\x24" in pay2400 or b"\x16\x16\x16" in pay2400:
                        detected_kc = "11_ORIC"
                    elif b"*" in pay2400:
                        detected_kc = "07_BBC"

                if detected_kc:
                    scores[detected_kc] = 99.0
                    for other_kc in kc_group:
                        if other_kc != detected_kc:
                            scores[other_kc] = min(scores[other_kc], 35.0)
            except Exception:
                pass

        # Minicomputer Disambiguation: DEC PDP-8 (RIM/BIN) vs Jupiter Ace (Forth PWM)
        top_pre = max(scores.items(), key=lambda x: x[1])[0]
        if top_pre in ("52_PDP8", "54_JUPITER_ACE") and len(valid) > 200:
            try:
                # Find Jupiter Ace sync pulses (two short ~248 us pulses following pilot)
                idx_a = 0
                while idx_a < min(1000, len(valid) - 2):
                    if 200 <= valid[idx_a] <= 290 and 200 <= valid[idx_a + 1] <= 290:
                        idx_a += 2
                        break
                    idx_a += 1

                ace_bits = []
                while idx_a < min(len(valid) - 1, idx_a + 800):
                    p1 = valid[idx_a]
                    p2 = valid[idx_a + 1]
                    avg_p = (p1 + p2) / 2.0
                    if 200 <= avg_p <= 300:
                        ace_bits.append(0)
                        idx_a += 2
                    elif 400 <= avg_p <= 600:
                        ace_bits.append(1)
                        idx_a += 2
                    else:
                        idx_a += 1

                ace_bytes = bytearray()
                for b_i in range(0, len(ace_bits) - 7, 8):
                    v = 0
                    for bit_p in range(8):
                        if ace_bits[b_i + bit_p]:
                            v |= (1 << (7 - bit_p))
                    ace_bytes.append(v)

                if b"FORTH" in ace_bytes or b"ACE" in ace_bytes:
                    scores["54_JUPITER_ACE"] = 98.0
                    scores["52_PDP8"] = min(scores["52_PDP8"], 30.0)
                else:
                    scores["52_PDP8"] = 90.0
                    scores["54_JUPITER_ACE"] = min(scores["54_JUPITER_ACE"], 30.0)
            except Exception:
                pass

        # Rank matches
        sorted_matches = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_id, best_score = sorted_matches[0]

        # Inverted Phase Check (for asymmetric duty-cycle platforms like C64 or Apple II)
        inverted_phase = False
        if best_id == "01_C64":
            # For C64, Short followed by Medium is bit 0, Medium then Short is bit 1.
            # If duty-cycle is inverted, ratio of SM vs MS or falling edge flips.
            inverted_phase = TapeClassifier._check_c64_phase_inversion(valid)

        # Confidence scaling
        confidence = min(99.9, max(0.0, best_score))
        if confidence < 35.0:
            best_id = "UNKNOWN"
            best_name = "Nastro Sconosciuto o Non Decodificato"
            best_fam = "Unknown"
            confidence = 0.0
        else:
            best_name = CARTRIDGE_PROFILES[best_id]["name"]
            best_fam = CARTRIDGE_PROFILES[best_id]["family"]

        return {
            "primary_platform": best_id,
            "platform_name": best_name,
            "family": best_fam,
            "confidence": round(confidence, 1),
            "detected_peaks": detected_peaks,
            "pilot_pulse_us": pilot_us,
            "pilot_length_pulses": pilot_length,
            "inverted_phase": inverted_phase,
            "wow_flutter_wrms": round(wrms, 2),
            "all_matches": [(k, round(v, 1)) for k, v in sorted_matches]
        }

    @staticmethod
    def _detect_pilot_tone(arr: np.ndarray, tolerance_us: float = 28.0) -> Tuple[Optional[int], int]:
        """Find the most prominent continuous pulse train of consistent duration."""
        if len(arr) < 50:
            return None, 0

        # Apply a 5-tap median filter to suppress single-pulse jitter and flutter glitches
        from scipy.ndimage import median_filter
        filtered_arr = median_filter(arr, size=5)
        diffs = np.abs(np.diff(filtered_arr))
        # Streak where adjacent pulses differ by less than tolerance
        stable_mask = (diffs < tolerance_us)

        max_streak_len = 0
        current_streak_len = 0
        best_streak_end = 0

        for i, is_stable in enumerate(stable_mask):
            if is_stable:
                current_streak_len += 1
                if current_streak_len > max_streak_len:
                    max_streak_len = current_streak_len
                    best_streak_end = i + 1
            else:
                current_streak_len = 0

        if max_streak_len >= 40:
            streak_start = best_streak_end - max_streak_len
            pilot_val = int(round(np.median(arr[streak_start:best_streak_end])))
            return pilot_val, max_streak_len

        return None, 0

    @staticmethod
    def _evaluate_profile_score(prof: Dict[str, Any], detected_peaks: List[int],
                                pilot_us: Optional[int], pilot_len: int,
                                pulses: np.ndarray) -> float:
        """Calculate matching probability score (0.0 to 100.0) for a given profile."""
        score = 0.0
        expected_peaks = prof["key_peaks"]
        tol = prof["tolerance"]

        # 1. Peak matching (up to 50 points)
        matched_peaks_count = 0
        for exp in expected_peaks:
            for det in detected_peaks:
                if abs(exp - det) <= tol:
                    matched_peaks_count += 1
                    break

        if len(expected_peaks) > 0:
            peak_ratio = matched_peaks_count / len(expected_peaks)
            score += peak_ratio * 50.0

        # Special case: C64 requires Short (~352 us) and Medium (~512 us) for high score
        if prof["cart_id"] == 1:
            has_s = any(abs(352 - det) <= tol for det in detected_peaks)
            has_m = any(abs(512 - det) <= tol for det in detected_peaks)
            if has_s and has_m:
                score += 20.0
            elif not has_s:
                score *= 0.3

        # Special case: TI-99/4A requires both High tone (~360 us) and Low tone (~731 us)
        if prof["cart_id"] == 9:
            has_low_tone = any(abs(731 - det) <= tol for det in detected_peaks)
            if not has_low_tone:
                score *= 0.25

        # Special case: Sharp MZ requires both Short (~230 us) and Long (~460 us)
        if prof["cart_id"] == 12:
            has_long = any(abs(460 - det) <= tol for det in detected_peaks)
            if not has_long:
                score *= 0.35

        # Special case: Thomson MO5 requires 159 us bit 1 pulses
        if prof["cart_id"] == 3:
            has_159 = any(abs(159 - det) <= tol for det in detected_peaks) or (np.sum((pulses >= 140) & (pulses <= 180)) >= 10)
            if has_159:
                score += 15.0
            else:
                score *= 0.5

        # 2. Pilot tone matching (crucial discriminator! Up to 40 points)
        p_min, p_max = prof["pilot_range"]
        if pilot_us is not None and pilot_len >= 50:
            if p_min <= pilot_us <= p_max:
                score += 40.0
            elif (p_min - 25) <= pilot_us <= (p_max + 25):
                score += 20.0
            else:
                # Active pilot doesn't match this profile
                score = max(0.0, score - 25.0)

        # 3. Penalize excess or alien peaks not in profile (Noise rejection)
        if len(detected_peaks) > 0:
            alien_peaks = 0
            for det in detected_peaks:
                matches_exp = any(abs(det - exp) <= tol for exp in expected_peaks)
                matches_pilot = (pilot_us is not None and abs(det - pilot_us) <= tol)
                if not matches_exp and not matches_pilot:
                    alien_peaks += 1
            
            # Heavy penalty if too many alien peaks (indicates chaotic noise or speech)
            penalty = alien_peaks * 8.0
            score = max(0.0, score - penalty)

        # 4. If no pilot tone found at all, cap score
        if pilot_us is None:
            score = min(score, 45.0)

        return min(99.9, score)

    @staticmethod
    def _check_c64_phase_inversion(pulses: np.ndarray) -> bool:
        """Detect if Commodore pulse train has inverted polarity."""
        # On C64, valid bit sequences consist of SM (Short-Medium) and MS (Medium-Short).
        # Count occurrences of SM vs MS vs invalid combinations.
        s_min, s_max = 240, 420
        m_min, m_max = 421, 600

        syms = []
        for p in pulses[:2000]:
            if s_min <= p <= s_max:
                syms.append('S')
            elif m_min <= p <= m_max:
                syms.append('M')
            else:
                syms.append('L')

        sm_count = 0
        ms_count = 0
        for i in range(len(syms) - 1):
            pair = syms[i] + syms[i+1]
            if pair == 'SM':
                sm_count += 1
            elif pair == 'MS':
                ms_count += 1

        total_valid = sm_count + ms_count
        # If valid pairs are very low compared to symbols, or inverted logic is present
        return False
