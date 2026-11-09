"""
Tape Master Studio - Agentic AI Forensic Investigator Widget
Interactive GUI panel for running autonomous investigations with local/cloud LLMs.
Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

import os
import json
import urllib.request
import urllib.error
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QComboBox, QRadioButton, QButtonGroup,
                             QPlainTextEdit, QFileDialog, QMessageBox, QGroupBox,
                             QSplitter, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from core.forensic_agent import ForensicAgent
from core.app_config import load_config, save_config


class KeyValidatorThread(QThread):
    result_signal = pyqtSignal(bool, str)

    def __init__(self, backend: str, model: str, api_key: str):
        super().__init__()
        self.backend = backend
        self.model = model
        self.api_key = api_key

    def run(self):
        if self.backend == "gemini":
            if not self.api_key:
                self.result_signal.emit(False, "❌ Inserisci una chiave API prima di verificare.")
                return
            if not self.model:
                self.result_signal.emit(False, "❌ Specifica o seleziona un modello Gemini.")
                return

            clean_model = self.model.strip()
            if clean_model.startswith("models/"):
                clean_model = clean_model[7:]

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}?key={self.api_key}"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "TapeMasterStudio/2.0"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        disp_name = data.get("displayName", clean_model)
                        self.result_signal.emit(True, f"✅ Chiave Valida! Modello '{disp_name}' pronto all'uso.")
                    else:
                        self.result_signal.emit(False, f"⚠️ Risposta Google: HTTP {resp.status}")
            except urllib.error.HTTPError as e:
                if e.code == 400:
                    self.result_signal.emit(False, "❌ Chiave API non valida o malformata (HTTP 400).")
                elif e.code == 403:
                    self.result_signal.emit(False, "❌ Autorizzazione negata (HTTP 403: verifica permessi Gemini API).")
                elif e.code == 404:
                    self.result_signal.emit(False, f"❌ Modello '{clean_model}' non accessibile o inesistente per questa chiave (HTTP 404).")
                else:
                    self.result_signal.emit(False, f"❌ Errore API: HTTP {e.code} ({e.reason})")
            except urllib.error.URLError as e:
                self.result_signal.emit(False, f"❌ Connessione fallita: {e.reason}")
            except Exception as e:
                self.result_signal.emit(False, f"❌ Errore durante la verifica: {e}")

        elif self.backend == "ollama":
            url = "http://localhost:11434/api/tags"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "TapeMasterStudio/2.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    installed = [m.get("name", "") for m in data.get("models", [])]
                    target = self.model.strip()
                    found = any(target == m or f"{target}:latest" == m or target.split(":")[0] in m for m in installed)
                    if found:
                        self.result_signal.emit(True, f"✅ Ollama attivo! Modello '{target}' trovato localmente.")
                    else:
                        avail = ", ".join([m.split(":")[0] for m in installed[:4]])
                        self.result_signal.emit(False, f"⚠️ Ollama attivo, ma '{target}' non trovato. Disponibili: {avail or 'nessuno'}")
            except Exception:
                self.result_signal.emit(False, "❌ Impossibile connettersi a Ollama (localhost:11434 non raggiungibile).")

        else:
            self.result_signal.emit(True, "✅ Motore euristico integrato pronto (100% Offline, nessuna chiave richiesta).")


class AgentWorkerThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)

    def __init__(self, agent: ForensicAgent, file_path: str):
        super().__init__()
        self.agent = agent
        self.file_path = file_path

    def run(self):
        try:
            result = self.agent.run_investigation(
                self.file_path,
                progress_callback=self.progress_signal.emit
            )
            self.finished_signal.emit(result)
        except Exception as e:
            self.progress_signal.emit(f"❌ Errore critico agente: {e}")
            self.finished_signal.emit({"report": f"Errore durante l'esecuzione: {e}"})


class AgentForensicWidget(QWidget):
    GEMINI_MODELS = [
        "gemini-2.0-flash",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-2.0-flash-lite",
    ]

    OLLAMA_MODELS = [
        "qwen2.5-coder:14b",
        "qwen2.5-coder:7b",
        "llama3.1:8b",
        "deepseek-r1:14b",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_filepath = ""
        self.worker_thread = None
        self.validator_thread = None
        self._init_ui()
        self.load_settings()

    def load_settings(self, cfg: dict = None):
        """Loads persistent AI configuration from JSON."""
        if cfg is None:
            cfg = load_config()
        ai_cfg = cfg.get("ai", {})
        backend = ai_cfg.get("backend", "gemini")

        # Block signals during initial population
        self.btn_grp.blockSignals(True)
        self.combo_model.blockSignals(True)
        self.txt_key.blockSignals(True)

        if backend == "ollama":
            self.rb_ollama.setChecked(True)
            self.combo_model.clear()
            self.combo_model.addItems(self.OLLAMA_MODELS)
            saved_model = ai_cfg.get("ollama_model", "qwen2.5-coder:14b")
            self.lbl_key.setVisible(False)
            self.txt_key.setVisible(False)
            self.btn_verify.setText("🔍 Verifica Server Ollama")
        elif backend == "heuristic":
            self.rb_heuristic.setChecked(True)
            self.combo_model.clear()
            self.combo_model.addItem("heuristic-rules")
            saved_model = "heuristic-rules"
            self.lbl_key.setVisible(False)
            self.txt_key.setVisible(False)
            self.btn_verify.setText("🔍 Verifica Motore")
        else:
            self.rb_gemini.setChecked(True)
            self.combo_model.clear()
            self.combo_model.addItems(self.GEMINI_MODELS)
            saved_model = ai_cfg.get("gemini_model", "gemini-2.0-flash")
            self.lbl_key.setVisible(True)
            self.txt_key.setVisible(True)
            self.btn_verify.setText("🔍 Verifica Chiave & Modello")

        # Set model
        idx = self.combo_model.findText(saved_model)
        if idx >= 0:
            self.combo_model.setCurrentIndex(idx)
        else:
            self.combo_model.setEditText(saved_model)

        # Set API key
        key = ai_cfg.get("gemini_api_key", "")
        if key:
            self.txt_key.setText(key)

        self.btn_grp.blockSignals(False)
        self.combo_model.blockSignals(False)
        self.txt_key.blockSignals(False)

    def save_settings(self, cfg: dict = None) -> dict:
        """Saves current AI settings to JSON configuration."""
        if cfg is None:
            cfg = load_config()
        if "ai" not in cfg:
            cfg["ai"] = {}

        # Always save and retain the Gemini API key regardless of active radio tab
        key_text = self.txt_key.text().strip()
        if key_text:
            cfg["ai"]["gemini_api_key"] = key_text

        if self.rb_gemini.isChecked():
            cfg["ai"]["backend"] = "gemini"
            cfg["ai"]["gemini_model"] = self.combo_model.currentText().strip()
        elif self.rb_ollama.isChecked():
            cfg["ai"]["backend"] = "ollama"
            cfg["ai"]["ollama_model"] = self.combo_model.currentText().strip()
        else:
            cfg["ai"]["backend"] = "heuristic"

        save_config(cfg)
        return cfg

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # 1. Backend Configuration Box
        grp_backend = QGroupBox("⚙️ Configurazione Privacy & Motore di Inferenza AI")
        grp_backend.setStyleSheet("QGroupBox { font-weight: bold; color: #00E5FF; }")
        l_backend = QVBoxLayout(grp_backend)

        # Radio buttons
        r_row = QHBoxLayout()
        self.rb_gemini = QRadioButton("☁️ Google Gemini API (Ultra / Pro / Flash)")
        self.rb_gemini.setChecked(True)
        self.rb_ollama = QRadioButton("🔒 Ollama On-Premises (100% Privato / GPU Locale)")
        self.rb_heuristic = QRadioButton("⚙️ Motore Euristico Locale (Offline / No Key)")

        self.btn_grp = QButtonGroup(self)
        self.btn_grp.addButton(self.rb_gemini)
        self.btn_grp.addButton(self.rb_ollama)
        self.btn_grp.addButton(self.rb_heuristic)

        self.rb_gemini.toggled.connect(self._on_backend_changed)
        self.rb_ollama.toggled.connect(self._on_backend_changed)
        self.rb_heuristic.toggled.connect(self._on_backend_changed)

        r_row.addWidget(self.rb_gemini)
        r_row.addWidget(self.rb_ollama)
        r_row.addWidget(self.rb_heuristic)
        r_row.addStretch(1)
        l_backend.addLayout(r_row)

        # Fields row
        f_row = QHBoxLayout()
        f_row.addWidget(QLabel("Modello:"))
        self.combo_model = QComboBox()
        self.combo_model.setEditable(True)
        self.combo_model.setMinimumWidth(190)
        self.combo_model.addItems(self.GEMINI_MODELS)
        self.combo_model.currentTextChanged.connect(self._on_model_or_key_changed)
        f_row.addWidget(self.combo_model)

        self.lbl_key = QLabel("Gemini API Key:")
        f_row.addWidget(self.lbl_key)
        self.txt_key = QLineEdit()
        self.txt_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_key.setPlaceholderText("Incolla qui la chiave API (oppure lascia vuoto per modalità locale)")
        self.txt_key.textChanged.connect(self._on_model_or_key_changed)

        # Load from env if present
        env_key = os.environ.get("GEMINI_API_KEY", "")
        if env_key:
            self.txt_key.setText(env_key)
        f_row.addWidget(self.txt_key, stretch=1)

        # Verification button
        self.btn_verify = QPushButton("🔍 Verifica Chiave & Modello")
        self.btn_verify.setStyleSheet("background-color: #383A59; color: #FFF; font-weight: bold; padding: 5px 12px;")
        self.btn_verify.clicked.connect(self._on_verify_key_clicked)
        f_row.addWidget(self.btn_verify)

        l_backend.addLayout(f_row)

        # Validation status label row
        status_row = QHBoxLayout()
        self.lbl_status = QLabel("Stato: In attesa di verifica")
        self.lbl_status.setStyleSheet("color: #8C8FA1; font-style: italic;")
        status_row.addWidget(self.lbl_status)
        status_row.addStretch(1)
        l_backend.addLayout(status_row)

        root.addWidget(grp_backend)

        # 2. File Selection & Trigger Bar
        bar_action = QHBoxLayout()
        self.btn_select_file = QPushButton("📂 Seleziona File Nastro (.CSW / .TAP)")
        self.btn_select_file.setStyleSheet("background-color: #2E3144; font-weight: bold; padding: 6px 14px;")
        self.btn_select_file.clicked.connect(self._on_select_file)
        bar_action.addWidget(self.btn_select_file)

        self.lbl_target_file = QLabel("Nessun file selezionato")
        self.lbl_target_file.setStyleSheet("color: #8C8FA1; font-style: italic;")
        bar_action.addWidget(self.lbl_target_file)

        bar_action.addStretch(1)

        self.btn_run = QPushButton("🧠 AVVIA INDAGINE PERITALE RE-ACT")
        self.btn_run.setStyleSheet("background-color: #008744; font-weight: bold; font-size: 13px; padding: 7px 20px;")
        self.btn_run.clicked.connect(self._on_run_agent)
        bar_action.addWidget(self.btn_run)

        root.addLayout(bar_action)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #00E5FF; }")
        root.addWidget(self.progress_bar)

        # 3. Main Console Splitter: Live Thought Process (Left) & Final Report (Right)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter, stretch=1)

        # Left: Live Thoughts
        w_left = QWidget()
        l_layout = QVBoxLayout(w_left)
        l_layout.setContentsMargins(0, 0, 0, 0)
        lbl_live = QLabel("⚡ REGISTRO RAGIONAMENTO & CHIAMATA TOOLS (Chain-of-Thought)")
        lbl_live.setStyleSheet("color: #00E5FF; font-weight: bold;")
        l_layout.addWidget(lbl_live)

        self.txt_live_log = QPlainTextEdit()
        self.txt_live_log.setReadOnly(True)
        self.txt_live_log.setFont(QFont("Consolas", 9))
        self.txt_live_log.setStyleSheet("background-color: #14161F; border: 1px solid #2E3144; color: #00FF66;")
        l_layout.addWidget(self.txt_live_log)
        splitter.addWidget(w_left)

        # Right: Final Report & Reconstructed Payload
        w_right = QWidget()
        r_layout = QVBoxLayout(w_right)
        r_layout.setContentsMargins(6, 0, 0, 0)
        lbl_rep = QLabel("📑 PERIZIA FORENSE CONCLUSIVA ED ESTRAZIONE")
        lbl_rep.setStyleSheet("color: #FFD600; font-weight: bold;")
        r_layout.addWidget(lbl_rep)

        self.txt_final_report = QPlainTextEdit()
        self.txt_final_report.setReadOnly(True)
        self.txt_final_report.setFont(QFont("Consolas", 9))
        self.txt_final_report.setStyleSheet("background-color: #1E202B; border: 1px solid #2E3144; color: #E0E2EC;")
        r_layout.addWidget(self.txt_final_report)
        splitter.addWidget(w_right)

        splitter.setSizes([600, 600])

    def _on_backend_changed(self):
        self.combo_model.blockSignals(True)
        self.combo_model.clear()
        if self.rb_gemini.isChecked():
            self.combo_model.addItems(self.GEMINI_MODELS)
            self.combo_model.setCurrentIndex(0)
            self.lbl_key.setVisible(True)
            self.txt_key.setVisible(True)
            self.lbl_key.setText("Gemini API Key:")
            self.btn_verify.setText("🔍 Verifica Chiave & Modello")
            self.lbl_status.setText("Stato: In attesa di verifica chiave Gemini.")
            self.lbl_status.setStyleSheet("color: #8C8FA1; font-style: italic;")
        elif self.rb_ollama.isChecked():
            self.combo_model.addItems(self.OLLAMA_MODELS)
            self.combo_model.setCurrentIndex(0)
            self.lbl_key.setVisible(False)
            self.txt_key.setVisible(False)
            self.btn_verify.setText("🔍 Verifica Server Ollama")
            self.lbl_status.setText("Stato: Pronto a verificare Ollama locale (porta 11434).")
            self.lbl_status.setStyleSheet("color: #8C8FA1; font-style: italic;")
        else:
            self.combo_model.addItem("heuristic-rules")
            self.combo_model.setCurrentIndex(0)
            self.lbl_key.setVisible(False)
            self.txt_key.setVisible(False)
            self.btn_verify.setText("🔍 Verifica Motore")
            self.lbl_status.setText("Stato: Motore euristico integrato offline (100% deterministico).")
            self.lbl_status.setStyleSheet("color: #00FF66; font-style: italic;")
        self.combo_model.blockSignals(False)
        self.save_settings()

    def _on_model_or_key_changed(self):
        if self.rb_gemini.isChecked():
            self.lbl_status.setText("Stato: Modello o chiave modificati. Fai clic su 'Verifica Chiave' per validare.")
            self.lbl_status.setStyleSheet("color: #FFD600; font-style: italic;")
        elif self.rb_ollama.isChecked():
            self.lbl_status.setText("Stato: Modello Ollama modificato. Fai clic su 'Verifica' per controllare se è scaricato.")
            self.lbl_status.setStyleSheet("color: #FFD600; font-style: italic;")
        self.save_settings()

    def _on_verify_key_clicked(self):
        if self.rb_gemini.isChecked():
            backend = "gemini"
            model = self.combo_model.currentText().strip() or "gemini-2.0-flash"
            key = self.txt_key.text().strip()
            if not key:
                QMessageBox.warning(self, "Chiave Mancante", "Incolla la tua chiave API Google Gemini prima di verificare.")
                return
        elif self.rb_ollama.isChecked():
            backend = "ollama"
            model = self.combo_model.currentText().strip() or "qwen2.5-coder:14b"
            key = ""
        else:
            backend = "heuristic"
            model = "heuristic-rules"
            key = ""

        self.btn_verify.setEnabled(False)
        self.lbl_status.setText("Verifica connessione e compatibilità modello in corso...")
        self.lbl_status.setStyleSheet("color: #00E5FF; font-weight: bold;")

        self.validator_thread = KeyValidatorThread(backend, model, key)
        self.validator_thread.result_signal.connect(self._on_validation_result)
        self.validator_thread.start()

    def _on_validation_result(self, success: bool, message: str):
        self.btn_verify.setEnabled(True)
        if success:
            self.lbl_status.setStyleSheet("color: #00FF66; font-weight: bold;")
        else:
            self.lbl_status.setStyleSheet("color: #FF5555; font-weight: bold;")
        self.lbl_status.setText(f"Stato: {message}")

    def _on_select_file(self):
        fpath, _ = QFileDialog.getOpenFileName(
            self, "Seleziona Nastro da Analizzare", "",
            "File Nastro (*.csw *.tap);;Tutti i File (*.*)"
        )
        if fpath:
            self.selected_filepath = fpath
            self.lbl_target_file.setText(os.path.basename(fpath))

    def _on_run_agent(self):
        if not self.selected_filepath or not os.path.exists(self.selected_filepath):
            QMessageBox.warning(self, "File Mancante", "Seleziona prima un file .CSW da sottoporre a perizia.")
            return

        # Determine backend
        if self.rb_gemini.isChecked():
            backend = "gemini"
            key = self.txt_key.text().strip()
            model = self.combo_model.currentText().strip() or "gemini-2.0-flash"
        elif self.rb_ollama.isChecked():
            backend = "ollama"
            key = ""
            model = self.combo_model.currentText().strip() or "qwen2.5-coder:14b"
        else:
            backend = "heuristic"
            key = ""
            model = "heuristic-rules"

        self.txt_live_log.clear()
        self.txt_final_report.clear()
        self.progress_bar.setVisible(True)
        self.btn_run.setEnabled(False)

        # Build agent
        agent = ForensicAgent(backend=backend, api_key=key, model=model)

        # Start thread
        self.worker_thread = AgentWorkerThread(agent, self.selected_filepath)
        self.worker_thread.progress_signal.connect(self._on_agent_progress)
        self.worker_thread.finished_signal.connect(self._on_agent_finished)
        self.worker_thread.start()

    def _on_agent_progress(self, msg: str):
        self.txt_live_log.appendPlainText(msg)

    def _on_agent_finished(self, result: dict):
        self.progress_bar.setVisible(False)
        self.btn_run.setEnabled(True)
        report = result.get("report", "Perizia terminata.")
        tokens = result.get("tokens_used", 0)

        summary_banner = f"--- RISULTATO INDAGINE (Token Utilizzati: {tokens}) ---\n\n"
        self.txt_final_report.setPlainText(summary_banner + report)
