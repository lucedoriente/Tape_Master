#!/usr/bin/env python3
"""
Tape Master Studio v2.0 — Forensic Tape Lab & Hardware Suite
Official Host Companion Application for Tape Master Exerciser & Signal Digitizer v2.

Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Tape Master Studio")
    app.setOrganizationName("Alessio Iodice")

    win = MainWindow()
    win.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
