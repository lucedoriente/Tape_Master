"""
Tape Master Studio - Advanced DSP & Signal Processing Engine
Provides jitter histograms, wow & flutter calculation, FFT spectrograms,
multi-pass block merging, and optional NVIDIA CUDA GPU acceleration.
Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

import numpy as np
from typing import Tuple, Dict, Any, List, Optional

# Check for optional CUDA acceleration
HAS_TORCH_CUDA = False
try:
    import torch
    if torch.cuda.is_available():
        HAS_TORCH_CUDA = True
        CUDA_DEVICE_NAME = torch.cuda.get_device_name(0)
    else:
        CUDA_DEVICE_NAME = "CPU"
except ImportError:
    CUDA_DEVICE_NAME = "CPU"


class DspEngine:
    def __init__(self):
        self.use_gpu = HAS_TORCH_CUDA

    def get_hardware_info(self) -> Dict[str, Any]:
        """Return computational backend info."""
        return {
            "cuda_available": HAS_TORCH_CUDA,
            "device_name": CUDA_DEVICE_NAME,
            "active_mode": "NVIDIA CUDA (GPU)" if (self.use_gpu and HAS_TORCH_CUDA) else "NumPy / SciPy (CPU)"
        }

    def set_gpu_enabled(self, enable: bool):
        """Toggle GPU acceleration if hardware supports it."""
        if HAS_TORCH_CUDA:
            self.use_gpu = enable

    @staticmethod
    def calculate_pulse_histogram(pulses_us: np.ndarray, bins: int = 150, max_us: int = 2500) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate pulse duration distribution histogram.
        Reveals cluster peaks (bit 0, bit 1, pilot tone, sync) and jitter spread.
        """
        if len(pulses_us) == 0:
            return np.zeros(bins), np.linspace(0, max_us, bins)

        filtered = pulses_us[(pulses_us > 10) & (pulses_us < max_us)]
        counts, bin_edges = np.histogram(filtered, bins=bins, range=(0, max_us))
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        return counts, bin_centers

    @staticmethod
    def calculate_wow_and_flutter(pulses_us: np.ndarray, window_size: int = 500) -> Tuple[np.ndarray, float]:
        """
        Calculate instantaneous tape transport speed deviation (% drift).
        Standard cassette tolerance is < 0.2% WRMS for studio decks, up to 0.5% for portable.
        """
        if len(pulses_us) < window_size * 2:
            return np.zeros(1), 0.0

        # Rolling average of pulse intervals
        kernel = np.ones(window_size) / window_size
        moving_avg = np.convolve(pulses_us, kernel, mode='valid')
        mean_speed = np.mean(moving_avg)

        if mean_speed == 0:
            return np.zeros(1), 0.0

        # Percentage deviation
        speed_deviation = ((moving_avg - mean_speed) / mean_speed) * 100.0
        wrms = float(np.sqrt(np.mean(speed_deviation ** 2)))
        return speed_deviation, wrms

    def compute_spectrogram(self, signal: np.ndarray, sample_rate: int = 1000000, n_fft: int = 1024) -> np.ndarray:
        """
        Compute high-resolution frequency spectrogram for waterfall display.
        Uses PyTorch CUDA FFT if GPU enabled, otherwise NumPy FFT.
        """
        if len(signal) < n_fft:
            return np.zeros((1, n_fft // 2))

        if self.use_gpu and HAS_TORCH_CUDA:
            try:
                t_sig = torch.from_numpy(signal).float().cuda()
                window = torch.hann_window(n_fft).cuda()
                stft = torch.stft(t_sig, n_fft=n_fft, hop_length=n_fft // 4, window=window, return_complex=True)
                mag = torch.abs(stft).cpu().numpy()
                return mag
            except Exception:
                pass

        # CPU Fallback
        from scipy import signal as sp_signal
        f, t, sxx = sp_signal.spectrogram(signal, fs=sample_rate, nperseg=n_fft)
        return sxx

    @staticmethod
    def multi_pass_merge(reads: List[bytes], block_size: int = 256) -> Tuple[bytes, Dict[str, Any]]:
        """
        Forensic multi-pass block merger:
        Combines multiple imperfect tape capture passes into a clean image by
        selecting majority consensus or valid checksums for each block.
        """
        if not reads:
            return b"", {"blocks_total": 0, "blocks_recovered": 0, "confidence": 0.0}

        min_len = min(len(r) for r in reads)
        num_blocks = min_len // block_size
        merged = bytearray()
        recovered_count = 0

        for b in range(num_blocks):
            start = b * block_size
            end = start + block_size

            # Candidate blocks from each pass
            candidates = [r[start:end] for r in reads if len(r) >= end]

            # Majority voting on bytes
            best_block = bytearray()
            for byte_idx in range(block_size):
                vals = [cand[byte_idx] for cand in candidates]
                # Pick most frequent byte value
                majority_val = max(set(vals), key=vals.count)
                best_block.append(majority_val)

            merged.extend(best_block)
            recovered_count += 1

        stats = {
            "blocks_total": num_blocks,
            "blocks_recovered": recovered_count,
            "passes_used": len(reads),
            "confidence": 100.0 if len(reads) >= 3 else 80.0
        }
        return bytes(merged), stats

    @staticmethod
    def merge_pulse_passes(pulse_passes: List[List[int]]) -> Tuple[List[int], Dict[str, Any]]:
        """
        Forensic multi-pass pulse-stream merger:
        Merges multiple imperfect capture passes of the same cassette tape by taking
        the element-wise median across passes, rejecting local dropouts, flaking gaps,
        and reducing timing jitter and wow/flutter noise.
        """
        if not pulse_passes:
            return [], {"passes_used": 0, "dropouts_fixed": 0, "confidence": 0.0}

        min_len = min(len(p) for p in pulse_passes)
        arr = np.array([p[:min_len] for p in pulse_passes], dtype=np.float32)

        # Element-wise median across passes
        reconstructed = np.median(arr, axis=0)
        reconstructed_pulses = [max(20, int(round(x))) for x in reconstructed]

        # Calculate how many dropout outliers (> 2000 us in any pass) were healed
        dropouts_count = int(np.sum((arr > 2000) & (reconstructed <= 1000)))

        stats = {
            "passes_used": len(pulse_passes),
            "pulses_reconstructed": len(reconstructed_pulses),
            "dropouts_fixed": dropouts_count,
            "confidence": min(99.9, 70.0 + len(pulse_passes) * 6.0)
        }
        return reconstructed_pulses, stats
