"""
Tape Master Studio - Deck Transport & Hardware Exerciser Control Widget
Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QGroupBox, QLabel, QFileDialog, QComboBox, QCheckBox)
from PyQt6.QtCore import pyqtSignal

class DeckControlWidget(QWidget):
    # Signals emitted to serial link
    command_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # 1. Transport Controls Group
        grp_deck = QGroupBox("CONTROLLI REGISTRATORE VIRTUALE")
        l_deck = QVBoxLayout(grp_deck)

        row_transport = QHBoxLayout()
        self.btn_play = QPushButton("▶ PLAY")
        self.btn_play.setObjectName("btnPlay")
        self.btn_play.clicked.connect(self._on_play_clicked)
        row_transport.addWidget(self.btn_play)

        self.btn_pause = QPushButton("⏸ PAUSA")
        self.btn_pause.clicked.connect(lambda: self.command_requested.emit("DECK PAUSE"))
        row_transport.addWidget(self.btn_pause)

        self.btn_resume = QPushButton("⏯ RIPRENDI")
        self.btn_resume.clicked.connect(lambda: self.command_requested.emit("DECK RESUME"))
        row_transport.addWidget(self.btn_resume)

        self.btn_stop = QPushButton("⏹ STOP")
        self.btn_stop.setObjectName("btnStop")
        self.btn_stop.clicked.connect(lambda: self.command_requested.emit("DECK STOP"))
        row_transport.addWidget(self.btn_stop)

        self.btn_rec = QPushButton("⏺ REGISTRA / ACQUISISCI")
        self.btn_rec.setObjectName("btnRec")
        self.btn_rec.clicked.connect(self._on_rec_clicked)
        row_transport.addWidget(self.btn_rec)

        l_deck.addLayout(row_transport)

        # File selection row
        row_file = QHBoxLayout()
        self.lbl_file = QLabel("Nessun file caricato")
        self.lbl_file.setStyleSheet("color: #00FF66; font-family: Consolas;")
        self.btn_browse = QPushButton("Carica File (.TAP / .TZX / .CSW)...")
        self.btn_browse.clicked.connect(self._on_browse_file)
        row_file.addWidget(self.btn_browse)
        row_file.addWidget(self.lbl_file, stretch=1)
        l_deck.addLayout(row_file)

        layout.addWidget(grp_deck)

        # 2. Hardware Exerciser & Diagnostics Group
        grp_ex = QGroupBox("COLLAUDO HARDWARE & TEST A BANCO")
        l_ex = QVBoxLayout(grp_ex)

        row_tones = QHBoxLayout()
        self.btn_1khz = QPushButton("Tono Calibrazione 1 kHz")
        self.btn_1khz.clicked.connect(lambda: self.command_requested.emit("EXERCISER 1KHZ"))
        row_tones.addWidget(self.btn_1khz)

        self.btn_2khz = QPushButton("Tono Calibrazione 2 kHz")
        self.btn_2khz.clicked.connect(lambda: self.command_requested.emit("EXERCISER 2KHZ"))
        row_tones.addWidget(self.btn_2khz)

        self.btn_loopback = QPushButton("Test Loopback Bus 40-Pin")
        self.btn_loopback.clicked.connect(lambda: self.command_requested.emit("EXERCISER LOOPBACK"))
        row_tones.addWidget(self.btn_loopback)
        l_ex.addLayout(row_tones)

        row_motor = QHBoxLayout()
        self.chk_motor = QCheckBox("Forzatura Manuale Relè Motore (Override Host)")
        self.chk_motor.toggled.connect(self._on_motor_toggled)
        row_motor.addWidget(self.chk_motor)

        self.chk_stream = QCheckBox("Streaming Continuo Oscilloscopio su USB")
        self.chk_stream.setChecked(True)
        self.chk_stream.toggled.connect(self._on_stream_toggled)
        row_motor.addWidget(self.chk_stream)
        l_ex.addLayout(row_motor)

        layout.addWidget(grp_ex)

        self.selected_file_path = ""

    def _on_browse_file(self):
        fpath, _ = QFileDialog.getOpenFileName(self, "Apri Immagine Nastro", "",
                                              "Tape Files (*.tap *.tzx *.csw *.cas);;All Files (*.*)")
        if fpath:
            self.selected_file_path = fpath
            self.lbl_file.setText(fpath.split("/")[-1])

    def _on_play_clicked(self):
        if self.selected_file_path:
            fname = self.selected_file_path.split("/")[-1]
            self.command_requested.emit(f"DECK START {fname}")
        else:
            self.command_requested.emit("DECK START")

    def _on_rec_clicked(self):
        self.command_requested.emit("REC START DUMP_PC.CSW")

    def _on_motor_toggled(self, state: bool):
        val = "ON" if state else "OFF"
        self.command_requested.emit(f"MOTOR {val}")

    def _on_stream_toggled(self, state: bool):
        val = "PULSES" if state else "STOP"
        self.command_requested.emit(f"STREAM {val}")
