"""
Tape Master Studio - Main Application Window
Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QPushButton, QComboBox, QLabel,
                             QStatusBar, QSplitter, QPlainTextEdit, QMessageBox,
                             QFileDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

from core.serial_link import SerialLink
from core.dsp_engine import DspEngine
from core.tape_decoder import TapeDecoder
from core.app_config import load_config, save_config
from gui.dark_theme import DARK_STYLESHEET
from gui.azimuth_widget import AzimuthVuWidget
from gui.scope_widget import ScopeWidget
from gui.deck_control_widget import DeckControlWidget
from gui.cartridge_card_widget import CartridgeCardWidget
from gui.file_lab_widget import FileLabWidget
from gui.agent_forensic_widget import AgentForensicWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tape Master Studio v2.0 — Forensic Tape Lab & Hardware Suite")
        
        # Load persistent configuration
        self.config = load_config()
        win_w = self.config.get("window", {}).get("width", 1280)
        win_h = self.config.get("window", {}).get("height", 840)
        self.resize(win_w, win_h)
        self.setStyleSheet(DARK_STYLESHEET)

        # Core engines
        self.serial = SerialLink()
        self.dsp = DspEngine()
        self.decoder = TapeDecoder()
        self.recovery_files = []

        # Connect serial callbacks
        self.serial.on_connected = self._on_connected
        self.serial.on_disconnected = self._on_disconnected
        self.serial.on_ident_received = self._on_ident_received
        self.serial.on_azimuth_received = self._on_azimuth_received
        self.serial.on_pulse_received = self._on_pulse_received
        self.serial.on_log_message = self._on_log_message

        self._init_ui()

        # Restore active tab from configuration
        saved_tab = self.config.get("window", {}).get("active_tab", 0)
        if 0 <= saved_tab < self.tabs.count():
            self.tabs.setCurrentIndex(saved_tab)

        # Auto-connect probe timer
        QTimer.singleShot(500, self._auto_connect)

    def _init_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(12, 10, 12, 10)
        root_layout.setSpacing(10)

        # 1. Top Control Bar (Connection & Backend GPU Indicator)
        bar_top = QHBoxLayout()
        bar_top.setSpacing(10)

        lbl_port = QLabel("Dispositivo:")
        lbl_port.setStyleSheet("font-weight: bold; color: #8C8FA1;")
        bar_top.addWidget(lbl_port)

        self.cmb_ports = QComboBox()
        self.cmb_ports.setMinimumWidth(220)
        self._refresh_ports()
        bar_top.addWidget(self.cmb_ports)

        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setFixedWidth(36)
        self.btn_refresh.clicked.connect(self._refresh_ports)
        bar_top.addWidget(self.btn_refresh)

        self.btn_connect = QPushButton("Connetti Tape Master")
        self.btn_connect.clicked.connect(self._toggle_connection)
        bar_top.addWidget(self.btn_connect)

        bar_top.addStretch(1)

        # GPU / Compute Engine Badge
        hw_info = self.dsp.get_hardware_info()
        self.lbl_gpu = QLabel(f"⚡ {hw_info['active_mode']}")
        if hw_info['cuda_available']:
            self.lbl_gpu.setStyleSheet("background-color: #1A3A22; color: #00FF66; padding: 4px 12px; border-radius: 4px; font-weight: bold;")
        else:
            self.lbl_gpu.setStyleSheet("background-color: #262938; color: #00E5FF; padding: 4px 12px; border-radius: 4px; font-weight: bold;")
        bar_top.addWidget(self.lbl_gpu)

        root_layout.addLayout(bar_top)

        # 2. Main Tab Widget
        self.tabs = QTabWidget()
        root_layout.addWidget(self.tabs, stretch=1)

        # Tab 1: Live Studio & Oscilloscope
        self.tab_live = QWidget()
        self._init_live_tab()
        self.tabs.addTab(self.tab_live, "📊 Live Studio & CDC")

        # Tab 2: Forensic File Lab & Blind Ingestion
        self.tab_file_lab = FileLabWidget()
        self.tabs.addTab(self.tab_file_lab, "📁 File Lab & Ingestion SD")

        # Tab 3: Forensic Recovery & Multi-Pass Merger
        self.tab_recovery = QWidget()
        self._init_recovery_tab()
        self.tabs.addTab(self.tab_recovery, "🔬 Forensic Multi-Pass Recovery")

        # Tab 4: Agentic AI Forensic Investigator
        self.tab_agent = AgentForensicWidget()
        self.tabs.addTab(self.tab_agent, "🧠 AI Forensic Agent")

        # Tab 5: Terminal & Log
        self.tab_log = QWidget()
        self._init_log_tab()
        self.tabs.addTab(self.tab_log, "💻 Terminale CDC USB")

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Tape Master Studio pronto. In attesa di connessione USB.")

    def _init_live_tab(self):
        layout = QHBoxLayout(self.tab_live)
        layout.setContentsMargins(10, 10, 10, 10)

        # Left Column: Scopes
        left_box = QWidget()
        l_layout = QVBoxLayout(left_box)
        l_layout.setContentsMargins(0, 0, 0, 0)

        self.azimuth_vu = AzimuthVuWidget()
        l_layout.addWidget(self.azimuth_vu)

        self.scope = ScopeWidget()
        l_layout.addWidget(self.scope, stretch=1)
        layout.addWidget(left_box, stretch=2)

        # Right Column: Cartridge Card & Deck Controls
        right_box = QWidget()
        r_layout = QVBoxLayout(right_box)
        r_layout.setContentsMargins(0, 0, 0, 0)

        self.cart_card = CartridgeCardWidget()
        r_layout.addWidget(self.cart_card)

        self.deck_controls = DeckControlWidget()
        self.deck_controls.command_requested.connect(self.serial.send_command)
        r_layout.addWidget(self.deck_controls, stretch=1)
        layout.addWidget(right_box, stretch=1)

    def _init_recovery_tab(self):
        layout = QVBoxLayout(self.tab_recovery)
        layout.setContentsMargins(14, 14, 14, 14)

        lbl = QLabel("FUSIONE MULTI-PASSAGGIO PER NASTRI DEGRADATI")
        lbl.setStyleSheet("color: #00E5FF; font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl)

        lbl_desc = QLabel("Carica 2 o più file di dump (.CSW o .TAP) catturati consecutivamente dallo stesso nastro rovinato.\n"
                          "L'algoritmo di voto a maggioranza e analisi probabilistica fonderà i settori integri ricostruendo l'immagine perfetta al 100%.")
        lbl_desc.setStyleSheet("color: #A0A4B8;")
        layout.addWidget(lbl_desc)

        row_btns = QHBoxLayout()
        btn_add = QPushButton("Aggiungi Dump Passata...")
        btn_add.clicked.connect(self._on_add_recovery_pass)
        row_btns.addWidget(btn_add)

        btn_merge = QPushButton("⚡ Esegui Ricostruzione & Merge Multi-Pass")
        btn_merge.setStyleSheet("background-color: #008744; font-weight: bold;")
        btn_merge.clicked.connect(self._on_run_merge)
        row_btns.addWidget(btn_merge)
        row_btns.addStretch(1)
        layout.addLayout(row_btns)

        self.txt_recovery_log = QPlainTextEdit()
        self.txt_recovery_log.setReadOnly(True)
        layout.addWidget(self.txt_recovery_log, stretch=1)

    def _init_log_tab(self):
        layout = QVBoxLayout(self.tab_log)
        layout.setContentsMargins(10, 10, 10, 10)

        self.txt_log = QPlainTextEdit()
        self.txt_log.setReadOnly(True)
        layout.addWidget(self.txt_log, stretch=1)

        row_send = QHBoxLayout()
        self.txt_cmd = QPlainTextEdit()
        self.txt_cmd.setMaximumHeight(36)
        row_send.addWidget(self.txt_cmd, stretch=1)

        btn_send = QPushButton("Invia")
        btn_send.clicked.connect(self._on_send_raw_cmd)
        row_send.addWidget(btn_send)
        layout.addLayout(row_send)

    def _refresh_ports(self):
        self.cmb_ports.clear()
        pico_port = SerialLink.find_pico_port()
        import serial.tools.list_ports
        for port in serial.tools.list_ports.comports():
            desc = f"{port.device} - {port.description}"
            self.cmb_ports.addItem(desc, port.device)
            if port.device == pico_port:
                self.cmb_ports.setCurrentIndex(self.cmb_ports.count() - 1)

    def _auto_connect(self):
        pico_port = SerialLink.find_pico_port()
        if pico_port:
            self.serial.connect(pico_port)

    def _toggle_connection(self):
        if self.serial.is_connected:
            self.serial.disconnect()
        else:
            idx = self.cmb_ports.currentIndex()
            port = self.cmb_ports.itemData(idx) if idx >= 0 else None
            self.serial.connect(port)

    def _on_connected(self, port: str):
        self.btn_connect.setText("Disconnetti")
        self.btn_connect.setStyleSheet("background-color: #B31D1D;")
        self.status_bar.showMessage(f"Connesso a Tape Master v2 su {port}")

    def _on_disconnected(self):
        self.btn_connect.setText("Connetti Tape Master")
        self.btn_connect.setStyleSheet("")
        self.status_bar.showMessage("Disconnesso.")

    def _on_ident_received(self, data):
        self.cart_card.update_cartridge_info(data)

    def _on_azimuth_received(self, bar_lvl: int, raw_adc: int):
        self.azimuth_vu.set_level(bar_lvl, raw_adc)

    def _on_pulse_received(self, us: int):
        self.scope.add_pulse(us)

    def _on_log_message(self, msg: str):
        self.txt_log.appendPlainText(msg)

    def _on_send_raw_cmd(self):
        cmd = self.txt_cmd.toPlainText().strip()
        if cmd:
            self.serial.send_command(cmd)
            self.txt_cmd.clear()

    def _on_add_recovery_pass(self):
        fpath, _ = QFileDialog.getOpenFileName(self, "Aggiungi Passata di Cattura", "", "CSW Files (*.csw);;All Files (*.*)")
        if fpath:
            self.recovery_files.append(fpath)
            self.txt_recovery_log.appendPlainText(f"[PASSATA {len(self.recovery_files)}] Aggiunta: {fpath}")

    def _on_run_merge(self):
        if len(self.recovery_files) < 2:
            QMessageBox.warning(self, "Passate Insufficienti", "Carica almeno 2 file di dump (.CSW) per eseguire il merge probabilistico.")
            return

        self.txt_recovery_log.appendPlainText(f"\nAvvio analisi probabilistica multi-pass su {len(self.recovery_files)} passate...")
        
        pulse_passes = []
        for pth in self.recovery_files:
            try:
                pulses, info = TapeDecoder.parse_csw_file(pth)
                pulse_passes.append(pulses)
            except Exception as e:
                self.txt_recovery_log.appendPlainText(f"Errore lettura {pth}: {e}")

        if len(pulse_passes) < 2:
            return

        merged_pulses, stats = DspEngine.merge_pulse_passes(pulse_passes)

        self.txt_recovery_log.appendPlainText("=" * 60)
        self.txt_recovery_log.appendPlainText("RISULTATO RICOSTRUZIONE MULTI-PASSAGGIO:")
        self.txt_recovery_log.appendPlainText(f"  • Passate utilizzate    : {stats['passes_used']}")
        self.txt_recovery_log.appendPlainText(f"  • Dropout eliminati     : {stats['dropouts_fixed']}")
        self.txt_recovery_log.appendPlainText(f"  • Confidenza statistica : {stats['confidence']:.1f}%")
        self.txt_recovery_log.appendPlainText(f"  • Impulsi unificati     : {len(merged_pulses):,}")
        self.txt_recovery_log.appendPlainText("=" * 60)

        # Allow saving merged file
        out_path, _ = QFileDialog.getSaveFileName(self, "Salva Dump Ricostruito", "MERGED_RECOVERED.csw", "CSW Files (*.csw)")
        if out_path:
            TapeDecoder.save_csw_file(out_path, merged_pulses)
            self.txt_recovery_log.appendPlainText(f"\n[OK] Immagine ricostruita salvata in: {out_path}")
            QMessageBox.information(self, "Merge Completato", f"File salvato con successo:\n{out_path}")

    def closeEvent(self, event):
        """Save configuration state on application close."""
        if "window" not in self.config:
            self.config["window"] = {}
        self.config["window"]["width"] = self.width()
        self.config["window"]["height"] = self.height()
        self.config["window"]["active_tab"] = self.tabs.currentIndex()

        if "serial" not in self.config:
            self.config["serial"] = {}
        self.config["serial"]["last_port"] = self.cmb_ports.currentText()

        # Save AI settings from widget
        self.tab_agent.save_settings(self.config)

        # Write configuration to JSON file
        save_config(self.config)

        # Disconnect serial if active
        if self.serial.is_connected:
            self.serial.disconnect()

        event.accept()
