# HANDOFF ARCHITETTURALE E SPECIFICHE TECNICHE
# Progetto: Tape / Cassette Master Exerciser & Signal Digitizer
**Autore / Hardware Designer**: Alessio Iodice (<alessio67@gmail.com>)  
**Contesto Operativo**: MuDIsTInf (Museo Didattico di Storia dell'Informatica Padova) & Laboratorio di Restauro  
**Toolchain Target**: KiCad 9.0 (`version 20250114`)  
**Licenza**: CC BY-NC-SA 4.0  

---

## 1. Obiettivo e Giustificazione Tecnica
I supporti a nastro magnetico (audiocassette a nastro ferro e cromo) prodotti tra gli anni '70 e '90 subiscono un'inesorabile degradazione chimico-fisica:
* **Idrolisi del legante (*Sticky-Shed Syndrome*)**: l'ossido magnetico si sfalda o produce attrito eccessivo sulla testina.
* **Perdita di magnetizzazione e fruscio**: il rapporto segnale/rumore (SNR) si riduce drasticamente.
* **Disallineamento dell'Azimut**: la vite di regolazione della testina del registratore spesso non è allineata con l'inclinazione usata durante l'incisione originaria, provocando la perdita delle alte frequenze (attenuazione dei fronti d'onda del segnale digitale FSK o PWM).
* **Usura nei Musei**: Far girare nastri originali rari nelle mostre interattive è improponibile per il rischio di strappi e usura della meccanica.

Questo strumento assolve a un duplice ruolo:
1. **Banco di Recupero & Taratura Testina (Analog Ingest)**: Preamplificatore analogico a bassissimo rumore con filtro passa-banda attivo, trigger a soglia adattiva e **indicatore grafico di fase/ampiezza in tempo reale** per consentire la taratura micrometrica della vite di azimut prima del dumping digitale.
2. **Virtual Tape Deck / Exerciser (Digital Player)**: Generatore hardware ad alta precisione di segnali digitali a nastro (emula un Datassette Commodore C2N, un registratore Sinclair o un registratore Apple II) riproducendo file `.TAP`, `.TZX`, `.CAS` da MicroSD senza toccare i nastri originali.

---

## 2. Specifiche Tecniche e Standard Supportati

| Standard di Codifica | Piattaforme Target | Meccanismo di Codifica | Risoluzione Temporale | Note Hardware |
| :--- | :--- | :--- | :--- | :--- |
| **Commodore C2N** | PET, VIC-20, C64, C16 | Durata intervallo tra fronti (Short, Medium, Long: 352 µs, 512 µs, 672 µs) | $\le 1\text{ }\mu\text{s}$ | Linee `READ`, `WRITE`, `MOTOR`, `SENSE` |
| **Sinclair ZX Tape** | ZX80, ZX81, Spectrum 16k/48k/128k | Onde quadre a semi-periodo variabile (Leader tone, Sync, Bit 0/1) | $\le 500\text{ ns}$ | Uscita attenuata a livello microfonico ($100\text{ mV}_{\text{pp}}$) ed EAR ($1\text{ V}_{\text{pp}}$) |
| **Kansas City Standard / CUTS** | Acorn BBC, Nascom, KIM-1, Apple II | FSK $1200\text{ Hz}$ (Mark) / $2400\text{ Hz}$ (Space) | $\le 2\text{ }\mu\text{s}$ | Modulatore e demodulatore FSK hardware |
| **Apple II Cassette** | Apple II, II+, IIe | Zero-crossing pulse length ($1\text{ kHz} \dots 2\text{ kHz}$) | $\le 1\text{ }\mu\text{s}$ | Ingresso/uscita jack $3.5\text{ mm}$ audio |

---

## 3. Architettura Circuitale e Componentistica Chiave

