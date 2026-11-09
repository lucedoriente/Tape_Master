"""
Tape Master Studio - Real-Time Pulse Scope & Jitter Histogram Widget
High-speed waveform and distribution display using PyQtGraph.
Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSplitter
from PyQt6.QtCore import Qt, QTimer
from core.dsp_engine import DspEngine

class ScopeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Configure pyqtgraph styling
        pg.setConfigOption('background', '#161820')
        pg.setConfigOption('foreground', '#A0A4B8')
        pg.setConfigOption('antialias', True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)

        # 1. Pulse Duration Stream Plot (Time Domain)
        self.plot_stream = pg.PlotWidget(title="FLUSSO IMPULSI IN TEMPO REALE (Microsecondi)")
        self.plot_stream.showGrid(x=True, y=True, alpha=0.3)
        self.plot_stream.setYRange(0, 2000)
        self.curve_stream = self.plot_stream.plot(pen=pg.mkPen(color="#00E5FF", width=1.5))
        splitter.addWidget(self.plot_stream)

        # 2. Jitter & Pulse Duration Histogram Plot (Frequency Domain)
        self.plot_hist = pg.PlotWidget(title="ISTOGRAMMA DI DISTRIBUZIONE IMPULSI & JITTER")
        self.plot_hist.showGrid(x=True, y=True, alpha=0.3)
        self.curve_hist = self.plot_hist.plot(stepMode="center", fillLevel=0, fillOutline=True,
                                              brush=pg.mkBrush(color=(0, 230, 118, 100)),
                                              pen=pg.mkPen(color="#00FF66", width=2))
        splitter.addWidget(self.plot_hist)

        # Ring buffer for live pulse data
        self.buffer_size = 1000
        self.pulse_buffer = np.zeros(self.buffer_size, dtype=np.float32)
        self.buffer_idx = 0
        self.total_pulses_counted = 0

        self.dsp = DspEngine()

        # Update timer at 30 FPS
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh_plots)
        self.timer.start(33)

    def add_pulse(self, interval_us: int):
        """Append incoming pulse duration to circular buffer."""
        self.pulse_buffer[self.buffer_idx] = float(interval_us)
        self.buffer_idx = (self.buffer_idx + 1) % self.buffer_size
        self.total_pulses_counted += 1

    def clear(self):
        """Reset live buffers."""
        self.pulse_buffer.fill(0)
        self.buffer_idx = 0
        self.total_pulses_counted = 0

    def _refresh_plots(self):
        """Refresh waveforms at regular frame rate."""
        if self.total_pulses_counted == 0:
            return

        # Roll buffer so newest is at the right
        rolled = np.roll(self.pulse_buffer, -self.buffer_idx)
        self.curve_stream.setData(rolled)

        # Compute histogram
        valid_pulses = rolled[rolled > 10]
        if len(valid_pulses) > 50:
            counts, bin_edges = np.histogram(valid_pulses, bins=80, range=(50, 1800))
            self.curve_hist.setData(bin_edges, counts)
