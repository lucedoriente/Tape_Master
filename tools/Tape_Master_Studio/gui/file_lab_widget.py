"""
Tape Master Studio - File Ingestion & Blind Tape Forensic Lab Widget
Provides offline inspection of captured SD tape files (.CSW / .TAP),
automatic platform identification across all 13 cartridges,
interactive pulse scopes, histogram peak analysis, and payload export.
Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

import os
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSplitter, QPlainTextEdit, QFileDialog,
                             QMessageBox, QFrame, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.tape_decoder import TapeDecoder
from core.tape_classifier import TapeClassifier, CARTRIDGE_PROFILES
from core.dsp_engine import DspEngine

class FileLabWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_filepath = ""
        self.current_pulses = []
        self.classification_result = {}
        self.decoded_result = {}

        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # 1. Top Control Bar (File Open & Hero Badges)
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        self.btn_open = QPushButton("📂 Apri File Dump da SD (.CSW / .TAP)")
        self.btn_open.setStyleSheet("background-color: #008744; font-weight: bold; font-size: 13px; padding: 6px 14px;")
        self.btn_open.clicked.connect(self._on_open_file)
        top_bar.addWidget(self.btn_open)

        self.lbl_filename = QLabel("Nessun file caricato")
        self.lbl_filename.setStyleSheet("color: #8C8FA1; font-style: italic;")
        top_bar.addWidget(self.lbl_filename)

        top_bar.addStretch(1)

        # Hero Platform Badge
        self.lbl_hero_badge = QLabel("🎯 In attesa di caricamento file...")
        self.lbl_hero_badge.setStyleSheet(
            "background-color: #262938; color: #00E5FF; padding: 6px 14px; border-radius: 6px; font-weight: bold; font-size: 13px;"
        )
        top_bar.addWidget(self.lbl_hero_badge)

        root.addLayout(top_bar)

        # 2. Secondary Metrics Banner
        banner = QHBoxLayout()
        banner.setSpacing(8)

        self.badge_pulses = self._create_metric_badge("Impulsi: 0", "#2E3144", "#A0A4B8")
        self.badge_duration = self._create_metric_badge("Durata: 0.0s", "#2E3144", "#A0A4B8")
        self.badge_wrms = self._create_metric_badge("Wow & Flutter: 0.0%", "#2E3144", "#A0A4B8")
        self.badge_phase = self._create_metric_badge("Fase: Normale", "#2E3144", "#A0A4B8")
        self.badge_pilot = self._create_metric_badge("Pilot: N/A", "#2E3144", "#A0A4B8")

        banner.addWidget(self.badge_pulses)
        banner.addWidget(self.badge_duration)
        banner.addWidget(self.badge_wrms)
        banner.addWidget(self.badge_phase)
        banner.addWidget(self.badge_pilot)
        banner.addStretch(1)

        root.addLayout(banner)

        # 3. Main Splitter: Scopes (Left) & Forensic / Decoded Payload (Right)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter, stretch=1)

        # Left Column: Waveform Plot + Histogram
        w_left = QWidget()
        l_layout = QVBoxLayout(w_left)
        l_layout.setContentsMargins(0, 0, 0, 0)

        # Waveform Plot
        self.plot_wave = pg.PlotWidget(title="FLUSSO TEMPORALE IMPULSI ACQUISITI (Microsecondi)")
        self.plot_wave.showGrid(x=True, y=True, alpha=0.3)
        self.plot_wave.setLabel("bottom", "Indice Impulso")
        self.plot_wave.setLabel("left", "Durata (us)")
        self.plot_wave.setYRange(0, 2000)
        self.curve_wave = self.plot_wave.plot(pen=pg.mkPen(color="#00E5FF", width=1.2))
        l_layout.addWidget(self.plot_wave, stretch=1)

        # Histogram Plot
        self.plot_hist = pg.PlotWidget(title="ISTOGRAMMA & CLUSTERING SOGLIE (Identificazione Picchi)")
        self.plot_hist.showGrid(x=True, y=True, alpha=0.3)
        self.plot_hist.setLabel("bottom", "Durata Impulso (us)")
        self.plot_hist.setLabel("left", "Conteggio")
        self.curve_hist = self.plot_hist.plot(stepMode="center", fillLevel=0, fillOutline=True,
                                              brush=pg.mkBrush(color=(0, 230, 118, 120)),
                                              pen=pg.mkPen(color="#00FF66", width=2))
        l_layout.addWidget(self.plot_hist, stretch=1)

        splitter.addWidget(w_left)

        # Right Column: Forensic Details & Decoded Payload
        w_right = QWidget()
        r_layout = QVBoxLayout(w_right)
        r_layout.setContentsMargins(6, 0, 0, 0)
        r_layout.setSpacing(8)

        lbl_forensic_title = QLabel("🔬 REPORT FORENSE E IDENTIFICAZIONE CIECA")
        lbl_forensic_title.setStyleSheet("color: #00E5FF; font-weight: bold; font-size: 13px;")
        r_layout.addWidget(lbl_forensic_title)

        self.txt_forensic_report = QPlainTextEdit()
        self.txt_forensic_report.setReadOnly(True)
        self.txt_forensic_report.setMaximumHeight(140)
        self.txt_forensic_report.setFont(QFont("Consolas", 9))
        self.txt_forensic_report.setStyleSheet("background-color: #1E202B; border: 1px solid #2E3144; color: #E0E2EC;")
        r_layout.addWidget(self.txt_forensic_report)

        lbl_payload_title = QLabel("📦 CONTENUTO E PAYLOAD DECODIFICATO")
        lbl_payload_title.setStyleSheet("color: #00FF66; font-weight: bold; font-size: 13px;")
        r_layout.addWidget(lbl_payload_title)

        self.txt_payload_hex = QPlainTextEdit()
        self.txt_payload_hex.setReadOnly(True)
        self.txt_payload_hex.setFont(QFont("Consolas", 9))
        self.txt_payload_hex.setStyleSheet("background-color: #14161F; border: 1px solid #2E3144; color: #00FF66;")
        r_layout.addWidget(self.txt_payload_hex, stretch=1)

        # Export Buttons
        btn_box = QHBoxLayout()
        self.btn_export_native = QPushButton("💾 Esporta Formato Emulatore")
        self.btn_export_native.setStyleSheet("background-color: #1A535C; font-weight: bold; padding: 6px;")
        self.btn_export_native.clicked.connect(self._on_export_native)
        self.btn_export_native.setEnabled(False)
        btn_box.addWidget(self.btn_export_native)

        self.btn_export_csw = QPushButton("💾 Salva .CSW v2 Ricostruito")
        self.btn_export_csw.setStyleSheet("background-color: #38405F; font-weight: bold; padding: 6px;")
        self.btn_export_csw.clicked.connect(self._on_export_csw)
        self.btn_export_csw.setEnabled(False)
        btn_box.addWidget(self.btn_export_csw)

        r_layout.addLayout(btn_box)

        splitter.addWidget(w_right)
        splitter.setSizes([750, 480])

    def _create_metric_badge(self, text: str, bg: str, fg: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"background-color: {bg}; color: {fg}; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;")
        return lbl

    def _on_open_file(self):
        fpath, _ = QFileDialog.getOpenFileName(
            self, "Apri Dump Nastro da MicroSD", "",
            "Tutti i formati nastro (*.csw *.tap *.tzx *.bin);;CSW Files (*.csw);;TAP Files (*.tap);;All Files (*.*)"
        )
        if not fpath:
            return

        self.load_file(fpath)

    def load_file(self, filepath: str):
        """Loads and processes a tape capture file."""
        try:
            self.current_filepath = filepath
            self.lbl_filename.setText(os.path.basename(filepath))

            # 1. Parse File (Universal Support: CSW v2/v1, C64 TAP, Spectrum TAP/TZX, BIN)
            pulses, info = TapeDecoder.universal_open_file(filepath)

            self.current_pulses = pulses

            # 2. Run Blind Classifier
            self.classification_result = TapeClassifier.classify_pulses(pulses)

            # 3. Run Decoder
            p_id = self.classification_result["primary_platform"]
            self.decoded_result = TapeDecoder.auto_decode(pulses, p_id)

            # 4. Update UI
            self._update_ui_views()

        except Exception as e:
            QMessageBox.critical(self, "Errore Caricamento File", f"Impossibile analizzare il file:\n{str(e)}")

    def _update_ui_views(self):
        pulses = self.current_pulses
        cls = self.classification_result
        dec = self.decoded_result

        # A. Update Hero Badge
        conf = cls.get("confidence", 0.0)
        p_name = cls.get("platform_name", "Sconosciuto")
        if conf >= 70.0:
            self.lbl_hero_badge.setText(f"🎯 RICONOSCIUTO: {p_name} ({conf:.1f}%)")
            self.lbl_hero_badge.setStyleSheet("background-color: #1A3A22; color: #00FF66; padding: 6px 14px; border-radius: 6px; font-weight: bold; font-size: 13px;")
        elif conf >= 35.0:
            self.lbl_hero_badge.setText(f"⚠️ PROBABILE: {p_name} ({conf:.1f}%)")
            self.lbl_hero_badge.setStyleSheet("background-color: #4D3800; color: #FFD600; padding: 6px 14px; border-radius: 6px; font-weight: bold; font-size: 13px;")
        else:
            self.lbl_hero_badge.setText("❌ SEGNALE NON RICONOSCIUTO / RUMORE")
            self.lbl_hero_badge.setStyleSheet("background-color: #4A1515; color: #FF5252; padding: 6px 14px; border-radius: 6px; font-weight: bold; font-size: 13px;")

        # B. Secondary Badges
        total_p = len(pulses)
        total_time_s = sum(pulses) / 1000000.0 if pulses else 0.0
        self.badge_pulses.setText(f"Impulsi: {total_p:,}")
        self.badge_duration.setText(f"Durata: {total_time_s:.2f}s")
        self.badge_wrms.setText(f"Wow & Flutter: {cls.get('wow_flutter_wrms', 0.0):.2f}%")
        self.badge_phase.setText("Fase: INVERTITA" if cls.get("inverted_phase", False) else "Fase: Normale")
        self.badge_pilot.setText(f"Pilot: {cls.get('pilot_pulse_us', 'Assente')} us")

        # C. Waveform Plot (sample up to 4000 pulses for fast responsiveness)
        disp_pulses = np.array(pulses[:4000], dtype=np.float32)
        self.curve_wave.setData(disp_pulses)
        self.plot_wave.setXRange(0, len(disp_pulses))

        # D. Histogram Plot
        valid_pulses = np.array([p for p in pulses if 20 <= p <= 2000], dtype=np.float32)
        if len(valid_pulses) > 0:
            counts, edges = np.histogram(valid_pulses, bins=150, range=(20, 2000))
            self.curve_hist.setData(x=edges, y=counts)
            self.plot_hist.setXRange(20, max(1000, np.max(cls.get("detected_peaks", [1000])) + 150))

        # E. Forensic Report Text
        peaks_str = ", ".join(f"{p} us" for p in cls.get("detected_peaks", []))
        ranking_lines = []
        for cand_id, score in cls.get("all_matches", [])[:4]:
            cand_name = CARTRIDGE_PROFILES.get(cand_id, {}).get("name", cand_id)
            ranking_lines.append(f"  - {cand_name:38s}: {score:5.1f}%")
        ranking_str = "\n".join(ranking_lines)

        report = (
            f"FILE SOTTOPOSTO A PERIZIA: {os.path.basename(self.current_filepath)}\n"
            f"Piattaforma Stimata : {p_name} (Confidenza: {conf:.1f}%)\n"
            f"Famiglia Modulazione: {cls.get('family', 'N/A')}\n"
            f"Tono Guida (Pilot)  : {cls.get('pilot_pulse_us')} us (Striscia: {cls.get('pilot_length_pulses', 0)} impulsi)\n"
            f"Picchi Gaussiani Δt : [{peaks_str}]\n"
            f"Deriva Motore WRMS  : {cls.get('wow_flutter_wrms', 0.0):.2f}%\n"
            f"Polarità Rilevata   : {'INVERTITA (180°)' if cls.get('inverted_phase') else 'Normale (Diretta)'}\n\n"
            f"GRADUATORIA CANDIDATI TAPE MASTER:\n"
            f"{ranking_str}"
        )
        self.txt_forensic_report.setPlainText(report)

        # F. Decoded Payload Hex / Text Preview
        payload = dec.get("payload_bytes", b"")
        fname = dec.get("filename", "DUMP.BIN")
        fmt = dec.get("format", "Sconosciuto")

        hex_preview = self._format_hex_dump(payload[:1024])
        info_header = (
            f"--- FILE ESTRATTO: {fname} ({len(payload)} byte) ---\n"
            f"--- FORMATO: {fmt} ---\n\n"
        )
        self.txt_payload_hex.setPlainText(info_header + hex_preview)

        # Enable export buttons
        self.btn_export_native.setEnabled(len(payload) > 0)
        self.btn_export_csw.setEnabled(len(pulses) > 0)
        self.btn_export_native.setText(f"💾 Esporta {fname}")

    def _format_hex_dump(self, data: bytes) -> str:
        if not data:
            return "(Nessun payload estratto dallo stream)"
        lines = []
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hex_str = " ".join(f"{b:02X}" for b in chunk)
            asc_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
            lines.append(f"{i:06X}  {hex_str:<48s}  |{asc_str}|")
        return "\n".join(lines)

    def _on_export_native(self):
        payload = self.decoded_result.get("payload_bytes", b"")
        default_name = self.decoded_result.get("filename", "DUMP.BIN")
        ext = os.path.splitext(default_name)[1]

        fpath, _ = QFileDialog.getSaveFileName(
            self, "Esporta File per Emulatore", default_name, f"File {ext} (*{ext});;Tutti i File (*.*)"
        )
        if fpath:
            with open(fpath, "wb") as f:
                f.write(payload)
            QMessageBox.information(self, "Esportazione Riuscita", f"File salvato con successo:\n{fpath}")

    def _on_export_csw(self):
        default_name = os.path.splitext(os.path.basename(self.current_filepath))[0] + "_clean.csw"
        fpath, _ = QFileDialog.getSaveFileName(
            self, "Esporta File CSW v2", default_name, "CSW Files (*.csw);;Tutti i File (*.*)"
        )
        if fpath:
            TapeDecoder.save_csw_file(fpath, self.current_pulses)
            QMessageBox.information(self, "Esportazione Riuscita", f"File CSW v2 salvato con successo:\n{fpath}")
