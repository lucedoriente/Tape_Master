# Tape Master v2 — Cartuccia 08: Tandy Color Computer & Dragon 32/64 Tape Interface

| Proprietà | Dettaglio / Valore |
| :--- | :--- |
| **Progetto** | Tape Master Exerciser & Signal Digitizer v2 |
| **Modulo** | Cartuccia Espansione #08 — Tandy CoCo & Dragon 32/64 (`08_Tandy_CoCo_Dragon`) |
| **Piattaforme Compatibili** | Tandy Radio Shack TRS-80 Color Computer (CoCo 1, CoCo 2, CoCo 3), Dragon Data Dragon 32 / Dragon 64, Tandy TRS-80 Model I/III/4 (con cavo DIN-5 a 3 Jack 3.5/2.5mm) |
| **Periferiche Supportate** | Tandy CCR-81, CCR-82, CCR-83, registratori a cassette standard compatibili Dragon Data e TRS-80 |
| **Autore & Hardware Designer** | Alessio Iodice (`alessio67@gmail.com`) |
| **Data di Rilascio** | 2026-11-06 |
| **Revisione** | 2.0 (KiCad 9.0 Nativo) |
| **Licenza** | CC BY-NC-SA 4.0 |
| **Stato Validazione KiCad 9** | **0 Violazioni ERC / 0 Violazioni DRC / 0 Net Non Connesse / 0 Parity Issues** |

---

## 1. Descrizione Architetturale

La **Cartuccia 08: Tandy CoCo & Dragon 32/64** interfaccia il sistema **Tape Master v2** alla porta a cassetta dei personal computer a microprocessore Motorola 6809 della famiglia **Tandy Color Computer (CoCo 1, 2 e 3)** e dei compatibili britannici **Dragon Data (Dragon 32 e 64)**, oltre a garantire la piena compatibilità elettrica con la linea classica **TRS-80 Model I, III e 4**.
Il modulo adotta lo standard industriale del connettore **DIN 5-Pin 180°** (standard DIN 41524 / IEC 60130-9, connettore serie CUI / Same Sky SDS-50J).

### Caratteristiche Elettriche Chiave
1. **Canale Riproduzione Dati (CASSETTE IN / EAR - Pin 4 DIN)**:
   - Modulazione FSK standard CoCo/Dragon: $1200\text{ Hz}$ (Zero logico, 1 ciclo) / $2400\text{ Hz}$ (Uno logico, 1 ciclo) a circa 1500 baud nominali.
   - Pilotaggio digitale tramite buffer invertente open-collector ad alta velocità **74HCT06** (`U2`) configurato a doppio stadio logico per preservare l'esatta polarità di fase, con resistenze di pull-up da $10\text{ k}\Omega$ (`R7`, `R8`) collegate alla linea di alimentazione `+5V`.
   - Rete di attenuazione, filtro e disaccoppiamento AC: resistenza serie da $1\text{ k}\Omega$ (`R9`), condensatore di disaccoppiamento DC da $4.7\ \mu\text{F}$ (`C3`) e resistenza shunt da $10\text{ k}\Omega$ (`R10`) verso massa per iniettare nel circuito amplificatore/comparatore della MC6883/MC6847 o DAC del CoCo un segnale audio pulito, esente da offset e calibrato ($\approx 1 \dots 1.5\text{ V}_{pp}$).
   - Secondo canale analogico diretto ausiliario proveniente da `AUDIO_DAC_L` via disaccoppiamento AC ($C_6 = 4.7\ \mu\text{F}$) e resistenza serie $2.2\text{ k}\Omega$ (`R6`) verso la medesima linea `COCO_READ`.
