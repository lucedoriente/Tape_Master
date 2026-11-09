#!/usr/bin/env python3
"""
Tape Master Studio v2.0 — Forensic Tape Lab & Hardware Suite
Official Host Companion Application for Tape Master Exerciser & Signal Digitizer v2.

Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

import sys
import os

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

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
