# Regole di Progetto — Tape Master Exerciser & Signal Digitizer v2

Questo documento definisce le regole architetturali ed elettroniche specifiche ed esclusive per il progetto **Tape Master** (Tape/Cassette Master Exerciser & Signal Digitizer). Queste regole integrano le regole globali utente e si applicano a tutti i file della Mainboard, della Daughterboard (UI Panel) e delle 12 Cartucce di espansione.

---

## 1. Centralizzazione della Diagnostica sulla Daughterboard (Front Panel UI)
- **Front-End Utente Unico**: L'intera interfaccia operatore, il monitoraggio in tempo reale, il display OLED e i LED diagnostici sono centralizzati esclusivamente sulla Daughterboard frontale (`Tape_Master_UI_Panel`).
- **Divieto di LED di Stato Duplicati sulle Cartucce**:
  - Le due schede (Mainboard e Cartuccia) sono perfettamente complanari e parallele (grazie all'accoppiamento dei due connettori maschio/femmina a 90°), con la cartuccia che estende orizzontalmente all'indietro la scheda madre.
  - La centralizzazione sull'UI Panel frontale garantisce la visione diretta e immediata per l'operatore, mentre la cartuccia all'indietro risulterebbe coperta dai connettori e cavi SIO o dal case.
  - È pertanto **vietato duplicare sulle cartucce i LED di attività dati o stato motore** (`READ`, `WRITE`, `MOTOR`, `SENSE`, ecc.).
  - Lo spazio sul PCB delle cartucce deve essere riservato a:
    1. Connettori fisici (porta proprietaria per cavo e pin-header maschio passo 2.54 mm per test a banco);
    2. Buffer di traslazione di livello (5V vs 3.3V) e filtri audio;
    3. Protezioni ESD / TVS su tutte le linee esposte;
    4. EEPROM I2C `24C02` di auto-riconoscimento Smart Plug&Play.
  - *Unica eccezione ammessa*: È consentito sulla cartuccia esclusivamente un micro-LED opzionale di monitoraggio hardware dell'alimentazione esterna proveniente dal computer vintage collegato (es. `+5V_SIO_OK` per Atari o `+5V_HOST` per verificare l'erogazione della console a macchina accesa).

---

## 2. Standardizzazione Universale dei LED di Stato (UI Panel)
Per garantire immediata leggibilità e coerenza con tutte le 12 piattaforme retrocomputing supportate (evitando le confusioni di verso tipiche tra standard diversi, es. `READ` vs `DATA IN`, `WRITE` vs `DATA OUT`, `EAR` vs `MIC`), i 5 LED di stato individuali sul pannello frontale (`Tape_Master_UI_Panel`) devono obbligatoriamente adottare la seguente dicitura standardizzata sia nello schema elettrico sia nella serigrafia PCB (`F.Silkscreen`):

| Riferimento | Colore | Label Serigrafata Standard | Funzione Universale di Sistema | Mapping Segnali per Piattaforma |
| :---: | :---: | :---: | :--- | :--- |
| **D2** | Verde | **`PLAY`** | Riproduzione verso il computer / trasmissione dati / emulazione nastro attiva | • **Commodore**: Linea `READ` attiva<br>• **Atari SIO**: Linea `DATA IN` (Pin 3)<br>• **Sinclair / Apple II**: Uscita `EAR`<br>• **MSX / Thomson / CoCo**: `CASSETTE IN` |
| **D3** | Rosso | **`REC`** | Registrazione dal computer / ricezione dati / acquisizione dump attiva | • **Commodore**: Linea `WRITE` attiva<br>• **Atari SIO**: Linea `DATA OUT` (Pin 5)<br>• **Sinclair / Apple II**: Ingresso `MIC`<br>• **MSX / Thomson / CoCo**: `CASSETTE OUT` |
| **D4** | Giallo | **`MOTOR`** | Linea di controllo trascinamento nastro o relè motore abilitata dal computer | • **Commodore**: Linea `MOTOR` a 5V<br>• **Atari SIO**: Linea `MOTOR` (Pin 8)<br>• **Sinclair / Jack**: Relè `REMOTE` chiuso<br>• **MSX / Thomson**: Linee `REM+` / `REM-` attive |
| **D5** | Blu | **`SIGNAL`** | Rilevamento portante FSK, sincronismo di blocco, impulso di clock o traccia audio stereo | • **Commodore**: Impulsi di clock / feedback `SENSE`<br>• **Atari SIO**: Traccia audio analogica (Pin 11) / Sync<br>• **Sinclair / CUTS**: Leader tone / Portante $1200/2400\text{ Hz}$ |
| **D6** | Verde | **`PWR`** | Alimentazione di sistema attiva (+5V / +3.3V) e microcontrollore operativo | Alimentazione principale di sistema |

### Barra a 10 Segmenti (VU-Meter / Azimut)
- **`D10` $\dots$ `D19`**: **`AZIMUTH / VU-METER`** (8 verdi, 1 giallo, 1 rosso).
- Dedicata esclusivamente alla visualizzazione dell'ampiezza di picco del segnale analogico e alla regolazione micrometrica dell'azimut della testina magnetica (oppure livello volume audio traccia secondaria).

---

## 3. Requisiti di Interfaccia per Tutte le 12 Cartucce
1. **Connettore Bus Universale (`J1`)**: Presa femmina $2 \times 20$ poli ad angolo retto (`Connector_PinSocket_2.54mm:PinSocket_2x20_P2.54mm_Horizontal`) con Pin 26 `CART_DETECT_N` collegato a massa.
2. **Dimensioni Meccaniche e Bordo Scheda**: Profilo standard $74.00\text{ mm} \times 55.00\text{ mm}$ con due intagli laterali su `Edge.Cuts` ($6.0\text{ mm} \times 8.0\text{ mm}$) per l'alloggiamento delle leve di ritenuta del connettore della scheda madre.
3. **Doppia Connettività Esterna**:
   - Connettore proprietario d'epoca per il cavo originale (es. SIO 13P, Mini-DIN 8, Card Edge, DIN 5/7/8, DE-9, Jack);
   - Pin-header maschio passo $2.54\text{ mm}$ in parallelo con serigrafia dettagliata di ogni singolo segnale, per facilitare prove a banco, analizzatori logici e oscilloscopio.
4. **Auto-ID Smart Cartridge**: EEPROM I2C `24C02` (indirizzo `0x50` o `0x51`) su bus `I2C_SDA` e `I2C_SCL` con descrittore hardware conforme.
5. **Ergonomia Serigrafica e Orientamento Cartuccia**:
   - Poiché la cartuccia si inserisce estendendosi orizzontalmente all'indietro rispetto alla scheda madre, i testi identificativi (`Title` e `Copyright © 2026 by Alessio Iodice`) devono essere posizionati sul bordo inferiore e **ruotati di 180°**, in modo da risultare perfettamente orientati e leggibili dall'operatore posto di fronte alla consolle.
   - Tutti i connettori e i pinout esterni devono rispettare al 100% la matrice di certificazione pinout di fabbrica (0 incongruenze).

---

## 4. Consegna Firmware e Binari (.UF2) Ready-to-Flash
- **Zero Compilazione Manuale per l'Utente**: L'utente non deve compilare manualmente il firmware né configurare toolchain complesse per caricare il software sul microcontrollore.
- **Fornitura del Binario Diretto**: A ogni aggiornamento del firmware, deve essere fornito il file binario compilato e pronto all'uso `firmware/bin/tape_master_v2.uf2` pronto da trascinare nella memoria di massa `RPI-RP2` del Raspberry Pi Pico via USB.


