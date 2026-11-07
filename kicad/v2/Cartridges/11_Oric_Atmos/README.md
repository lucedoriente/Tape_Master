# Tape Master v2 — Cartuccia 11: Oric 1 / Oric Atmos / Telestrat Tape Interface

| Proprietà | Dettaglio / Valore |
| :--- | :--- |
| **Progetto** | Tape Master Exerciser & Signal Digitizer v2 |
| **Modulo** | Cartuccia Espansione #11 — Oric 1 / Oric Atmos (`11_Oric_Atmos`) |
| **Piattaforme Compatibili** | Tangerine Oric-1 (16K/48K), Oric Atmos (16K/48K), Oric Telestrat, Oric Stratos |
| **Periferiche Supportate** | Registratori a cassette standard compatibili Oric (cavi DIN-7 a 3 Jack 3.5/2.5mm), formati nastro standard FSK e turbo hyper-load |
| **Autore & Hardware Designer** | Alessio Iodice (`alessio67@gmail.com`) |
| **Data di Rilascio** | 2026-11-06 |
| **Revisione** | 2.0 (KiCad 9.0 Nativo) |
| **Licenza** | CC BY-NC-SA 4.0 |
| **Stato Validazione KiCad 9** | **0 Violazioni ERC / 0 Violazioni DRC / 0 Net Non Connesse / 0 Parity Issues** |

---

## 1. Descrizione Architetturale

La **Cartuccia 11: Oric 1 / Oric Atmos** interfaccia il sistema **Tape Master v2** alla porta a cassetta dei microcomputer britannici/francesi **Oric-1** (1983) ed **Oric Atmos** (1984) basati su CPU 6502 e gate array ULA Tangerine.
Il modulo adotta lo standard industriale del connettore **DIN 7-Pin 270°** (standard DIN 45322 / IEC 60130-9, connettore serie CUI / Same Sky `SDS-70J` orizzontale).

---

### Caratteristiche Elettriche Chiave
1. **Canale Riproduzione Dati (TAPE IN / EAR — Pin 3 DIN)**:
   - Modulazione FSK Oric: velocità standard $300\text{ baud}$ (Space $1200\text{ Hz}$ / Mark $2400\text{ Hz}$) e velocità hyper-load $2400\text{ baud}$ (Space $2400\text{ Hz}$ / Mark $4800\text{ Hz}$).
   - Pilotaggio digitale tramite buffer open-collector ad alta velocità **74HCT06** (`U2`) configurato a doppio stadio logico per preservare la fase corretta, con resistenze di pull-up da $4.7\text{ k}\Omega$ (`R7`, `R8`) collegate a `+5V`.
   - Rete di attenuazione, filtro e disaccoppiamento AC: resistenza serie da $1\text{ k}\Omega$ (`R9`), condensatore di disaccoppiamento DC da $4.7\ \mu\text{F}$ (`C3`) e resistenza shunt da $10\text{ k}\Omega$ (`R10`) verso massa per iniettare nel circuito comparatore dell'Oric (LM3900 quad Norton o transistor discreto) un segnale audio pulito e calibrato ($\approx 1.0\dots 1.5\text{ V}_{pp}$).
   - Secondo canale analogico ausiliario diretto proveniente da `AUDIO_DAC_L` via disaccoppiamento AC ($C_6 = 4.7\ \mu\text{F}$) e resistenza serie $2.2\text{ k}\Omega$ (`R6`) verso la medesima linea `ORIC_READ`.
2. **Canale Registrazione Dati (TAPE OUT / MIC — Pin 4 & Pin 5 DIN)**:
   - L'Oric genera il segnale a cassetta e l'audio sintetizzato tramite la ULA e il generatore sonoro programmabile AY-3-8912, producendo un segnale AC audio compreso tra $\approx 100\text{ mV}_{pp}$ e $500\text{ mV}_{pp}$ sui Pin 4 e 5.
   - Condizionamento e protezione d'ingresso a 3.0V tramite partitore resistivo ($R_1 = 2.2\text{ k}\Omega$, $R_2 = 3.3\text{ k}\Omega$) e diodo di clamping rapido Schottky **BAT54S** (`D1`) verso `+3.3V` e `GND`, collegato all'ingresso di cattura temporale `TAPE_REC_IN` dell'RP2040.
   - Ramo di monitoraggio analogico AC ad alta impedenza tramite condensatore da $4.7\ \mu\text{F}$ (`C4`), filtro RC passa-basso ($R_{11} = 1\text{ k}\Omega$, $C_5 = 10\text{ nF}$) e resistenza shunt da $10\text{ k}\Omega$ (`R12`) collegato a `AUDIO_RAW_L` per alimentare la catena preamplificatore / indicatore azimut / oscilloscopio sulla scheda madre.
