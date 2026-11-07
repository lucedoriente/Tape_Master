# Tape Master v2 — Cartuccia 10: Apple II / II+ / IIe Tape Interface

| Proprietà | Dettaglio / Valore |
| :--- | :--- |
| **Progetto** | Tape Master Exerciser & Signal Digitizer v2 |
| **Modulo** | Cartuccia Espansione #10 — Apple II / II+ / IIe (`10_Apple_II`) |
| **Piattaforme Compatibili** | Apple II, Apple II Plus, Apple IIe (tutte le revisioni NTSC/PAL), cloni Apple II (Franklin Ace, Laser 128 con adattatore jack) |
| **Periferiche Supportate** | Registratori a cassette standard compatibili Apple II (Panasonic RQ-2102, Sears, Realistic, Sanyo), nastri software Wozniak Standard Format |
| **Autore & Hardware Designer** | Alessio Iodice (`alessio67@gmail.com`) |
| **Data di Rilascio** | 2026-11-06 |
| **Revisione** | 2.0 (KiCad 9.0 Nativo) |
| **Licenza** | CC BY-NC-SA 4.0 |
| **Stato Validazione KiCad 9** | **0 Violazioni ERC / 0 Violazioni DRC / 0 Net Non Connesse / 0 Parity Issues** |

---

## 1. Descrizione Architetturale