```
                      [CATENA ANALOGICA DI INGESTIONE]
[Ingresso Testina / Line-In] 
           │
           ├──> [Op-Amp Basso Rumore NE5532 / OPA2134] (Guadagno Regolabile 20dB..60dB)
           ├──> [Filtro Passa-Banda Attivo 300 Hz .. 12 kHz (Sallen-Key 4° ordine)]
           ├──> [Peak Detector & VU Meter Driver] ──────────> [Bargraph LED Azimut / ADC MCU]
           └──> [Comparatore Veloce con Isteresi Regolabile] ──> [MCU Capture Timer (RP2040 / STM32)]
                                                                           │
                                                                           ├──> MicroSD (.TAP/.TZX)
                      [GENERATORE VIRTUAL TAPE / EXERCISER]               │
[Driver Uscita C2N Open-Collector 7406] <── [Timer PWM Hardware] <─────────┘
[Attenuatore Passivo Uscita EAR/MIC]   <── [DAC / Timer PWM Filtrato]
```

### A. Front-End Analogico & Taratura Azimut
* **Preamplificatore a Basso Rumore**: Operazionale audio di precisione (`OPA2134` o `NE5532`) con guadagno configurabile tramite potenziometro multigiro o potenziometro digitale I2C (`MCP41010`) da $20\text{ dB}$ a $60\text{ dB}$.
* **Filtro Passa-Banda Attivo (300 Hz – 12 kHz)**: Rimuove il ronzio di rete a 50/100 Hz indotto dai motori e le componenti ultrasoniche/bias di registrazione non udibili.
* **Peak Detector e Indicatore di Azimut Ottico**: Raddrizzatore di precisione a diodi ideali che alimenta un display OLED o un bargraph a 10 LED (`LM3914` o campionato da ADC). Ruotando la vite di azimut della testina, l'operatore osserva istantaneamente il picco di ampiezza e di nitidezza delle alte frequenze sul segnale di sincronismo (*leader tone*), garantendo la taratura ottimale prima di avviare il riversamento del nastro.
* **Digitizer Schmitt Trigger**: Comparatore a risposta rapida (`LM393` o `TLV3501`) con soglia di trigger e isteresi regolabili per trasformare l'onda sinusoidale degradata del nastro in impulsi logici a spigolo vivo senza falsi rimbalzi da rumore di fondo.

### B. Emulatore Hardware Virtual Tape (Digital Deck)
* **MCU Core**: **Raspberry Pi Pico (RP2040)**:
  * La macchina a stati programmabile **PIO** consente di generare le temporizzazioni dei segnali C2N o Sinclair con precisione di nanosecondi, senza jitter software o interrupt overhead.
  * Interfaccia **MicroSD** SPI per leggere file `.TAP` (Commodore), `.TZX` (Sinclair), `.CAS` (MSX) o file audio `.WAV`.
  * Supporto della linea `MOTOR`: se il computer vintage spegne il motore del registratore (tramite il transistor interno), l'emulatore sospende la riproduzione del file immagine, riprendendola esattamente al fronte successivo (fondamentale per i caricamenti a blocchi multipli di C64 e ZX Spectrum).

---