2. **Canale Registrazione Dati (CASSETTE OUT / MIC - Pin 5 DIN)**:
   - Il CoCo genera l'uscita a cassetta attraverso il DAC a 6-bit interno pilotato dal PIA Motorola 6821, con un segnale a gradini sinusoidali centrato a circa $1.5\text{ V}_{pp}$.
   - Condizionamento e protezione d'ingresso a 3.0V tramite partitore resistivo ($R_1 = 2.2\text{ k}\Omega$, $R_2 = 3.3\text{ k}\Omega$) e diodo di clamping rapido Schottky **BAT54S** (`D1`) verso `+3.3V` e `GND`, collegato all'ingresso di cattura temporale `TAPE_REC_IN` del microcontrollore RP2040.
   - Ramo di monitoraggio analogico AC ad alta impedenza tramite condensatore da $4.7\ \mu\text{F}$ (`C4`), filtro RC passa-basso ($R_{11} = 1\text{ k}\Omega$, $C_5 = 10\text{ nF}$) e resistenza shunt da $10\text{ k}\Omega$ (`R12`) collegato a `AUDIO_RAW_L` per alimentare la catena preamplificatore / indicatore azimut / oscilloscopio sulla scheda madre.
3. **Rilevamento e Controllo Motore Relè (Pin 1 & Pin 3 DIN)**:
   - Sulla scheda madre del Tandy CoCo e del Dragon è presente un relè a reed pilotato dal PIA (`MOTOR ON` / `MOTOR OFF`).
   - Pin 1 (`MOTOR_REM_A`) è vincolato permanentemente a massa (`GND`).
   - Pin 3 (`MOTOR_REM_B`) è tirato a +5V tramite resistenza di pull-up da $10\text{ k}\Omega$ (`R3`) con partitore $2.2\text{ k}\Omega / 3.3\text{ k}\Omega$ (`R4`, `R5`) e clamp Schottky **BAT54S** (`D2`) verso la linea `MOTOR_SENSE`. Alla chiusura del relè da parte del CoCo (comando `MOTOR ON`), la linea viene cortocircuitata a massa provocando l'immediata rilevazione dello stato da parte della MCU.
   - **Bypass / Test Banco (`MOTOR_CTRL`)**: N-MOSFET **2N7002** (`Q1`) collegato in parallelo al relè tra Pin 3 e massa, pilotato da `MOTOR_CTRL` tramite resistenza di gate da $100\ \Omega$ (`R13`) e pull-down da $100\text{ k}\Omega$ (`R14`), permettendo la simulazione o il test a banco di registratori reali (es. CCR-81).
4. **Protezione ESD / Transitori**:
   - Soppressore TVS monolitico a basso carico capacitivo **USBLC6-2SC6** (`D3`) posto in prossimità del connettore DIN sulle linee `COCO_READ`, `COCO_WRITE` e `COCO_REM_B`.
5. **Smart Plug & Play (Auto-ID Cartridge)**:
   - EEPROM seriale I2C **24C02** (`U1`) configurata all'indirizzo standard `0x50` (`A0=0, A1=0, A2=0`), contenente il descrittore hardware univoco del modulo Tandy CoCo & Dragon.
   - Pin 26 del connettore bus principale `CART_DETECT_N` vincolato permanentemente a massa per rilevamento hardware automatico dell'inserimento scheda.

---

## 2. Centralizzazione Diagnostica sul Front Panel (Daughterboard)

Come prescritto dalle regole ufficiali di progetto `tape-master-rules.md`, l'intera interfaccia diagnostica e di stato per l'operatore è centralizzata sul pannello frontale (`Tape_Master_UI_Panel`), evitando LED duplicati non visibili a banco.

I 5 LED diagnostici standardizzati sul pannello operatore riflettono il funzionamento della cartuccia CoCo/Dragon:

| Riferimento UI | Colore | Serigrafia Standard | Segnale Mappato per CoCo/Dragon | Funzione Operativa |
| :---: | :---: | :---: | :--- | :--- |
| **D2** | Verde | **`PLAY`** | `COCO_READ` (Pin 4 DIN) | Riproduzione dati verso il CoCo/Dragon (emulazione nastro / riproduzione CAS / C10 / WAV) |
| **D3** | Rosso | **`REC`** | `COCO_WRITE` (Pin 5 DIN) | Acquisizione flusso audio/dati dal CoCo/Dragon verso il Tape Master (salvataggio dump) |
| **D4** | Giallo | **`MOTOR`** | `COCO_REM_B` (Pin 3 DIN) | Relè motore chiuso dal CoCo (`MOTOR ON`) o pilotaggio forzato da banco |
| **D5** | Blu | **`SIGNAL`** | FSK Carrier $1200/2400\text{ Hz}$ | Rilevamento portante sincrona FSK / transizioni di bit |
| **D6** | Verde | **`PWR`** | Alimentazione Tape Master | Alimentazione principale di sistema attiva (+5V / +3.3V) e MCU operativo |
| **D10..D19** | 8V/1G/1R | **`AZIMUTH / VU-METER`** | Livello di picco ADC `AUDIO_RAW_L` | Barra VU-meter per regolazione azimut / intensità segnale audio in riproduzione |

