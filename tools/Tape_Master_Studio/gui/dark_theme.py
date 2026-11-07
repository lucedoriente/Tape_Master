"""
Tape Master Studio - Professional Dark Laboratory Theme
Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

DARK_STYLESHEET = """
QMainWindow {
    background-color: #121316;
    color: #E0E0E6;
    font-family: 'Segoe UI', 'SF Pro Text', 'Helvetica Neue', sans-serif;
}

QWidget {
    background-color: #121316;
    color: #E0E0E6;
    font-size: 13px;
}

QTabWidget::pane {
    border: 1px solid #282A36;
    background-color: #18191E;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #18191E;
    color: #8C8FA1;
    padding: 8px 18px;
    border: 1px solid #282A36;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #242630;
    color: #00E5FF;
    border-bottom: 2px solid #00E5FF;
}

QTabBar::tab:hover {
    color: #FFFFFF;
    background-color: #20222B;
}

QGroupBox {
    border: 1px solid #2C2E3B;
    border-radius: 6px;
    margin-top: 18px;
    padding-top: 14px;
    font-weight: bold;
    color: #00E5FF;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    background-color: #121316;
}

QPushButton {
    background-color: #242735;
    color: #FFFFFF;
    border: 1px solid #36394D;
    border-radius: 4px;
    padding: 7px 16px;
    font-weight: 600;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #2F3346;
    border-color: #00E5FF;
}

QPushButton:pressed {
    background-color: #1A1C27;
}

QPushButton:disabled {
    background-color: #181A22;
    color: #555768;
    border-color: #22242F;
}

QPushButton#btnPlay {
    background-color: #008744;
    border-color: #00A854;
    color: #FFFFFF;
}
QPushButton#btnPlay:hover {
    background-color: #00A854;
}

QPushButton#btnRec {
    background-color: #B31D1D;
    border-color: #D32F2F;
    color: #FFFFFF;
}
QPushButton#btnRec:hover {
    background-color: #D32F2F;
}

QPushButton#btnStop {
    background-color: #3E4357;
    border-color: #525872;
}

QProgressBar {
    border: 1px solid #2E3244;
    border-radius: 4px;
    text-align: center;
    background-color: #161820;
    color: #FFFFFF;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #00E5FF;
    border-radius: 3px;
}

QTextEdit, QPlainTextEdit, QLineEdit {
    background-color: #0E0F14;
    border: 1px solid #282A36;
    border-radius: 4px;
    color: #00FF66;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 4px;
}

QStatusBar {
    background-color: #0D0E12;
    color: #8C8FA1;
    border-top: 1px solid #20222C;
}
"""
