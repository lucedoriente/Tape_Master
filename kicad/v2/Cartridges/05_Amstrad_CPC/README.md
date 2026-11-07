# Tape Master v2 — Cartuccia 05: Amstrad CPC Tape Interface

| Proprietà | Dettaglio / Valore |
| :--- | :--- |
| **Progetto** | Tape Master Exerciser & Signal Digitizer v2 |
| **Modulo** | Cartuccia Espansione #05 — Amstrad CPC (`05_Amstrad_CPC`) |
| **Piattaforme Compatibili** | Amstrad CPC 464 (porta ausiliaria esterna), CPC 664, CPC 6128, Schneider CPC |
| **Periferiche Supportate** | Registratore incorporato CPC 464, deck esterno Amstrad MP-1/MP-2, registratori standard per CPC 664/6128, interfacce compatibili turbo (Speedlock, etc.) |
| **Autore & Hardware Designer** | Alessio Iodice (`alessio67@gmail.com`) |
| **Data di Rilascio** | 2026-11-06 |
| **Revisione** | 2.0 (KiCad 9.0 Nativo) |
| **Licenza** | CC BY-NC-SA 4.0 |
| **Stato Validazione KiCad 9** | **0 Violazioni ERC / 0 Violazioni DRC / 0 Net Non Connesse / 0 Parity Issues** |

---

## 1. Descrizione Architetturale

La **Cartuccia 05: Amstrad CPC** interfaccia il sistema **Tape Master v2** al registratore e al bus a cassetta della celebre famiglia di personal computer **Amstrad CPC** (CPC 464, CPC 664 e CPC 6128), adottando lo standard industriale del connettore **DIN 5-Pin 180°** (DIN 41524 / IEC 60130-9).

### Caratteristiche Elettriche Chiave
1. **Canale Riproduzione Dati (DATA IN / EAR - Pin 4 DIN)**:
   - Modulazione FSK a due toni standard Amstrad ($1000\text{ Hz} \dots 2000\text{ Hz}$ fino a $4000\text{ baud}$ per loader turbo).
   - Pilotaggio tramite buffer open-collector ad alta velocità **74HCT06** (`U2`) configurato a doppio stadio logico per preservare la fase originaria del segnale, con resistenze di pull-up da $4.7\text{ k}\Omega$ (`R7`, `R8`) a `+5V`.
   - Rete di condizionamento e calibrazione del livello audio verso il CPC composta da resistenza serie $1\text{ k}\Omega$ (`R9`), condensatore di disaccoppiamento AC da $4.7\ \mu\text{F}$ (`C3`) e resistenza shunt da $10\text{ k}\Omega$ (`R10`) a massa, iniettando un segnale audio pulito e calibrato ($\approx 1 \dots 2\text{ V}_{pp}$).
2. **Canale Registrazione Dati (DATA OUT / MIC - Pin 5 DIN)**:
   - Il computer Amstrad trasmette impulsi digitali a 5V TTL su Pin 5 durante i comandi di salvataggio (`SAVE`).
   - Traslazione di livello rapida e sicura a 3.0V tramite partitore resistivo ($R_1 = 2.2\text{ k}\Omega$, $R_2 = 3.3\text{ k}\Omega$) con clamp a doppio diodo Schottky **BAT54S** (`D1`) verso `+3.3V` e `GND`, pilotando l'ingresso `TAPE_REC_IN` del microcontrollore Tape Master.
   - Derivazione audio AC con condensatore da $4.7\ \mu\text{F}$ (`C4`), filtro RC passa-basso ($R_{11} = 1\text{ k}\Omega$, $C_5 = 10\text{ nF}$) e shunt $10\text{ k}\Omega$ (`R12`) collegata a `AUDIO_RAW_L` per la visualizzazione dinamica in tempo reale sul VU-meter del pannello frontale durante i salvataggi.
3. **Rilevamento e Controllo Motore (REMOTE - Pin 1 & Pin 3 DIN)**:
   - All'interno del CPC, un relè a lamelle (*reed relay*) azionato dal Gate Array/PPI chiude i contatti tra Pin 1 e Pin 3 per avviare il registratore.
   - **Rilevamento Stato Motore (`MOTOR_SENSE`)**: Pin 1 è collegato a massa permanente (`GND`), Pin 3 è tirato a +5V tramite resistenza di pull-up da $10\text{ k}\Omega$ (`R3`) ed entra in un partitore $2.2\text{ k}\Omega / 3.3\text{ k}\Omega$ (`R4`, `R5`) con clamp Schottky **BAT54S** (`D2`) verso `MOTOR_SENSE`. Quando il CPC chiude il relè, la linea scende a 0V indicando la richiesta motore attiva.
   - **Controllo Motore Attivo Registratore Esterno (`MOTOR_CTRL`)**: N-MOSFET di commutazione **2N7002** (`Q1`) collegato tra Pin 3 e Pin 1 (GND), con gate pilotato dalla linea `MOTOR_CTRL` tramite resistenza di disaccoppiamento da $100\ \Omega$ (`R13`) e resistenza di pull-down da $100\text{ k}\Omega$ (`R14`) a massa. Consente al Tape Master di azionare direttamente il motore di un registratore Amstrad reale collegato alla porta per collaudi a banco.
4. **Protezione ESD / Transitori**:
   - Soppressore TVS integrato ultra-rapido **USBLC6-2SC6** (`D3`) posto a ridosso del connettore DIN sulle linee `CPC_READ`, `CPC_WRITE` e `CPC_REM_B`.
