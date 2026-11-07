"""
Tape Master Studio - Azimuth Peak & VU-Meter Display Widget
Displays high-resolution analog level matching the physical 10-LED bar on Tape Master v2 UI Panel.
Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush

class AzimuthVuWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)
        self.setMinimumWidth(280)

        self.current_level = 0.0     # 0.0 .. 10.0
        self.peak_level = 0.0        # Peak hold
        self.peak_decay_timer = QTimer(self)
        self.peak_decay_timer.timeout.connect(self._decay_peak)
        self.peak_decay_timer.start(50)

        self.millivolts = 0

    def set_level(self, bar_level: int, raw_adc: int):
        """Update current measured level from board."""
        self.current_level = float(bar_level)
        self.millivolts = int((raw_adc * 3300) / 4095)

        if self.current_level > self.peak_level:
            self.peak_level = self.current_level

        self.update()

    def _decay_peak(self):
        if self.peak_level > self.current_level:
            self.peak_level -= 0.15
            if self.peak_level < self.current_level:
                self.peak_level = self.current_level
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # Background panel
        painter.fillRect(0, 0, w, h, QColor("#161820"))
        painter.setPen(QPen(QColor("#2B2E3E"), 1))
        painter.drawRect(0, 0, w - 1, h - 1)

        # Title
        painter.setPen(QColor("#00E5FF"))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(14, 22, "ALLINEAMENTO AZIMUT (TESTINA)")

        # Voltage readout
        painter.setPen(QColor("#00FF66"))
        painter.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        text_mv = f"{self.millivolts:4d} mV  ({int(self.current_level)}/10)"
        painter.drawText(w - 150, 22, text_mv)

        # Draw 10 LED segments (8 green, 1 yellow, 1 red)
        bar_x = 14
        bar_y = 38
        bar_w = w - 28
        bar_h = 32

        seg_gap = 4
        num_segs = 10
        seg_w = (bar_w - (seg_gap * (num_segs - 1))) / num_segs

        for i in range(num_segs):
            sx = int(bar_x + i * (seg_w + seg_gap))
            is_active = (i < int(self.current_level))
            is_peak = (int(self.peak_level) == i + 1)

            # Colors: 0..7 Green, 8 Yellow, 9 Red
            if i < 8:
                on_color = QColor("#00E676")
                off_color = QColor("#0A2B18")
            elif i == 8:
                on_color = QColor("#FFD600")
                off_color = QColor("#2B2500")
            else:
                on_color = QColor("#FF1744")
                off_color = QColor("#330A10")

            if is_active:
                painter.fillRect(sx, bar_y, int(seg_w), bar_h, on_color)
            else:
                painter.fillRect(sx, bar_y, int(seg_w), bar_h, off_color)

            # Draw peak-hold indicator dot
            if is_peak and not is_active:
                painter.fillRect(sx, bar_y, int(seg_w), 4, QColor("#FFFFFF"))

            # Segment border
            painter.setPen(QPen(QColor("#101216"), 1))
            painter.drawRect(sx, bar_y, int(seg_w), bar_h)

        # Bottom scale markings
        painter.setPen(QColor("#6A6E82"))
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(14, h - 8, "MIN (0 mV)")
        painter.drawText(w // 2 - 20, h - 8, "OTTIMALE")
        painter.drawText(w - 80, h - 8, "MAX (3.3V)")
