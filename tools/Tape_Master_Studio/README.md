# Tape Master Studio v2.0 — Forensic Tape Lab & Hardware Suite

Applicazione desktop ufficiale per computer (Windows, macOS, Linux) di controllo, analisi del segnale, taratura meccanica e recupero forense dei dati per **Tape Master Exerciser & Signal Digitizer v2.0**.

---

## 1. Funzionalità Chiave

1. **Auto-Discovery USB Plug & Play**: Riconoscimento automatico del Raspberry Pi Pico via USB CDC Serial (`2E8A:000A`).
2. **VU-Meter Azimut Digitale ad Alta Risoluzione**: Riproduce fedelmente la barra a 10 segmenti LED della scheda frontale, visualizzando la tensione istantanea in millivolt per una taratura micrometrica della vite della testina.
3. **Oscilloscopio Impulsi & Istogramma Jitter**: Visualizzazione dei fronti d'onda a 60 FPS con accelerazione hardware grafica, identificazione automatica dei picchi di frequenza e calcolo di Wow & Flutter.
4. **Controlli Registratore Virtuale**: Comandi remoti di riproduzione, registrazione, forzatura manuale del relè motore e selezione immagini `.TAP`, `.TZX`, `.CSW`.
5. **Smart Cartridge Inspector**: Lettura in tempo reale della EEPROM `24C02` della cartuccia inserita con mapping segnali e piedinatura a banco.
6. **Forensic Multi-Pass Reconstruction**: Fusione probabilistica a maggioranza di letture multiple dello stesso nastro degradato per ricostruire blocchi privi di errori.
7. **Accelerazione Hardware GPU NVIDIA (Opzionale)**: Se disponibile una scheda grafica dedicata (es. RTX 3060), accelera i calcoli FFT, la deconvoluzione e i filtri neurali anti-fruscio tramite CUDA.

---

## 2. Requisiti e Avvio

### Esecuzione Diretta con Python:
```bash
cd tools/Tape_Master_Studio
pip install -r requirements.txt
python tape_master_studio.py
```

### Generazione Eseguibile Standalone `.exe` (PyInstaller):
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="Tape_Master_Studio" tape_master_studio.py
```
Verrà generato un unico file `dist/Tape_Master_Studio.exe` pronto per il doppio clic su qualsiasi PC Windows senza installare librerie.