5. **Smart Plug & Play (Auto-ID Cartridge)**:
   - EEPROM I2C **24C02** (`U1`) configurata all'indirizzo `0x52` (`A0=0, A1=1, A2=0`), contenente il descrittore hardware univoco del modulo Amstrad CPC.
   - Pin 26 del connettore bus principale `CART_DETECT_N` vincolato permanentemente a massa per rilevamento hardware automatico dell'inserimento scheda.

---

## 2. Centralizzazione Diagnostica sul Front Panel (Daughterboard)

Come prescritto dalle regole ufficiali di progetto `tape-master-rules.md`, l'intera interfaccia diagnostica e di stato per l'operatore è centralizzata sul pannello frontale (`Tape_Master_UI_Panel`), evitando LED duplicati non visibili a banco.

I 5 LED diagnostici standardizzati sul pannello operatore riflettono il funzionamento della cartuccia Amstrad CPC:

| Riferimento UI | Colore | Serigrafia Standard | Segnale Mappato per Amstrad CPC | Funzione Operativa |
| :---: | :---: | :---: | :--- | :--- |
| **D2** | Verde | **`PLAY`** | `CPC_READ` (Pin 4 DIN) | Trasmissione dati verso il computer Amstrad CPC (emulazione nastro / riproduzione CDT) |
| **D3** | Rosso | **`REC`** | `CPC_WRITE` (Pin 5 DIN) | Ricezione dati dal computer Amstrad CPC verso il Tape Master (salvataggio dump) |
| **D4** | Giallo | **`MOTOR`** | `CPC_REM_B` (Pin 3 DIN) | Relè motore chiuso dal CPC o pilotaggio motore attivo da Tape Master |
| **D5** | Blu | **`SIGNAL`** | Sincronismo FSK / Leader Tone | Leader tone $1300\text{ Hz}$ / modulazione $1000/2000\text{ Hz}$ rilevata |
| **D6** | Verde | **`PWR`** | Alimentazione Tape Master | Alimentazione principale di sistema attiva (+5V / +3.3V) e MCU operativo |
| **D10..D19** | 8V/1G/1R | **`AZIMUTH / VU-METER`** | Livello di picco ADC `AUDIO_RAW_L` | Barra VU-meter per regolazione azimut / intensità segnale audio in riproduzione |

---

## 3. Doppia Connettività Esterna

La cartuccia adotta la configurazione a **doppia porta**:
1. **`J2` — Presa DIN 5-Pin 180° Femmina (CUI SDS-50J)**: Connettore orizzontale per il cavo originale Amstrad DIN-5 standard.
2. **`J3` — Pin-Header Maschio Breakout 1x06 passo 2.54 mm**: Pin header a bordo scheda per collegamenti rapidi a banco, oscilloscopio e analizzatore logico.

### Piedinatura Connettori (`J2` e `J3`)

| Pin # J3 | Pin # J2 (DIN-5) | Serigrafia J3 | Segnale | Direzione Elettrica | Descrizione Tecnica |
| :---: | :---: | :--- | :--- | :---: | :--- |
| **1** | **2** | `GND` | `GND` | Riferimento | Massa logica e schermo comune |
| **2** | — | `+5V` | `+5V` | Potenza | Tensione alimentazione Tape Master |
| **3** | **1** | `RA` | `GND` (REM_A) | Ingresso/Uscita | Primo capo contatto relè motore CPC (a massa) |
| **4** | **3** | `RB` | `CPC_REM_B` | Ingresso/Uscita | Secondo capo relè motore CPC (pull-up + sense + switch MOSFET) |
| **5** | **4** | `RD` | `CPC_READ` | Verso CPC (Input) | Segnale audio modulato cassetta verso CPC (EAR / Cassette In) |
| **6** | **5** | `WR` | `CPC_WRITE` | Dal CPC (Output) | Impulsi TTL di registrazione generati dal CPC (MIC / Cassette Out) |

---

## 4. Specifiche Meccaniche e Bordo Scheda

- **Dimensioni**: $74.00\text{ mm} \times 55.00\text{ mm}$.
- **Intagli Meccanici**: Due intagli su `Edge.Cuts` ($6.0\text{ mm} \times 8.0\text{ mm}$) per l'alloggiamento delle leve di ritenuta del connettore `J1` della Mainboard.
- **Complanarità**: Connettore maschio ad angolo retto sulla Mainboard e connettore femmina ad angolo retto sulla Cartuccia (`J1`) permettono alle due schede di rimanere **perfettamente parallele e complanari**, con la cartuccia che estende orizzontalmente all'indietro il corpo principale del Tape Master.

---

## 5. File di Rilascio e Produzione

- Schema Elettrico KiCad: `Tape_Master_Cartridge_Amstrad_CPC.kicad_sch`
- Layout PCB KiCad: `Tape_Master_Cartridge_Amstrad_CPC.kicad_pcb`
- Modello 3D Meccanico Solido PCB Assemblato: `Tape_Master_Cartridge_Amstrad_CPC.step`
- Schema Elettrico Vettoriale: `Tape_Master_Cartridge_Amstrad_CPC.pdf` e `Tape_Master_Cartridge_Amstrad_CPC_Sch.svg`
- Disegno PCB Top Layer: `Tape_Master_Cartridge_Amstrad_CPC_Top.pdf` e `Tape_Master_Cartridge_Amstrad_CPC_Top.svg`
- Disegno PCB Bottom Layer: `Tape_Master_Cartridge_Amstrad_CPC_Bottom.pdf`
- Pacchetto Gerbers & Drills Produzione: cartella `gerbers/`
- Report di Validazione KiCad 9:
  - ERC: `Tape_Master_Cartridge_Amstrad_CPC-erc.rpt` (**0 errori / 0 warning**)
  - DRC: `Tape_Master_Cartridge_Amstrad_CPC-drc.rpt` (**0 violazioni / 0 unconnected / 0 parity**)
