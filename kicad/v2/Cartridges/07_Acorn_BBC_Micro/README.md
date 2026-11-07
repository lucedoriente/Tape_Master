# Tape Master v2 — Cartuccia 07: Acorn BBC Micro & Electron Tape Interface

| Proprietà | Dettaglio / Valore |
| :--- | :--- |
| **Progetto** | Tape Master Exerciser & Signal Digitizer v2 |
| **Modulo** | Cartuccia Espansione #07 — Acorn BBC Micro & Electron (`07_Acorn_BBC_Micro`) |
| **Piattaforme Compatibili** | Acorn BBC Micro (Model A, Model B, B+ 64/128, Master 128), Acorn Electron |
| **Periferiche Supportate** | Acorn Data Recorder ANF03, registratori a cassette standard compatibili BBC (cavi DIN-7 a DIN-7 o DIN-7 a jack 3.5mm/2.5mm), loader turbo e standard CUTS |
| **Autore & Hardware Designer** | Alessio Iodice (`alessio67@gmail.com`) |
| **Data di Rilascio** | 2026-11-06 |
| **Revisione** | 1.0 (KiCad 9.0 Nativo) |
| **Licenza** | CC BY-NC-SA 4.0 |
| **Stato Validazione KiCad 9** | **0 Violazioni ERC / 0 Violazioni DRC / 0 Net Non Connesse / 0 Parity Issues** |

---

## 1. Descrizione Architetturale

La **Cartuccia 07: Acorn BBC Micro & Electron** interfaccia il sistema **Tape Master v2** alla porta a cassetta dei personal computer ad 8-bit britannici di riferimento educational e scientifico **Acorn BBC Micro** ed **Acorn Electron**, adottando lo standard industriale del connettore **DIN 7-Pin 270°** (standard industriale DIN 45329 / IEC 60130-9, connettore serie CUI / Same Sky SDS-70J).

### Caratteristiche Elettriche Chiave
1. **Canale Riproduzione Dati (CASSETTE IN / EAR - Pin 3 DIN)**:
   - Codifica standard CUTS / Kansas City Standard ($1200\text{ Hz}$ Space / $2400\text{ Hz}$ Mark a 300 e 1200 baud).
   - Pilotaggio digitale tramite buffer open-collector ad alta velocità **74HCT06** (`U2`) configurato a doppio stadio inverter per preservare la fase del segnale, con resistenze di pull-up da $4.7\text{ k}\Omega$ (`R7`, `R8`) a `+5V`.
   - Rete di attenuazione e disaccoppiamento AC composta da resistenza serie $1\text{ k}\Omega$ (`R9`), condensatore di blocco DC da $4.7\ \mu\text{F}$ (`C3`) e resistenza shunt da $10\text{ k}\Omega$ (`R10`) a massa, che inietta verso il computer un segnale audio pulito e calibrato ($\approx 1 \dots 2\text{ V}_{pp}$).
   - Secondo canale analogico diretto ausiliario proveniente da `AUDIO_DAC_L` via disaccoppiamento AC ($C_6 = 4.7\ \mu\text{F}$) e resistenza serie $2.2\text{ k}\Omega$ (`R6`) verso la stessa linea `BBC_IN`.
2. **Canale Registrazione Dati (CASSETTE OUT / MIC - Pin 1 & Pin 4 DIN)**:
   - Il sintetizzatore sonoro ULA/ACIA del computer BBC Micro genera un segnale AC audio di ampiezza compresa tra $200\text{ mV}_{pp}$ e $1\text{ V}_{pp}$ (o impulsi digitali) sulle linee Pin 1 e Pin 4 (collegate insieme).
   - Condizionamento e protezione d'ingresso a 3.0V tramite partitore resistivo ($R_1 = 2.2\text{ k}\Omega$, $R_2 = 3.3\text{ k}\Omega$) e diodo di clamping Schottky rapido **BAT54S** (`D1`) verso `+3.3V` e `GND`, collegato all'ingresso di cattura temporale `TAPE_REC_IN` dell'RP2040.
   - Ramo di monitoraggio analogico AC ad alta impedenza tramite condensatore da $4.7\ \mu\text{F}$ (`C4`), filtro RC passa-basso ($R_{11} = 1\text{ k}\Omega$, $C_5 = 10\text{ nF}$) e resistenza shunt da $10\text{ k}\Omega$ (`R12`) collegato a `AUDIO_RAW_L` per alimentare la catena preamplificatore / indicatore azimut / oscilloscopio sulla scheda madre.
