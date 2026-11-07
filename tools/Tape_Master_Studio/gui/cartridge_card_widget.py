"""
Tape Master Studio - Smart Cartridge Information Card Widget
Displays real-time hardware status of the active expansion cartridge from 24C02 EEPROM.
Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QGridLayout
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from typing import Dict, Any

class CartridgeCardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        grp = QGroupBox("SMART CARTRIDGE AUTO-ID (SLOT 40-PIN)")
        grid = QGridLayout(grp)
        grid.setSpacing(10)

        # Labels
        lbl_s_title = QLabel("Stato Slot:")
        lbl_s_title.setStyleSheet("color: #8C8FA1; font-weight: bold;")
        self.lbl_status = QLabel("NESSUNA CARTUCCIA")
        self.lbl_status.setStyleSheet("color: #FF5252; font-weight: bold;")

        lbl_p_title = QLabel("Piattaforma:")
        lbl_p_title.setStyleSheet("color: #8C8FA1; font-weight: bold;")
        self.lbl_platform = QLabel("---")
        self.lbl_platform.setStyleSheet("color: #00E5FF; font-size: 14px; font-weight: bold;")

        lbl_t_title = QLabel("Interfaccia Segnale:")
        lbl_t_title.setStyleSheet("color: #8C8FA1; font-weight: bold;")
        self.lbl_sig_type = QLabel("---")

        lbl_b_title = QLabel("Velocità Nominale:")
        lbl_b_title.setStyleSheet("color: #8C8FA1; font-weight: bold;")
        self.lbl_baud = QLabel("---")

        grid.addWidget(lbl_s_title, 0, 0)
        grid.addWidget(self.lbl_status, 0, 1)
        grid.addWidget(lbl_p_title, 1, 0)
        grid.addWidget(self.lbl_platform, 1, 1)
        grid.addWidget(lbl_t_title, 2, 0)
        grid.addWidget(self.lbl_sig_type, 2, 1)
        grid.addWidget(lbl_b_title, 3, 0)
        grid.addWidget(self.lbl_baud, 3, 1)

        layout.addWidget(grp)

    def update_cartridge_info(self, data: Dict[str, Any]):
        """Update fields from IDENT response."""
        inserted = data.get("CART_INSERTED", 0) == 1
        cid = data.get("CART_ID", 0)
        platform = data.get("PLATFORM", "Sconosciuta")
        sig_type = data.get("SIG_TYPE", 0)
        baud = data.get("BAUD", 0)

        if inserted and cid > 0:
            self.lbl_status.setText(f"INSERITA (ID #{cid})")
            self.lbl_status.setStyleSheet("color: #00E676; font-weight: bold;")
            self.lbl_platform.setText(str(platform))

            sig_names = {
                0: "Impulsi TTL Squadrati (5V Logico)",
                1: "Audio Analogico FSK (Cavo Jack/DIN)",
                2: "Seriale Asincrona UART (SIO / RS-232)",
                3: "Testina Grezza Diretta (Raw Magnetic Ingest)"
            }
            self.lbl_sig_type.setText(sig_names.get(sig_type, f"Tipo {sig_type}"))
            self.lbl_baud.setText(f"{baud} baud / bps" if baud > 0 else "Frequenza Variabile")
        elif inserted:
            self.lbl_status.setText("INSERITA (EEPROM non programmata)")
            self.lbl_status.setStyleSheet("color: #FFD600; font-weight: bold;")
            self.lbl_platform.setText("Cartuccia Generica")
            self.lbl_sig_type.setText("---")
            self.lbl_baud.setText("---")
        else:
            self.lbl_status.setText("SLOT VUOTO")
            self.lbl_status.setStyleSheet("color: #FF5252; font-weight: bold;")
            self.lbl_platform.setText("Nessuna Cartuccia")
            self.lbl_sig_type.setText("---")
            self.lbl_baud.setText("---")