## 4. Requisiti di Interfaccia Fisica (Connettori)
* **Connettore Edge C2N Commodore**: Connettore a pettine passo $3.96\text{ mm}$ (0.156") a 6 poli (GND, +5V, MOTOR, READ, WRITE, SENSE) per collegarsi direttamente alla porta registratore di PET, VIC-20 e C64.
* **Connettore Mini-DIN 8 / DIN 7**: Per Commodore 16 e Plus/4.
* **Coppia Jack Audio $3.5\text{ mm}$**: `MIC` ed `EAR` con attenuazione selezionabile a jumper (Mic level $-40\text{ dB}$, Line level $0\text{ dB}$).
* **Jack $2.5\text{ mm}$**: Linea `REMOTE` a relè optoisolato per il controllo motore standard dei registratori Sinclair e portatili generici.

---

## 5. Checklist di Validazione
1. 0 violazioni ERC e DRC su KiCad 9.0.
2. Risposta in frequenza del filtro analogico verificata con ngspice: banda passante piatta tra $400\text{ Hz}$ e $10\text{ kHz}$, attenuazione $> 30\text{ dB}$ a $50\text{ Hz}$.
3. Test di caricamento da SD su Commodore 64 reale: validazione di software multi-blocco con gestione linea motore.

---

## 6. Evoluzione Versione 2 (Architettura Modulare a Scheda Figlia e Slot Cartuccia 40 Pin)
Nella Versione 1 a scheda singola è emersa una sovrapposizione meccanica tra lo sbalzo inferiore dell'OLED da 0.96" e la barra a 10 LED di taratura dell'azimut. Inoltre, l'estrema sensibilità dello stadio analogico per testine a nastro ($1 \dots 2\text{ mV}_{\text{rms}}$) consiglia la separazione fisica tra interfaccia utente rumorosa e stadio di ingresso.

La **Versione 2** adotta una struttura a tre blocchi:
* **Daughterboard 1 (Front Panel UI)**: OLED, Rotary Encoder, 5 pulsanti e barra LED azimut a 10 segmenti, collegata via cavo/connettore IDC dedicato.
* **Mainboard Base**: MCU RP2040, storage microSD, power management ultra-low-noise e front-end analogico schermato.
* **Daughterboard 2 (Target Cartridges su Slot 40 Pin)**: Connettore maschio a $90^\circ$ Boxed Latched con leve di ritegno a $2 \times 20$ pin (passo $2.54\text{ mm}$), comprendente:
  - 8 pin alimentazioni e masse di potenza (`+5V`, `+3.3V`, `V_AUX`, `GND`).
  - 8 pin sezione analogica stereo schermata con masse di guardia alternate (`AGND`, `AUDIO_RAW_L`, `AUDIO_RAW_R`, `AUDIO_DAC_L`, `AUDIO_DAC_R`).
  - 8 pin bus digitale tape (`TAPE_EMU_OUT`, `TAPE_REC_IN`, `MOTOR_SENSE`, `MOTOR_CTRL`, `TAPE_SENSE`, `AUX_GPIO1/2`).
  - 11 pin bus smart cartuccia ed espansione ad alta velocità (`I2C_SDA/SCL`, `CART_DETECT_N`, `CART_IRQ_N`, `CART_RESET_N`, bus `SPI` dedicato a 4 pin, bus `UART` a 2 pin).
  - 5 pin di riserva libera (`SPARE_1` .. `SPARE_5`).

Il dettaglio completo dei pin e delle specifiche costruttive è documentato in:
`docs/Tape_Master_v2_Hardware_Architecture.md`.



---

## 7. Stato Attuativo v2: Collaudo e Sign-Off di Mainboard Base e UI Daughterboard

### A. Front Panel UI Daughterboard (`kicad/v2/UI_Panel/`) — 100% COMPLETATO
* **Schematico (`Tape_Master_UI_Panel.kicad_sch`)**:
  - Validazione `kicad-cli sch erc`: **0 errori, 0 avvisi (0 violazioni ERC)**.
  - Componenti integrati: Display OLED I2C 128x64, Rotary Encoder ALPS con switch centrale, 5 pulsanti di navigazione trasporto tape con resistenze di pull-up e debouncing, Bargraph a 10 segmenti LED per azimut con doppi registri a scorrimento 74HC595 su bus SPI dedicato, connettore IDC-20 polarizzato verso la scheda madre.
* **Layout e Routing PCB (`Tape_Master_UI_Panel.kicad_pcb`)**:
  - Dimensioni: $110.0\text{ mm} \times 65.0\text{ mm}$, 2 layer FR4 con piani di massa GND continui sia su F.Cu che su B.Cu.
  - Validazione `kicad-cli pcb drc --schematic-parity`: **0 violazioni DRC, 0 unconnected, 0 parity issues**.
* **Deliverable di Produzione**:
  - Schema vettoriale: `Tape_Master_UI_Panel.pdf`
  - Render 3D Top: `Tape_Master_UI_Panel_Top.png` (1920x1080)
  - Render 3D Bottom: `Tape_Master_UI_Panel_Bottom.png` (1920x1080)
  - Modello solido CAD 3D: `Tape_Master_UI_Panel.step`

---

### B. Mainboard Base (`kicad/v2/Mainboard/`) — 100% COMPLETATO
* **Schematico (`Tape_Master_Mainboard.kicad_sch`)**:
  - Validazione `kicad-cli sch erc`: **0 errori, 0 avvisi (0 violazioni ERC)**.
  - Componenti integrati:
    - **MCU Core**: Raspberry Pi Pico (RP2040) con connettore micro-USB e piedinatura THT (`Tape-Master:RaspberryPi_Pico_Common_THT`).
    - **Power Stage Ultra-Low Noise**: USB-C GCT USB4105-xx-A a filo bordo sinistro con fusibile autoripristinante Polyfuse 1.1A, diodo Schottky di protezione e regolatore LDO a basso rumore AP2112K-3.3V filtrato con perla di ferrite e condensatori al tantalio/ceramici.
    - **Storage**: Slot MicroSD Hirose DM3D-SF push-pull a filo bordo sinistro alimentato a 3.3V con terminazioni di pull-up e bus SPI hardware dedicato.
    - **Front-End Analogico & Azimut**: Stadio preamplificatore a basso rumore con rail-to-rail op-amp TLV2372, trimmer di guadagno multigiro, circuito raddrizzatore/peak-detector con diodo Schottky e costante di tempo RC calibrata, canale ADC RP2040 per visualizzazione dinamica del picco di azimut, comparatore rapido LM393 con trimmer di soglia e isteresi per digitalizzazione diretta del segnale tape audio. Test point THT per PREAMP, FILTERED, DIGITIZED e AGND.
    - **Header Connessione UI Panel**: Header maschio IDC-20 pin polarizzato (J4) con corrispondenza 1:1 pin-to-pin con la UI Daughterboard (alimentazione 3.3V, bus I2C, SPI, linee tasti di trasporto e linea `/RESET_L` su Pin 20). Il pulsante di Reset locale (SW1) è stato rimosso dalla Mainboard ed è delegato unicamente al tasto Reset SW6 sul pannello frontale.
    - **Slot Cartuccia Connettore 40 Pin (J5)**: Boxed Header a $90^\circ$ ad alta densità a due file passo 2.54 mm, orientato verso il bordo posteriore e a filo scheda per consentire l'inserimento orizzontale e l'uso agevole con case/enclosure. Pinout standardizzato comprensivo di alimentazioni protette, bus analogico differenziale, bus digitale tape, bus smart I2C/SPI/UART e 5 linee di espansione libera.
* **Layout e Routing PCB (`Tape_Master_Mainboard.kicad_pcb`)**:
  - Dimensioni: $125.0\text{ mm} \times 95.0\text{ mm}$, 2 layer FR4 con piani di massa continui F.Cu e B.Cu e 4 fori di fissaggio M3 agli angoli.
  - Connettori a filo scheda: USB-C (J1) e MicroSD (J2) sporgenti/a filo su bordo sinistro ($X = 0$), Slot Cartuccia 40 pin (J5) ad angolo retto a filo bordo posteriore ($Y = 0$).
  - Routing automatico completato al 100% in modalità headless tramite Freerouting (690 tracce e vie, 0 net incomplete, score di sbroglio 973.82) con micro-accordatura per clearance ottimale ($> 0.24\text{ mm}$).
  - Validazione `kicad-cli pcb drc --schematic-parity`: **0 violazioni DRC, 0 unconnected, 0 parity issues**.
* **Deliverable di Produzione**:
  - Schema vettoriale: `Tape_Master_Mainboard.pdf`
  - Render 3D Top: `Tape_Master_Mainboard_Top.png` (1920x1080)
  - Render 3D Bottom: `Tape_Master_Mainboard_Bottom.png` (1920x1080)
  - Modello solido CAD 3D: `Tape_Master_Mainboard.step` (con modello 3D Pico integrato)

---

### C. Hand-Off per la Prossima Sessione: Progettazione Cartucce su Bus 40 Pin
Con il congelamento e il sign-off definitivo di Mainboard Base e UI Daughterboard, l'infrastruttura centrale v2 è pronta e validata. Nella prossima chat verranno realizzate le cartucce modulari target:
1. **Cartuccia C2N Commodore 64 / VIC-20 / PET**: Connettore a pettine edge card $3.96\text{ mm}$ (0.156"), buffer open-collector 7406, sensing motore a transistor.
2. **Cartuccia C16 / Plus4**: Connettore Mini-DIN 8 / DIN 7 poli con commutazione logica e alimentazione dedicata.
3. **Cartuccia Sinclair ZX Spectrum / MSX / Amstrad CPC**: Jack audio $3.5\text{ mm}$ EAR/MIC stereo/mono con attenuatori passivi a jumper e relè optoisolato per linea REMOTE ($2.5\text{ mm}$).
4. **Cartuccia Atari SIO (400/800/XL/XE)**: Connettore SIO proprietario con demodulatore FSK hardware integrato.