---

## 3. Doppia Connettività Esterna

La cartuccia adotta la configurazione a **doppia porta**:
1. **`J2` — Presa DIN 5-Pin 180° Femmina (CUI SDS-50J)**: Connettore orizzontale compatibile con i cavi originali Tandy TRS-80 / CoCo e Dragon Data.
2. **`J3` — Pin-Header Maschio Breakout 1x06 passo 2.54 mm**: Pin header a bordo scheda per collegamenti rapidi a banco, oscilloscopio e analizzatore logico.

### Piedinatura Connettori (`J2` e `J3`)

| Pin # J3 | Pin # J2 (DIN-5) | Serigrafia J3 | Segnale | Direzione Elettrica | Descrizione Tecnica |
| :---: | :---: | :--- | :--- | :---: | :--- |
| **1** | **1** | `GND` | `GND` (REM_A) | Riferimento | Ritorno relè motore (a massa permanente) |
| **2** | — | `+5V` | `+5V` | Alimentazione | Alimentazione ausiliaria a banco |
| **3** | **2** | `GND` | `GND` | Riferimento | Massa logica e schermo comune |
| **4** | **3** | `REM` | `COCO_REM_B` | Ingresso/Uscita | Capo attivo relè motore CoCo (pull-up + sense + MOSFET) |
| **5** | **4** | `RD` | `COCO_READ` | Verso CoCo (Input) | Ingresso audio al CoCo da uscita registratore (EAR) |
| **6** | **5** | `WR` | `COCO_WRITE` | Dal CoCo (Output) | Uscita audio dal CoCo verso ingresso registratore (MIC) |

---

## 4. Specifiche Meccaniche e Bordo Scheda

- **Dimensioni**: $74.00\text{ mm} \times 55.00\text{ mm}$.
- **Intagli Meccanici**: Due intagli su `Edge.Cuts` ($6.0\text{ mm} \times 8.0\text{ mm}$) per l'alloggiamento delle leve di ritenuta del connettore `J1` della Mainboard.
- **Complanarità**: Connettore maschio ad angolo retto sulla Mainboard e connettore femmina ad angolo retto sulla Cartuccia (`J1`) permettono alle due schede di rimanere **perfettamente parallele e complanari**, con la cartuccia che estende orizzontalmente all'indietro il corpo principale del Tape Master.

---

## 5. File di Rilascio e Produzione

- Schema Elettrico KiCad: `Tape_Master_Cartridge_CoCo_Dragon.kicad_sch`
- Layout PCB KiCad: `Tape_Master_Cartridge_CoCo_Dragon.kicad_pcb`
- Modello 3D Meccanico Solido PCB Assemblato: `Tape_Master_Cartridge_CoCo_Dragon.step`
- Schema Elettrico Vettoriale: `Tape_Master_Cartridge_CoCo_Dragon.pdf` e `Tape_Master_Cartridge_CoCo_Dragon_Sch.svg`
- Disegno PCB Top Layer: `Tape_Master_Cartridge_CoCo_Dragon_Top.pdf` e `Tape_Master_Cartridge_CoCo_Dragon_Top.svg`
- Disegno PCB Bottom Layer: `Tape_Master_Cartridge_CoCo_Dragon_Bottom.pdf`
- Pacchetto Gerbers & Drills Produzione: cartella `gerbers/`
- Report di Validazione KiCad 9:
  - ERC: `Tape_Master_Cartridge_CoCo_Dragon_erc.rpt` (**0 errori / 0 warning**)
  - DRC: `Tape_Master_Cartridge_CoCo_Dragon_drc.rpt` (**0 violazioni / 0 unconnected / 0 parity**)