La **Cartuccia 10: Apple II** interfaccia il sistema **Tape Master v2** alla porta a cassetta della storica famiglia di personal computer ad 8-bit **Apple II**, **Apple II Plus** ed **Apple IIe**, progettata da Steve Wozniak nel 1976/1977.
Il modulo adotta la configurazione standard a **doppia presa jack mini-phone da 3.5 mm (1/8")** orizzontale (CUI / Same Sky serie `SJ1-3533NG`):
- **`J2` (CASSETTE IN / EAR)**: Iniezione del segnale audio/dati dal Tape Master verso l'ingresso EAR dell'Apple II.
- **`J3` (CASSETTE OUT / MIC)**: Cattura e digitalizzazione del segnale proveniente dall'uscita MIC dell'Apple II.

---

### Caratteristiche Elettriche Chiave
1. **Canale Riproduzione Dati (CASSETTE IN / EAR — `APPLE_READ` — J2)**:
   - Modulazione Wozniak ad intervalli di zero-crossing: sync tone da $770\text{ Hz}$ ($1300\ \mu\text{s}$ periodo), bit '0' a $2000\text{ Hz}$ ($500\ \mu\text{s}$ periodo, due semi-cicli da $250\ \mu\text{s}$), bit '1' a $1000\text{ Hz}$ ($1000\ \mu\text{s}$ periodo, due semi-cicli da $500\ \mu\text{s}$). Baud rate nominale $\approx 1500\text{ baud}$ ($\approx 180\text{ bytes/s}$).
   - Pilotaggio digitale tramite buffer invertente open-collector ad alta velocità **74HCT06** (`U2`) configurato a doppio stadio logico per preservare l'esatta polarità di fase, con resistenze di pull-up da $4.7\text{ k}\Omega$ (`R7`, `R8`) collegate alla linea di alimentazione `+5V`.
   - Rete di attenuazione, filtro e disaccoppiamento AC: resistenza serie da $1\text{ k}\Omega$ (`R9`), condensatore di disaccoppiamento DC da $4.7\ \mu\text{F}$ (`C3`) e resistenza shunt da $10\text{ k}\Omega$ (`R10`) verso massa per iniettare nel circuito comparatore/limiter dell'Apple II (74LS04 polarizzato a $1\text{ M}\Omega$ o amplificatore operazionale LM324/NE558) un segnale audio calibrato e pulito a livello cuffia ($\approx 1.0\dots 1.5\text{ V}_{pp}$).
   - Secondo canale analogico ausiliario diretto proveniente da `AUDIO_DAC_L` via disaccoppiamento AC ($C_6 = 4.7\ \mu\text{F}$) e resistenza serie $2.2\text{ k}\Omega$ (`R6`) verso la medesima linea `APPLE_READ`.
2. **Canale Registrazione Dati (CASSETTE OUT / MIC — `APPLE_WRITE` — J3)**:
   - L'Apple II genera l'uscita a cassetta commutando il softswitch all'indirizzo di memoria `$C020`. Sulla scheda madre Apple è presente un partitore resistivo ($100\ \Omega$ serie / $100\ \Omega$ shunt) che attenua l'onda quadra TTL 0-5V a un livello microfonico compreso tra $\approx 50\text{ mV}_{pp}$ e $500\text{ mV}_{pp}$.
   - Condizionamento e protezione d'ingresso a 3.0V tramite partitore resistivo ($R_1 = 2.2\text{ k}\Omega$, $R_2 = 3.3\text{ k}\Omega$) e diodo di clamping rapido Schottky **BAT54S** (`D1`) verso `+3.3V` e `GND`, collegato all'ingresso di cattura temporale `TAPE_REC_IN` del microcontrollore RP2040.
   - Ramo di monitoraggio analogico AC ad alta impedenza tramite condensatore da $4.7\ \mu\text{F}$ (`C4`), filtro RC passa-basso ($R_{11} = 1\text{ k}\Omega$, $C_5 = 10\text{ nF}$) e resistenza shunt da $10\text{ k}\Omega$ (`R12`) collegato a `AUDIO_RAW_L` per alimentare la catena preamplificatore / indicatore azimut / oscilloscopio sulla scheda madre.
3. **Rilevamento e Controllo Motore Relè (`APPLE_REM_B`)**:
   - I personal computer Apple II standard non disponevano di una presa motore sul telaio, ma i registratori commerciali (es. Panasonic RQ-2102) utilizzavano un cavo con spinotto ausiliario da 2.5 mm per lo start/stop.
   - La cartuccia include sul pin-header ausiliario `J4` e sulla circuitazione interna la linea completa di comando/sense motore:
     - Pull-up $10\text{ k}\Omega$ a +5V (`R3`), partitore $2.2\text{ k}\Omega / 3.3\text{ k}\Omega$ (`R4`, `R5`) e clamp Schottky **BAT54S** (`D2`) verso `MOTOR_SENSE`.
     - N-MOSFET **2N7002** (`Q1`) collegato tra la linea `APPLE_REM_B` e massa, pilotato da `MOTOR_CTRL` tramite resistenza di gate da $100\ \Omega$ (`R13`) e pull-down da $100\text{ k}\Omega$ (`R14`), permettendo la simulazione o il controllo automatico di registratori reali a banco.
4. **Protezione ESD / Transitori**:
   - Soppressore TVS monolitico a basso carico capacitivo **USBLC6-2SC6** (`D3`) posto in prossimità dei connettori audio sulle linee `APPLE_READ`, `APPLE_WRITE` e `APPLE_REM_B`.
5. **Smart Plug & Play (Auto-ID Cartridge)**:
   - EEPROM seriale I2C **24C02** (`U1`) configurata all'indirizzo standard `0x50` (`A0=0, A1=0, A2=0`), contenente il descrittore hardware univoco del modulo Apple II.
   - Pin 26 del connettore bus principale `CART_DETECT_N` vincolato permanentemente a massa per rilevamento hardware automatico dell'inserimento scheda.

---

## 2. Centralizzazione Diagnostica sul Front Panel (Daughterboard)

Come prescritto dalle regole ufficiali di progetto `tape-master-rules.md`, l'intera interfaccia diagnostica e di stato per l'operatore è centralizzata sul pannello frontale (`Tape_Master_UI_Panel`), evitando LED duplicati non visibili a banco.

I 5 LED diagnostici standardizzati sul pannello operatore riflettono il funzionamento della cartuccia Apple II:

| Riferimento UI | Colore | Serigrafia Standard | Segnale Mappato per Apple II | Funzione Operativa |
| :---: | :---: | :---: | :--- | :--- |
| **D2** | Verde | **`PLAY`** | `APPLE_READ` (J2 EAR) | Riproduzione dati verso l'Apple II (emulazione nastro / riproduzione file Apple Cassette / WAV) |
| **D3** | Rosso | **`REC`** | `APPLE_WRITE` (J3 MIC) | Acquisizione flusso audio/dati dall'Apple II verso il Tape Master (salvataggio dump) |
| **D4** | Giallo | **`MOTOR`** | `APPLE_REM_B` | Stato linea telecomando registratore / pilotaggio forzato da banco |
| **D5** | Blu | **`SIGNAL`** | Leader Tone $770\text{ Hz}$ / Zero-cross | Rilevamento portante sincrona Wozniak / transizioni di semi-ciclo |
| **D6** | Verde | **`PWR`** | Alimentazione Tape Master | Alimentazione principale di sistema attiva (+5V / +3.3V) e MCU operativo |
| **D10..D19** | 8V/1G/1R | **`AZIMUTH / VU-METER`** | Livello di picco ADC `AUDIO_RAW_L` | Barra VU-meter per regolazione azimut / intensità segnale audio in riproduzione |

---

## 3. Doppia Connettività Esterna

La cartuccia adotta la configurazione a **doppia porta**:
1. **`J2` & `J3` — Prese Jack Audio 3.5 mm (1/8") Mono Orizzontali (CUI SJ1-3533NG)**: Connettori orizzontali compatibili con i cavi originali jack-jack Apple II.
2. **`J4` — Pin-Header Maschio Breakout 1x06 passo 2.54 mm**: Pin header a bordo scheda per collegamenti rapidi a banco, oscilloscopio e analizzatore logico.

### Piedinatura Connettori (`J2`, `J3` e `J4`)

| Pin # J4 | Connettore Esterno | Serigrafia J4 | Segnale | Direzione Elettrica | Descrizione Tecnica |
| :---: | :---: | :--- | :--- | :---: | :--- |
| **1** | J2/J3 Sleeve & Ring | `GND` | `GND` | Riferimento | Massa comune e schermo |
| **2** | — | `+5V` | `+5V` | Alimentazione | Alimentazione ausiliaria a banco |
| **3** | J2/J3 Sleeve & Ring | `GND` | `GND` | Riferimento | Massa comune e schermo |
| **4** | — | `REM` | `APPLE_REM_B` | Ingresso/Uscita | Linea controllo motore registratore a banco |
| **5** | J2 Tip | `RD` | `APPLE_READ` | Verso Apple II (Input) | Ingresso audio all'Apple II da uscita EAR |
| **6** | J3 Tip | `WR` | `APPLE_WRITE` | Dall'Apple II (Output) | Uscita audio dall'Apple II verso ingresso MIC |

---

## 4. Specifiche Meccaniche e Bordo Scheda

- **Dimensioni**: $74.00\text{ mm} \times 55.00\text{ mm}$.
- **Intagli Meccanici**: Due intagli su `Edge.Cuts` ($6.0\text{ mm} \times 8.0\text{ mm}$) per l'alloggiamento delle leve di ritenuta del connettore `J1` della Mainboard.
- **Complanarità**: Connettore maschio ad angolo retto sulla Mainboard e connettore femmina ad angolo retto sulla Cartuccia (`J1`) permettono alle due schede di rimanere **perfettamente parallele e complanari**, con la cartuccia che estende orizzontalmente all'indietro il corpo principale del Tape Master.

---

## 5. File di Rilascio e Produzione

- Schema Elettrico KiCad: `Tape_Master_Cartridge_Apple_II.kicad_sch`
- Layout PCB KiCad: `Tape_Master_Cartridge_Apple_II.kicad_pcb`
- Modello 3D Meccanico Solido PCB Assemblato: `Tape_Master_Cartridge_Apple_II.step`
- Schema Elettrico Vettoriale: `Tape_Master_Cartridge_Apple_II.pdf` e `Tape_Master_Cartridge_Apple_II_Sch.svg`
- Disegno PCB Top Layer: `Tape_Master_Cartridge_Apple_II_Top.pdf` e `Tape_Master_Cartridge_Apple_II_Top.svg`
- Disegno PCB Bottom Layer: `Tape_Master_Cartridge_Apple_II_Bottom.pdf`
- Pacchetto Gerbers & Drills Produzione: cartella `gerbers/`
- Report di Validazione KiCad 9:
  - ERC: `Tape_Master_Cartridge_Apple_II_erc.rpt` (**0 errori / 0 warning**)
  - DRC: `Tape_Master_Cartridge_Apple_II_drc.rpt` (**0 violazioni / 0 unconnected / 0 parity**)