3. **Rilevamento e Controllo Motore Relè (Pin 6 & Pin 7 DIN)**:
   - Sulla scheda madre del BBC Micro e dell'Acorn Electron è presente un relè a contatti dorati comandato dal MOS (`*MOTOR 1` per chiusura / `*MOTOR 0` per apertura).
   - **Rilevamento Stato Motore (`MOTOR_SENSE`)**: Pin 7 (`MOTOR_REM_B`) è vincolato a massa permanente (`GND`). Pin 6 (`MOTOR_REM_A`) è tirato a +5V tramite resistenza di pull-up da $10\text{ k}\Omega$ (`R3`) con partitore $2.2\text{ k}\Omega / 3.3\text{ k}\Omega$ (`R4`, `R5`) e clamp Schottky **BAT54S** (`D2`) verso la linea `MOTOR_SENSE`. All'attivazione del motore da parte del software BBC, la chiusura del relè abbatte la tensione a 0V, segnalando istantaneamente alla MCU lo stato di motore in rotazione.
   - **Bypass / Test Banco (`MOTOR_CTRL`)**: N-MOSFET **2N7002** (`Q1`) collegato in parallelo al relè tra Pin 6 e massa, pilotato da `MOTOR_CTRL` tramite resistenza di gate da $100\ \Omega$ (`R13`) e pull-down da $100\text{ k}\Omega$ (`R14`), permettendo la simulazione o il test a banco di registratori reali.
4. **Protezione ESD / Transitori**:
   - Soppressore TVS monolitico a 4 canali **USBLC6-2SC6** (`D3`) posto in prossimità del connettore DIN sulle linee `BBC_IN`, `BBC_OUT` e `BBC_REM_A`.
5. **Smart Plug & Play (Auto-ID Cartridge)**:
   - EEPROM seriale I2C **24C02** (`U1`) configurata all'indirizzo standard `0x50` (`A0=0, A1=0, A2=0`), contenente il descrittore hardware univoco del modulo Acorn BBC Micro & Electron.
   - Pin 26 del connettore bus principale `CART_DETECT_N` vincolato permanentemente a massa per rilevamento hardware automatico dell'inserimento scheda.

---

## 2. Centralizzazione Diagnostica sul Front Panel (Daughterboard)

Come prescritto dalle regole ufficiali di progetto `tape-master-rules.md`, l'intera interfaccia diagnostica e di stato per l'operatore è centralizzata sul pannello frontale (`Tape_Master_UI_Panel`), evitando LED duplicati non visibili a banco.

I 5 LED diagnostici standardizzati sul pannello operatore riflettono il funzionamento della cartuccia Acorn BBC Micro:

| Riferimento UI | Colore | Serigrafia Standard | Segnale Mappato per BBC Micro | Funzione Operativa |
| :---: | :---: | :---: | :--- | :--- |
| **D2** | Verde | **`PLAY`** | `BBC_IN` (Pin 3 DIN) | Riproduzione dati verso il computer BBC Micro (emulazione nastro / riproduzione UEF / CSW) |
| **D3** | Rosso | **`REC`** | `BBC_OUT` (Pin 1/4 DIN) | Acquisizione flusso audio/dati dal BBC Micro verso il Tape Master (salvataggio dump) |
| **D4** | Giallo | **`MOTOR`** | `BBC_REM_A` (Pin 6 DIN) | Relè motore chiuso dal BBC Micro (`*MOTOR 1`) o pilotaggio forzato da banco |
| **D5** | Blu | **`SIGNAL`** | Leader Tone CUTS $2400\text{ Hz}$ | Rilevamento portante sincrona $2400\text{ Hz}$ / modulazione Kansas City |
| **D6** | Verde | **`PWR`** | Alimentazione Tape Master | Alimentazione principale di sistema attiva (+5V / +3.3V) e MCU operativo |
| **D10..D19** | 8V/1G/1R | **`AZIMUTH / VU-METER`** | Livello di picco ADC `AUDIO_RAW_L` | Barra VU-meter per regolazione azimut / intensità segnale audio in riproduzione |

