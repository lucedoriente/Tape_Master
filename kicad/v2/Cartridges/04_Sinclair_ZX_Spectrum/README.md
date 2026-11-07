# Tape Master v2 — Cartuccia #04: Sinclair ZX Spectrum / ZX81 / Timex Sinclair

Modulo di interfaccia cassetta hardware conforme allo standard **Tape Master v2 (Tape/Cassette Master Exerciser & Signal Digitizer)** progettato da **Alessio Iodice**.

---

## 1. Modelli e Piattaforme Supportate
La cartuccia supporta la totalità della famiglia Sinclair a 8 bit e i relativi cloni compatibili:
- **Sinclair ZX80 / ZX81** (jack standard 3.5 mm MIC/EAR)
- **Sinclair ZX Spectrum 16K / 48K** ("Rubber Keys" e "Plus")
- **Sinclair ZX Spectrum 128K** ("Toastrack")
- **Sinclair ZX Spectrum +2** (Grigio con Datacorder integrato e prese ausiliarie)
- **Sinclair ZX Spectrum +2A / +2B / +3** (Nero - Amstrad design)
- **Timex Sinclair 1000 / 1500 / 2068**
- **Cloni internazionali**: Microdigital TK85, TK90X, TK95 (Brasile), Didaktik Gama / M (Cecoslovacchia), Pentagon / Scorpion (URSS).

---

## 2. Architettura Elettronica e Circuiti di Segnale

### A. Uscita Verso il Computer (`SPECTRUM_EAR` / Jack J2)
- **Livello Segnale e Attenuazione**: Il microcontrollore Tape Master genera segnali digitali a 3.3V/5V (`TAPE_EMU_OUT`). La porta EAR dello Spectrum accetta ampiezze nominali da $0.7\text{ V}$ a $1.5\text{ V}_\text{pp}$.
- **Buffer di Pilotaggio**: Buffer invertitore open-collector ad alta velocità **74HCT06** (`U2`), configurato a doppio stadio con resistenze di pull-up da $4.7\text{ k}\Omega$ (`R8`, `R9`) a +5V.
- **Partitore e Disaccoppiamento AC**: Partitore resistivo simmetrico $1\text{ k}\Omega / 1\text{ k}\Omega$ (`R6`, `R7`) per ridurre il segnale a circa $1.25\text{ V}_\text{pp}$, seguito da condensatore elettrolitico/tantalio SMD da $4.7\ \mu\text{F}$ (`C4`) per il disaccoppiamento della componente continua.

### B. Ingresso dal Computer (`SPECTRUM_MIC` / Jack J3)
- **Doppio Percorso di Acquisizione**:
  1. **Percorso Digitale MCU (`TAPE_REC_IN`)**: Partitore resistivo $2.2\text{ k}\Omega / 3.3\text{ k}\Omega$ (`R1`, `R2`) con stadio di clamp a diodi Schottky ultraveloci **BAT54S** (`D1`) verso GND e +3.3V, per una cattura a squadratura perfetta senza jitter.
  2. **Percorso Analogico Digitizer (`AUDIO_RAW_L`)**: Disaccoppiamento in frequenza tramite condensatore da $4.7\ \mu\text{F}$ (`C5`) diretto al convertitore analogico ADC e alla barra VU-meter a 10 segmenti frontale.

### C. Controllo Motore Remoto (`SPECTRUM_REM_A` / Header J4)
- Interruttore a stato solido basato su MOSFET a canale N **2N7002** (`Q1`) pilotato dalla linea `MOTOR_SENSE` con resistenza di pull-up da $10\text{ k}\Omega$ (`R3`), in grado di emulare il relè del telecomando registratore per registratori esterni compatibili.

### D. Protezione ESD e Auto-Riconoscimento Smart Plug&Play
- **Protezione TVS**: Array di diodi ad altissima velocità **USBLC6-2SC6** (`D2`) su tutte le linee esterne esposte (`EAR`, `MIC`, `REM_A`).
- **EEPROM I2C 24C02 (`U1`)**: Indirizzo hardware `0x54` (`A2=1`, `A1=0`, `A0=0`), contenente il descrittore binario Plug&Play con identificativo cartuccia `#04`, mapping piedini e parametri di temporizzazione ULA.

---

## 3. Connettività Esterna e Banco di Collaudo

### Connettori Audio Jack 3.5 mm TRS (CUI SJ1-3533NG)
- **`J2` (`EAR` / Riproduzione verso Spectrum)**:
  - `Tip (T)`: Segnale `SPECTRUM_EAR`
  - `Ring (R)`: Connesso a Tip per piena compatibilità con cavetti sia mono sia stereo
  - `Sleeve (S)`: Massa (`GND`)
- **`J3` (`MIC` / Registrazione dallo Spectrum)**:
  - `Tip (T)`: Segnale `SPECTRUM_MIC`
  - `Ring (R)`: Connesso a Tip per compatibilità con cavetti mono e stereo
  - `Sleeve (S)`: Massa (`GND`)

### Pin Header Banco di Prova (`J4` - Maschio 1x06 passo 2.54 mm)
| Pin | Segnale Serigrafato | Funzione Elettrica |
| :---: | :---: | :--- |
| **1** | `GND` | Riferimento di massa 0V |
| **2** | `+5V` | Alimentazione secondaria ausiliaria |
| **3** | `EAR` | Linea audio riproduzione diretta / oscilloscopio |
| **4** | `MIC` | Linea audio acquisizione grezza / analizzatore |
| **5** | `REM` | Linea controllo motore registratore |
| **6** | `GND` | Riferimento di massa 0V |

---

## 4. Specifiche Meccaniche e PCB
- **Dimensioni Esterne**: $74.00\text{ mm} \times 55.00\text{ mm}$ con profilo Edge.Cuts standard.
- **Intagli Laterali di Ritenuta**: Due aperture $6.00\text{ mm} \times 8.00\text{ mm}$ per le leve di aggancio rapido (latch) del connettore Mainboard.
- **Connettore Bus**: $2 \times 20$ contatti femmina a 90° (`J1`), perfettamente complanare alla Mainboard.
- **Finitura**: Piani di massa rame continui su Top (`F.Cu`) e Bottom (`B.Cu`), serigrafia con dicitura d'autore `© 2026 by Alessio Iodice`.

---

## 5. Validazione KiCad 9.0 e File di Fabbricazione
- **Controllo Regole Elettriche (ERC)**: `0 errori / 0 avvisi`
- **Controllo Regole di Design (DRC)**: `0 violazioni / 0 net non connesse / 0 discrepanze netlist-PCB`
- **File Inclusi**:
  - `Tape_Master_Cartridge_Sinclair_ZX.kicad_sch` (Schema elettrico)
  - `Tape_Master_Cartridge_Sinclair_ZX.kicad_pcb` (Layout sbrogliato e verificato)
  - `Tape_Master_Cartridge_Sinclair_ZX.pdf` (Tavola vettoriale dello schema)
  - `Tape_Master_Cartridge_Sinclair_ZX.step` (Modello 3D solido MCAD con tutti i componenti integrati)
  - `Tape_Master_Cartridge_Sinclair_ZX_Top.pdf` / `Bottom.pdf` / `Top.svg` (Plottaggi serigrafia e rame)
  - `gerbers/` (26 file standard RS-274X e forature Excellon pronti per JLCPCB/PCBWay).