3. **Rilevamento e Controllo Motore Relè (Pin 1 DIN — `ORIC_REM_B`)**:
   - Sulla scheda madre dell'Oric, il comando motore è affidato al bit `PB3` della 6522 VIA: a motore acceso il transistor interno cortocircuita il Pin 1 a massa, mentre a motore spento il pin rimane flottante.
   - **Rilevamento Stato Motore (`MOTOR_SENSE`)**: Pin 1 è collegato a pull-up da $10\text{ k}\Omega$ a +5V (`R3`), partitore $2.2\text{ k}\Omega / 3.3\text{ k}\Omega$ (`R4`, `R5`) e clamp Schottky **BAT54S** (`D2`) verso la linea `MOTOR_SENSE`. All'attivazione del motore, la chiusura a massa fa crollare la tensione a 0V, segnalando istantaneamente alla MCU lo stato di rotazione.
   - **Bypass / Test Banco (`MOTOR_CTRL`)**: N-MOSFET **2N7002** (`Q1`) collegato tra Pin 1 e massa, pilotato da `MOTOR_CTRL` tramite resistenza di gate da $100\ \Omega$ (`R13`) e pull-down da $100\text{ k}\Omega$ (`R14`), permettendo la simulazione e il controllo automatico di registratori reali a banco.
4. **Protezione ESD / Transitori**:
   - Soppressore TVS monolitico a basso carico capacitivo **USBLC6-2SC6** (`D3`) posto in prossimità del connettore DIN sulle linee `ORIC_READ`, `ORIC_WRITE` e `ORIC_REM_B`.
5. **Smart Plug & Play (Auto-ID Cartridge)**:
   - EEPROM seriale I2C **24C02** (`U1`) configurata all'indirizzo standard `0x50` (`A0=0, A1=0, A2=0`), contenente il descrittore hardware univoco del modulo Oric 1 / Oric Atmos.
   - Pin 26 del connettore bus principale `CART_DETECT_N` vincolato permanentemente a massa per rilevamento hardware automatico dell'inserimento scheda.

---

## 2. Centralizzazione Diagnostica sul Front Panel (Daughterboard)

Come prescritto dalle regole ufficiali di progetto `tape-master-rules.md`, l'intera interfaccia diagnostica e di stato per l'operatore è centralizzata sul pannello frontale (`Tape_Master_UI_Panel`), evitando LED duplicati non visibili a banco.

I 5 LED diagnostici standardizzati sul pannello operatore riflettono il funzionamento della cartuccia Oric:

| Riferimento UI | Colore | Serigrafia Standard | Segnale Mappato per Oric | Funzione Operativa |
| :---: | :---: | :---: | :--- | :--- |
| **D2** | Verde | **`PLAY`** | `ORIC_READ` (Pin 3 DIN) | Riproduzione dati verso l'Oric (emulazione nastro / riproduzione TAP / WAV) |
| **D3** | Rosso | **`REC`** | `ORIC_WRITE` (Pin 4/5 DIN) | Acquisizione flusso audio/dati dall'Oric verso il Tape Master (salvataggio dump) |
| **D4** | Giallo | **`MOTOR`** | `ORIC_REM_B` (Pin 1 DIN) | Comando motore attivato dall'Oric (`CLOAD`/`CSAVE`) o pilotaggio forzato da banco |
| **D5** | Blu | **`SIGNAL`** | FSK Sync $1200/2400\text{ Hz}$ | Rilevamento portante sincrona FSK e transizioni di bit |
| **D6** | Verde | **`PWR`** | Alimentazione Tape Master | Alimentazione principale di sistema attiva (+5V / +3.3V) e MCU operativo |
| **D10..D19** | 8V/1G/1R | **`AZIMUTH / VU-METER`** | Livello di picco ADC `AUDIO_RAW_L` | Barra VU-meter per regolazione azimut / intensità segnale audio in riproduzione |