---

## 3. Doppia Connettività Esterna

La cartuccia adotta la configurazione a **doppia porta**:
1. **`J2` — Presa DIN 7-Pin 270° Femmina (CUI SDS-70J)**: Connettore orizzontale per il cavo originale BBC Micro DIN-7 standard.
2. **`J3` — Pin-Header Maschio Breakout 1x07 passo 2.54 mm**: Pin header a bordo scheda per collegamenti rapidi a banco, oscilloscopio e analizzatore logico.

### Piedinatura Connettori (`J2` e `J3`)

| Pin # J3 | Pin # J2 (DIN-7) | Serigrafia J3 | Segnale | Direzione Elettrica | Descrizione Tecnica |
| :---: | :---: | :--- | :--- | :---: | :--- |
| **1** | **1** | `OUT` | `BBC_OUT` | Dal BBC (Output) | Uscita audio/dati dal BBC Micro verso ingresso registratore (MIC) |
| **2** | **2** | `GND` | `GND` | Riferimento | Massa logica e schermo comune |
| **3** | **3** | `IN` | `BBC_IN` | Verso BBC (Input) | Ingresso audio/dati al BBC Micro da uscita registratore (EAR) |
| **4** | **4** | `ALT` | `BBC_OUT` | Dal BBC (Output) | Canale audio alternativo (collegato in parallelo a Pin 1) |
| **5** | **5** | `NC` | `NC` | — | Non connesso |
| **6** | **6** | `RA` | `BBC_REM_A` | Ingresso/Uscita | Primo capo contatto relè motore BBC Micro (pull-up + sense + MOSFET) |
| **7** | **7** | `GND` | `GND` | Ingresso/Uscita | Secondo capo contatto relè motore BBC Micro (a massa permanente) |

---

## 4. Specifiche Meccaniche e Bordo Scheda

- **Dimensioni**: $74.00\text{ mm} \times 55.00\text{ mm}$.
- **Intagli Meccanici**: Due intagli su `Edge.Cuts` ($6.0\text{ mm} \times 8.0\text{ mm}$) per l'alloggiamento delle leve di ritenuta del connettore `J1` della Mainboard.
- **Complanarità**: Connettore maschio ad angolo retto sulla Mainboard e connettore femmina ad angolo retto sulla Cartuccia (`J1`) permettono alle due schede di rimanere **perfettamente parallele e complanari**, con la cartuccia che estende orizzontalmente all'indietro il corpo principale del Tape Master.

---

## 5. File di Rilascio e Produzione

- Schema Elettrico KiCad: `Tape_Master_Cartridge_BBC_Micro.kicad_sch`
- Layout PCB KiCad: `Tape_Master_Cartridge_BBC_Micro.kicad_pcb`
- Modello 3D Meccanico Solido PCB Assemblato: `Tape_Master_Cartridge_BBC_Micro.step`
- Schema Elettrico Vettoriale: `Tape_Master_Cartridge_BBC_Micro.pdf` e `Tape_Master_Cartridge_BBC_Micro_Sch.svg`
- Disegno PCB Top Layer: `Tape_Master_Cartridge_BBC_Micro_Top.pdf` e `Tape_Master_Cartridge_BBC_Micro_Top.svg`
- Disegno PCB Bottom Layer: `Tape_Master_Cartridge_BBC_Micro_Bottom.pdf`
- Pacchetto Gerbers & Drills Produzione: cartella `gerbers/`
- Report di Validazione KiCad 9:
  - ERC: `Tape_Master_Cartridge_BBC_Micro-erc.rpt` (**0 errori / 0 warning**)
  - DRC: `Tape_Master_Cartridge_BBC_Micro-drc.rpt` (**0 violazioni / 0 unconnected / 0 parity**)
