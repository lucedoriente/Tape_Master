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

## 2. Specifiche Tecniche e Standard Supportati (Architettura Modulare v2 — 13 Piattaforme)

L'apparato supporta l'emulazione, l'acquisizione, la diagnosi e il recupero del segnale per tutte le 13 principali famiglie retrocomputing e standard fisici a nastro:

| # | Standard di Codifica & Piattaforma | Meccanismo di Codifica & Frequenze di Lavoro | Risoluzione Temporale | Note Elettroniche e Hardware di Interfaccia |
| :---: | :--- | :--- | :---: | :--- |
| **01** | **Commodore C2N**<br>(PET, VIC-20, C64, C128, C16, Plus/4) | Durata intervallo tra fronti negativi (Short: $352\text{ µs}$, Medium: $512\text{ µs}$, Long: $672\text{ µs}$) | $\le 1\text{ }\mu\text{s}$ | Connettore edge $3.96\text{ mm}$ + Mini-DIN 8. Linee `READ`, `WRITE`, `MOTOR` (PNP 5V), `SENSE` a massa. |
| **02** | **Atari SIO Tape**<br>(400, 800, XL, XE — Registratore 410, 1010, XC12) | Asynchronous Serial FSK (5327 baud, Mark $3995\text{ Hz}$, Space $5327\text{ Hz}$) + Traccia audio analogica stereo | $\le 500\text{ ns}$ | Presa proprietaria SIO 13 pin. Linee seriali `DATA IN`, `DATA OUT`, linea analogica `AUDIO IN` (Pin 11), `MOTOR`. |
| **03** | **Thomson & Olivetti PC 128**<br>(MO5, TO7, TO7/70, MO6, TO8, PC 128) | Modulazione FSK bifase LEP ($4500\text{ Hz}$ / $6300\text{ Hz}$ a 1200 baud o standard $1200/2400\text{ Hz}$) | $\le 1\text{ }\mu\text{s}$ | Presa DIN 5 180°. Linee digitali TTL `READ`, `WRITE`, ingresso ausiliario `AUDIO` e controllo motore `REM`. |
| **04** | **Sinclair ZX Tape**<br>(ZX80, ZX81, Spectrum 16k/48k/128k, +2) | Tono pilota $807\text{ Hz}$, sync pulse e modulazione di periodo ('0': $855\text{ µs}$, '1': $1710\text{ µs}$) | $\le 500\text{ ns}$ | Doppi jack $3.5\text{ mm}$ `EAR` ($1\text{ V}_{\text{pp}}$) e `MIC` attenuato ($100\text{ mV}_{\text{pp}}$) + relè `REMOTE` optoisolato. |
| **05** | **Amstrad CPC**<br>(CPC 464, 472, 664, 6128) | Modulazione a transizione di fase a due toni (1000/2000 baud, semi-periodi da $1000\text{ µs}$ e $500\text{ µs}$) | $\le 500\text{ ns}$ | Presa DIN 5 180°. Linee audio AC `READ`, `WRITE` e relè motore `REM_B`. |
| **06** | **MSX Standard**<br>(MSX 1, MSX 2, MSX 2+, Turbo-R) | Standard Kansas City FSK ($1200\text{ Hz}$ Mark / $2400\text{ Hz}$ Space a 1200/2400 baud) | $\le 1\text{ }\mu\text{s}$ | Presa DIN 8 270°. Linee audio `CMTIN`, `CMTOUT` e controllo motore polarizzato `REM+` / `REM-`. |
| **07** | **Acorn BBC Micro & Atom**<br>(BBC Model A/B, B+, Master 128) | Kansas City / CUTS FSK framing UART (1 start, 8 dati, 2 stop, 300/1200 baud, toni $1200/2400\text{ Hz}$) | $\le 1\text{ }\mu\text{s}$ | Presa DIN 7 270°. Linee audio bilanciate `CASSETTE IN`, `CASSETTE OUT` e controllo motore a relè. |
| **08** | **Tandy CoCo & Dragon**<br>(Color Computer 1/2/3, Dragon 32/64) | Modulazione sinusoidale a due frequenze ($1200\text{ Hz}$ / $2400\text{ Hz}$ a 1500 baud) | $\le 1\text{ }\mu\text{s}$ | Presa DIN 5 180°. Uscita/ingresso audio `READ`/`WRITE` e relè remoto controllo motore. |
| **09** | **Texas Instruments TI-99/4A**<br>(TI-99/4, TI-99/4A) | Modulazione a zero-crossing bicanale ($1379\text{ Hz}$ '0' / $1953\text{ Hz}$ '1' a circa 700 baud) | $\le 1\text{ }\mu\text{s}$ | Presa DE-9 Femmina. Gestione registratore primario/secondario `CS1`/`CS2`, `AUDIO_GATE` e `TAPE_IN`. |
| **10** | **Apple II Series**<br>(Apple ][, ][+, //e, //c) | Zero-crossing pulse length a ciclo singolo ($1\text{ kHz}$ '0' / $2\text{ kHz}$ '1' a ~1500 baud) | $\le 1\text{ }\mu\text{s}$ | Doppi jack audio $3.5\text{ mm}$ `CASSOUT` (Read) e `CASSIN` (Write). |
| **11** | **Oric Series**<br>(Oric 1, Oric Atmos, Telestrat) | Leader tone ad onda quadra ($1200/2400\text{ Hz}$) e bit sincroni a periodo variabile (300/2400 baud) | $\le 500\text{ ns}$ | Presa DIN 7 270°. Linee `READ`, `WRITE` e relè comando motore `REM_B`. |
| **12** | **Sharp MZ Series**<br>(MZ-80K/A/B, MZ-700, MZ-800) | Segnale PWM ad onda quadra (1200 baud, bit a duty cycle differenziato) sia analogico che logico | $\le 500\text{ ns}$ | Doppi jack $3.5\text{ mm}$ audio + Header 9 poli interno CMT (8255 TTL puro per `READ`, `WRITE`, `MOTOR`, `SENSE`). |
| **13** | **Raw Head Stereo Digitizer**<br>(Banco di Taratura e Restauro) | Preamplificazione strumentale a basso rumore ($0.5\text{ mV}_{\text{rms}} \dots 5\text{ mV}_{\text{rms}}$) dai traferri testina magnetica | Real-time ADC dual-track | Morsettiera a vite Phoenix + Doppi jack $3.5\text{ mm}$ L/R. Regolazione azimut via VU-meter e DIP switch d'impedenza. |

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

## 4. Requisiti di Interfaccia Fisica (Architettura Modulare v2)
Nell'architettura v2, l'interfaccia fisica verso il mondo esterno non è più limitata a singoli connettori saldati sulla scheda madre, ma è interamente demandata al **Bus Universale a 40 Pin** (`J5` Mainboard $\leftrightarrow$ `J1` Cartuccia) e alla famiglia delle **13 Cartucce di Espansione**:
* **Bus Cartuccia 40 Pin (`J5`)**: Boxed header $2 \times 20$ ad angolo retto con alimentazione a 5V e 3.3V, bus I2C per auto-identificazione plug & play (EEPROM 24C02), linee di controllo motore bidirezionali, canali DAC analogici e trigger digitali PIO.
* **Porte Vintage Dedicate sulle Cartucce**:
  - **Commodore C2N (#01)**: Connettore a pettine card edge $3.96\text{ mm}$ (0.156") a 6 poli + Mini-DIN 8 femmina (C16/Plus4).
  - **Atari SIO (#02)**: Presa proprietaria SIO 13 poli orizzontale.
  - **Thomson / PC 128 (#03)**: Presa circolare DIN 5-pin 180° CUI SDS-50J.
  - **Sinclair ZX Spectrum (#04)**: Doppi jack $3.5\text{ mm}$ CUI SJ1-3525N (`EAR` / `MIC`) + header relè `REMOTE`.
  - **Amstrad CPC (#05)**: Presa circolare DIN 5-pin 180° CUI SDS-50J.
  - **MSX Standard (#06)**: Presa circolare DIN 8-pin 270° CUI SDS-80J.
  - **Acorn BBC Micro (#07)**: Presa circolare DIN 7-pin 270° CUI SDS-70J.
  - **Tandy CoCo / Dragon (#08)**: Presa circolare DIN 5-pin 180° CUI SDS-50J.
  - **Texas Instruments TI-99/4A (#09)**: Presa D-Sub DE-9 Femmina 9 poli.
  - **Apple II (#10)**: Doppi jack $3.5\text{ mm}$ CUI SJ1-3525N (`CASSOUT` / `CASSIN`).
  - **Oric Atmos (#11)**: Presa circolare DIN 7-pin 270° CUI SDS-70J.
  - **Sharp MZ (#12)**: Doppi jack $3.5\text{ mm}$ CUI SJ1-3525N + Header 9 pin CMT interno.
  - **Stereo Digitizer (#13)**: Morsettiera a vite Phoenix Contact passo 2.54 mm + doppi jack $3.5\text{ mm}$ L/R.
* **Doppia Connettività a Bordo di Ogni Cartuccia**: Ciascuna cartuccia monta in parallelo al connettore d'epoca un **pin-header maschio passo $2.54\text{ mm}$** con serigrafia chiara di ogni segnale, pensato per collaudo a banco, collegamenti volanti con analizzatore logico e oscilloscopio.

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

### C. Hand-Off e Tabella Connettori Ufficiali Cartucce su Bus 40 Pin
Per tutte le 12 cartucce target, le specifiche dei connettori adottano i seguenti codici di acquisto ufficiali (documentati in `docs/Tape_Master_Connectors_BOM_Purchasing_Guide.md`):
- **Slot Bus Cartuccia Femmina 40P (`J1`)**: Samtec `SSW-120-02-G-D-RA` (Receptacle Femmina 2x20 90°, montaggio a filo scheda con battuta a $Y = 0.00\text{ mm}$, piedinatura 1:1 allineata alla Mainboard).
- **Jack Audio 3.5 mm TRS Orizzontali (`EAR` / `MIC`)**: Same Sky (ex CUI Devices) `SJ1-3525N` a 5 pin con interruttori interni (Mouser: `490-SJ1-3525N`), compatibile anche con le varianti `SJ1-3524N` (4 pin) e `SJ1-3523N` (3 pin).
- **Prese DIN Circolari Orizzontali THT**:
  - DIN 5-Pin 180° (Thomson, Amstrad, CoCo): Same Sky `SDS-50J` (Mouser: `490-SDS-50J`).
  - DIN 7-Pin 270° (Acorn BBC Micro, Oric): Same Sky `SDS-70J` (Mouser: `490-SDS-70J`).
  - DIN 8-Pin 270° (MSX Standard): Same Sky `SDS-80J` (Mouser: `490-SDS-80J`).
  - Mini-DIN 8-Pin (Commodore Plus/4): Same Sky `MD-80` (Mouser: `490-MD-80`).
- **Connettore Card Edge 3.96 mm (Commodore C2N)**: EDAC `306-006-520-102` / Sullins `EBC06DRAH`.
- **Presa D-Sub DE-9 Femmina 90° (TI-99/4A)**: Amphenol ICC `L77SDE09S` / TE Connectivity `5747844-4`.

---

### D. Matrice di Collaudo e Sign-Off di Tutte le 13 Cartucce v2 — 100% COMPLETATO
Tutte le 13 cartucce di espansione sono state interamente aggiornate e convalidate con la toolchain ufficiale KiCad 9.0 (`kicad-cli 9.0.0`) e sbrogliate al 100% tramite Freerouting:
* **Connettore Bus Cartuccia `J1`**: sostituito su tutte le schede con il footprint flush `Tape-Master:PinSocket_2x20_P2.54mm_Horizontal_Cartridge` posizionato esattamente a $Y = 0.00\text{ mm}$ con battuta a filo bordo PCB, passo $2.54\text{ mm}$ a 2 file, orientamento $0^\circ$ e mappatura pin-to-pin 1:1 rigorosamente allineata con l'header maschio `J5` della Mainboard.
* **Jack Audio 3.5 mm (`J2` / `J3`)**: aggiornati sulle cartucce Sinclair (#04), Apple II (#10) e Sharp MZ (#12) al footprint universale 5-pin `Tape-Master:Jack_3.5mm_CUI_SJ1-3525N_Horizontal` compatibile sia con i jack Same Sky `SJ1-3525N` sia con i diffusissimi cloni cinesi AliExpress `PJ-324M`.
* **Prese DIN**: verificate e convalidate con footprint `Tape-Master:DIN-*` conformi alle specifiche CUI Devices `SDS-50J`, `SDS-70J`, `SDS-80J` e codici cinesi AliExpress `DS-5-01`, `DS-7-101`, `DS-8-01`.

| Cartuccia | Piattaforma Vintage | ERC Violations | DRC Violations | Unconnected Items | Parity Issues | Connettori Esterni Validati | Esito Collaudo |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- | :---: |
| **#01** | `Commodore C2N` | **0** | **0** | **0** | **0** | Card Edge 3.96mm + Mini-DIN 8 | **PASS** |
| **#02** | `Atari SIO` | **0** | **0** | **0** | **0** | Atari SIO 13P + Test Header | **PASS** |
| **#03** | `Thomson / Olivetti PC128` | **0** | **0** | **0** | **0** | DIN-5 180° + Test Header | **PASS** |
| **#04** | `Sinclair ZX Spectrum` | **0** | **0** | **0** | **0** | Jack 3.5mm EAR/MIC (SJ1-3525N/PJ-324M) | **PASS** |
| **#05** | `Amstrad CPC` | **0** | **0** | **0** | **0** | DIN-5 180° + Test Header | **PASS** |
| **#06** | `MSX Standard` | **0** | **0** | **0** | **0** | DIN-8 270° + Test Header | **PASS** |
| **#07** | `Acorn BBC Micro` | **0** | **0** | **0** | **0** | DIN-7 270° + Test Header | **PASS** |
| **#08** | `Tandy CoCo / Dragon` | **0** | **0** | **0** | **0** | DIN-5 180° + Test Header | **PASS** |
| **#09** | `TI-99/4A` | **0** | **0** | **0** | **0** | D-Sub DE-9 Femmina + Test Header | **PASS** |
| **#10** | `Apple II / IIe` | **0** | **0** | **0** | **0** | Jack 3.5mm IN/OUT (SJ1-3525N/PJ-324M) | **PASS** |
| **#11** | `Oric Atmos` | **0** | **0** | **0** | **0** | DIN-7 270° + Test Header | **PASS** |
| **#12** | `Sharp MZ` | **0** | **0** | **0** | **0** | Jack 3.5mm + Header CMT 9P | **PASS** |
| **#13** | `Raw Head Stereo Digitizer` | **0** | **0** | **0** | **0** | Terminal Block + Dual Jack 3.5mm SMD | **PASS** |

#### E. Accoppiamento Meccanico ed Ergonomia di Inserimento Cartucce
* **Accoppiamento Complanare a 90°**: Le cartucce si innestano estendendosi orizzontalmente all'indietro rispetto alla scheda madre, mantenendo i due PCB complanari su un unico piano di lavoro. L'header maschio boxed `J5` della Mainboard accoglie la presa femmina `J1` delle cartucce, con i due intagli laterali ($6.0\text{ mm} \times 8.0\text{ mm}$) che fanno da battuta e alloggiamento per le leve di blocco.
* **Ergonomia Serigrafica a 180°**: Titolo e copyright (`© 2026 by Alessio Iodice`) sono posizionati sul bordo inferiore delle cartucce e ruotati di $180^\circ$, risultando orientati dritti verso l'operatore quando la scheda è inserita.

#### F. Matrice di Certificazione Pinout Cartucce vs Datasheet di Fabbrica
Tutti i connettori fisici delle 13 cartucce sono stati collaudati e certificati 1:1 contro i datasheet e i manuali di servizio originali:
* **#01 Commodore C2N**: Card Edge 6P / Mini-DIN 8 / Header (1: GND, 2: +5V, 3: MOTOR, 4: READ, 5: WRITE, 6: SENSE) $\rightarrow$ **100% Conforme**.
* **#02 Atari SIO**: Receptacle SIO 13P / Header (1: CLK_IN, 2: CLK_OUT, 3: DATA_IN, 4: GND, 5: DATA_OUT, 6: GND, 7: COMMAND, 8: MOTOR, 9: PROCEED, 10: +5V, 11: AUDIO_IN, 12: +12V, 13: INTERRUPT) $\rightarrow$ **100% Conforme**.
* **#03 Thomson / PC 128**: DIN-5 180° / Header (1: REM, 2: GND, 3: AUDIO, 4: READ, 5: WRITE) $\rightarrow$ **100% Conforme**.
* **#04 Sinclair Spectrum**: Jack EAR/MIC 3.5mm / Header (Tip/Ring Signal, Sleeve GND; Relay REM A/B) $\rightarrow$ **100% Conforme**.
* **#05 Amstrad CPC**: DIN-5 180° / Header (1: GND, 2: GND, 3: REM_B, 4: READ, 5: WRITE) $\rightarrow$ **100% Conforme**.
* **#06 MSX Standard**: DIN-8 270° / Header (1..3: GND, 4: CMTOUT, 5: CMTIN, 6: REM+, 7: REM-, 8: GND) $\rightarrow$ **100% Conforme**.
* **#07 BBC Micro**: DIN-7 270° / Header (1, 4: OUT, 2, 7: GND, 3: IN, 6: REM_A) $\rightarrow$ **100% Conforme**.
* **#08 Tandy CoCo / Dragon**: DIN-5 180° / Header (1, 2: GND, 3: REM_B, 4: READ, 5: WRITE) $\rightarrow$ **100% Conforme**.
* **#09 TI-99/4A**: DE-9 Femmina / Header (1: CS1_MOTOR+, 2, 5, 7, 9: GND, 3: CS2_OUT, 4: AUDIO_GATE, 6: CS2_MOTOR+, 8: TAPE_IN) $\rightarrow$ **100% Conforme**.
* **#10 Apple II**: Jack 3.5mm CASSOUT/CASSIN / Header (Tip: Data, Sleeve: GND) $\rightarrow$ **100% Conforme**.
* **#11 Oric Atmos**: DIN-7 270° / Header (1: REM_B, 2: GND, 3: READ, 4, 5: WRITE) $\rightarrow$ **100% Conforme**.
* **#12 Sharp MZ**: Jack 3.5mm READ/WRITE / Header 9P CMT MZ-700/800 (1: WRITE, 2: READ, 3, 9: GND, 4: MOTOR, 5: SENSE, 6: +5V, 7: WRITE, 8: READ TTL) $\rightarrow$ **100% Conforme**.
* **#13 Stereo Digitizer**: Terminal Block Phoenix / Dual Jack 3.5mm (L/R raw differential & unbalanced magnetic head inputs) $\rightarrow$ **100% Conforme**.