---

## 3. Doppia Connettività Esterna

La cartuccia adotta la configurazione a **doppia porta**:
1. **`J2` — Presa DIN 7-Pin 270° Femmina (CUI SDS-70J)**: Connettore orizzontale compatibile con il cavo originale Oric-1 / Oric Atmos DIN-7 standard.
2. **`J3` — Pin-Header Maschio Breakout 1x07 passo 2.54 mm**: Pin header a bordo scheda per collegamenti rapidi a banco, oscilloscopio e analizzatore logico.

### Piedinatura Connettori (`J2` e `J3`)

| Pin # J3 | Pin # J2 (DIN-7) | Serigrafia J3 | Segnale | Direzione Elettrica | Descrizione Tecnica |
| :---: | :---: | :--- | :--- | :---: | :--- |
| **1** | **1** | `REM` | `ORIC_REM_B` | Ingresso/Uscita | Capo telecomando motore registratore (pull-up + sense + MOSFET) |
| **2** | **2** | `GND` | `GND` | Riferimento | Massa logica e schermo comune |
| **3** | **3** | `IN` | `ORIC_READ` | Verso Oric (Input) | Ingresso audio/dati all'Oric da uscita registratore (EAR) |
| **4** | **4** | `OUT` | `ORIC_WRITE` | Dall'Oric (Output) | Uscita audio/dati dall'Oric verso ingresso registratore (MIC) |
| **5** | **5** | `ALT` | `ORIC_WRITE` | Dall'Oric (Output) | Canale audio/dati ausiliario collegato in parallelo al Pin 4 |
| **6** | — | `+5V` | `+5V` | Alimentazione | Alimentazione ausiliaria a banco |
| **7** | — | `GND` | `GND` | Riferimento | Ritorno di massa ausiliario a banco |

---

## 4. Specifiche Meccaniche e Bordo Scheda

- **Dimensioni**: $74.00\text{ mm} \times 55.00\text{ mm}$.
- **Intagli Meccanici**: Due intagli su `Edge.Cuts` ($6.0\text{ mm} \times 8.0\text{ mm}$) per l'alloggiamento delle leve di ritenuta del connettore `J1` della Mainboard.
- **Complanarità**: Connettore maschio ad angolo retto sulla Mainboard e connettore femmina ad angolo retto sulla Cartuccia (`J1`) permettono alle due schede di rimanere **perfettamente parallele e complanari**, con la cartuccia che estende orizzontalmente all'indietro il corpo principale del Tape Master.

---

## 5. File di Rilascio e Produzione

- Schema Elettrico KiCad: `Tape_Master_Cartridge_Oric_Atmos.kicad_sch`
- Layout PCB KiCad: `Tape_Master_Cartridge_Oric_Atmos.kicad_pcb`
- Modello 3D Meccanico Solido PCB Assemblato: `Tape_Master_Cartridge_Oric_Atmos.step`
- Schema Elettrico Vettoriale: `Tape_Master_Cartridge_Oric_Atmos.pdf` e `Tape_Master_Cartridge_Oric_Atmos_Sch.svg`
- Disegno PCB Top Layer: `Tape_Master_Cartridge_Oric_Atmos_Top.pdf` e `Tape_Master_Cartridge_Oric_Atmos_Top.svg`
- Disegno PCB Bottom Layer: `Tape_Master_Cartridge_Oric_Atmos_Bottom.pdf`
- Pacchetto Gerbers & Drills Produzione: cartella `gerbers/`
- Report di Validazione KiCad 9:
  - ERC: `Tape_Master_Cartridge_Oric_Atmos_erc.rpt` (**0 errori / 0 warning**)
  - DRC: `Tape_Master_Cartridge_Oric_Atmos_drc.rpt` (**0 violazioni / 0 unconnected / 0 parity**)
