# Tape Master v2 — Cartuccia 09: Texas Instruments TI-99/4A Tape Interface

| Proprietà | Dettaglio / Valore |
| :--- | :--- |
| **Progetto** | Tape Master Exerciser & Signal Digitizer v2 |
| **Modulo** | Cartuccia Espansione #09 — Texas Instruments TI-99/4A (`09_TI99_4A`) |
| **Piattaforme Compatibili** | Texas Instruments TI-99/4 e TI-99/4A (microprocessore a 16 bit TMS9900 @ 3.0 MHz) |
| **Periferiche Supportate** | Registratore a nastro dedicato TI Program Recorder PHP2700, registratori audio standard tramite cavo PHA2000 o cavo seriale maschio/femmina DE-9 dritto |
| **Autore & Hardware Designer** | Alessio Iodice (`alessio67@gmail.com`) |
| **Data di Rilascio** | 2026-11-06 |
| **Revisione** | 2.0 (KiCad 9.0 Nativo) |
| **Licenza** | CC BY-NC-SA 4.0 |
| **Stato Validazione KiCad 9** | **0 Violazioni ERC / 0 Violazioni DRC / 0 Net Non Connesse / 0 Parity Issues** |

---

## 1. Descrizione Architetturale

La **Cartuccia 09: Texas Instruments TI-99/4A** interfaccia il sistema **Tape Master v2** alla porta a nastro a 9 poli posta sul retro della console TI-99/4 e TI-99/4A, adottando il connettore standard **D-Sub 9-pin Femmina (DE-9 Socket)** a montaggio su circuito stampato ([DSUB-9_Socket_Horizontal_P2.77x2.84mm_EdgePinOffset9.40mm](file:///C:/Users/aless/OneDrive/temp/Manutenzione/Kicad_Project/Tape_Master/kicad/v2/Cartridges/09_TI99_4A/Tape_Master_Cartridge_TI99.kicad_pcb)).

L'architettura cassetta del TI-99/4A è unica nel panorama degli home computer degli anni '80:
- È controllata direttamente dal chip **TMS9901 PSI** tramite registri **CRU (Communications Register Unit)**;
- Integra **fotoaccoppiatori e stadi di isolamento ottico** interni alla console;
- Supporta nativamente **due registratori simultanei**: **Cassette 1 (CS1)** dedicato alla lettura, e **Cassette 2 (CS2)** per lettura e scrittura;
- Utilizza modulazione audio FSK a 1200 baud nominali ($1379\text{ Hz}$ per il bit `1` / Mark, $689\text{ Hz}$ per il bit `0` / Space).

### Caratteristiche Elettriche Chiave
1. **Canale Riproduzione Dati (TAPE_IN - Pin 8 DE-9)**:
   - Ingresso audio FSK del computer TI-99/4A (comune per la lettura da CS1 o CS2, associato a CRU Bit 27).
   - Pilotaggio tramite buffer open-collector ad alta velocità **74HCT06** (`U2`) configurato a doppio stadio logico con resistori di pull-up da $4.7\text{ k}\Omega$ (`R7`, `R8`) a `+5V`.
   - Rete passiva di disaccoppiamento AC e calibrazione dinamica: resistore serie $1\text{ k}\Omega$ (`R9`), condensatore di disaccoppiamento da $4.7\ \mu\text{F}$ (`C3`) e resistore di carico shunt da $10\text{ k}\Omega$ (`R10`) verso massa, garantendo un'onda audio calibrata e pulita per il comparatore operazionale interno della console.
2. **Canale Registrazione Dati (CS2_OUT - Pin 3 DE-9)**:
   - Uscita audio FSK dal computer TI-99/4A durante le operazioni di salvataggio (`SAVE "CS2"` o `OLD "CS2"`, CRU Bit 25).
   - Traslazione rapida di livello logico verso i 3.3V tramite partitore resistivo ($R_1 = 2.2\text{ k}\Omega$, $R_2 = 3.3\text{ k}\Omega$) protetto da clamp a doppio diodo Schottky ultra-veloce **BAT54S** (`D1`) verso `+3.3V` e `GND`, collegato alla linea `TAPE_REC_IN` dell'RP2040.
   - Derivazione audio analogica AC con condensatore di blocco DC da $4.7\ \mu\text{F}$ (`C4`), filtro RC passa-basso anti-aliasing ($R_{11} = 1\text{ k}\Omega$, $C_5 = 10\text{ nF}$) e shunt da $10\text{ k}\Omega$ (`R12`) collegata al canale ADC `AUDIO_RAW_L` per il pilotaggio dinamico del display OLED e del VU-meter a 10 segmenti del front panel.
3. **Gestione Indipendente del Doppio Motore (CS1 e CS2)**:
   - **Registratore 1 (`TI_CS1_MOTOR_P`, Pin 1 DE-9 - CRU Bit 22)**:
     - Resistore di pull-up da $10\text{ k}\Omega$ (`R3`) a `+5V`.
     - Partitore $2.2\text{ k}\Omega / 3.3\text{ k}\Omega$ (`R4`, `R5`) con clamp Schottky **BAT54S** (`D2`) attestato sulla linea `MOTOR_SENSE` del bus universale. Quando il computer attiva il motore di CS1, il contatto dell'optoisolatore interno alla console chiude Pin 1 a massa, portando `MOTOR_SENSE` a 0V (attivo basso).
     - N-MOSFET di commutazione **2N7002** (`Q1`) pilotato dalla linea `MOTOR_CTRL` (con resistore serie di gate `R13` da $100\ \Omega$ e pull-down `R14` da $100\text{ k}\Omega$) per consentire al Tape Master di azionare direttamente il motore di un registratore esterno a banco.
   - **Registratore 2 (`TI_CS2_MOTOR_P`, Pin 6 DE-9 - CRU Bit 23)**:
     - Resistore di pull-up da $10\text{ k}\Omega$ (`R15`) a `+5V`.
     - Partitore $2.2\text{ k}\Omega / 3.3\text{ k}\Omega$ (`R16`, `R17`) con clamp Schottky **BAT54S** (`D4`) attestato sulla linea ausiliaria configurabile **`AUX_GPIO1`** (Pin 21 del bus a 40 pin), consentendo al firmware del Tape Master di monitorare separatamente e in tempo reale lo stato del secondo registratore.
4. **Campionamento Audio Gate (`TI_AUDIO_GATE` - Pin 4 DE-9 - CRU Bit 24)**:
   - Partitore resistivo ($R_{18} = 2.2\text{ k}\Omega$, $R_{19} = 3.3\text{ k}\Omega$) con clamp Schottky **BAT54S** (`D5`) collegato alla linea **`AUX_GPIO2`** (Pin 22 del bus a 40 pin) per rilevare l'abilitazione hardware del segnale audio operata dalla console.
5. **Protezione ESD / Transitori**:
   - Due array integrati a diodi TVS ultra-rapidi a bassissima capacità **USBLC6-2SC6** (`U3` e `U4`, package SOT-23-6L) proteggono le linee esterne del connettore DE-9 da scariche elettrostatiche fino a $\pm 15\text{ kV}$.
6. **Smart Plug & Play (Auto-ID Cartridge)**:
   - EEPROM I2C seriale **24C02** (`U1`) all'indirizzo `0x50` con descrittore hardware binario univoco TI-99/4A.
   - Pin 26 del bus principale `CART_DETECT_N` vincolato permanentemente a massa per rilevamento hardware istantaneo all'inserimento.

---

## 2. Centralizzazione Diagnostica sul Front Panel (Daughterboard)

Come prescritto dalle regole ufficiali di progetto `tape-master-rules.md`, tutti i LED diagnostici sono centralizzati sul pannello frontale (`Tape_Master_UI_Panel`), evitando duplicati non visibili a banco sulla cartuccia.

I 5 LED diagnostici standardizzati sul pannello operatore riflettono il funzionamento della cartuccia TI-99/4A:

| Riferimento UI | Colore | Serigrafia Standard | Segnale Mappato per TI-99/4A | Funzione Operativa |
| :---: | :---: | :---: | :--- | :--- |
| **D2** | Verde | **`PLAY`** | `TI_TAPE_IN` (Pin 8 DE-9) | Trasmissione dati FSK verso la console TI-99 (emulazione nastro / riproduzione file WAV o dump) |
| **D3** | Rosso | **`REC`** | `TI_CS2_OUT` (Pin 3 DE-9) | Ricezione dati FSK dalla console TI-99/4A verso il Tape Master (salvataggio dump da `SAVE "CS2"`) |
| **D4** | Giallo | **`MOTOR`** | `TI_CS1_MOTOR_P` (Pin 1 DE-9) | Relè motore CS1 chiuso dalla console o forzatura motore esterna attiva |
| **D5** | Blu | **`SIGNAL`** | Rilevamento portante FSK | Rilevamento toni FSK a $1379\text{ Hz}$ (Mark) o $689\text{ Hz}$ (Space) |
| **D6** | Verde | **`PWR`** | Alimentazione Tape Master | Alimentazione principale di sistema attiva (+5V / +3.3V) e MCU operativo |
| **D10..D19** | 8V/1G/1R | **`AZIMUTH / VU-METER`** | Livello picco ADC `AUDIO_RAW_L` | Barra VU-meter per regolazione azimut / intensità segnale audio analogico in ingresso |

---

## 3. Doppia Connettività Esterna

La cartuccia adotta l'architettura a **doppia porta**:
1. **`J2` — Presa D-Sub 9-Pin Femmina (DE-9 Socket)**: Connettore orizzontale a montaggio su circuito stampato conforme al pinout originale TI-99/4A. Permette il collegamento diretto alla console tramite cavo seriale dritto standard 1:1 maschio-femmina.
2. **`J3` — Pin-Header Maschio Breakout 1x09 passo 2.54 mm**: Pin-header orizzontale serigrafato posto sul bordo inferiore del PCB, progettato per collegamenti rapidi a banco, oscilloscopio, analizzatore di stati logici e cavi volanti.

### Piedinatura Connettori (`J2` e `J3`)

| Pin # J3 | Pin # J2 (DE-9) | Serigrafia J3 | Segnale | Direzione Elettrica | Descrizione Tecnica TI-99 |
| :---: | :---: | :--- | :--- | :---: | :--- |
| **1** | **2, 5, 7, 9** | `GND` | `GND` | Riferimento | Massa comune di segnale e ritorno schermo |
| **2** | — | `+5V` | `+5V` | Potenza | Tensione alimentazione Tape Master per test a banco |
| **3** | **1** | `M1` | `TI_CS1_MOTOR_P` | Dalla console (Output) | Comando motore registratore 1 (CS1, CRU Bit 22) |
| **4** | **3** | `OUT` | `TI_CS2_OUT` | Dalla console (Output) | Uscita audio FSK da console a registratore 2 (MIC, CRU Bit 25) |
| **5** | **4** | `GATE` | `TI_AUDIO_GATE` | Dalla console (Output) | Segnale di abilitazione e gating audio (CRU Bit 24) |
| **6** | **6** | `M2` | `TI_CS2_MOTOR_P` | Dalla console (Output) | Comando motore registratore 2 (CS2, CRU Bit 23) |
| **7** | **8** | `IN` | `TI_TAPE_IN` | Verso console (Input) | Ingresso audio FSK al comparatore della console (EAR, CRU Bit 27) |
| **8** | **2, 5, 7, 9** | `GND` | `GND` | Riferimento | Ritorno di massa ausiliario |
| **9** | **2, 5, 7, 9** | `GND` | `GND` | Riferimento | Ritorno di massa ausiliario |

---

## 4. Specifiche Meccaniche e Bordo Scheda

- **Dimensioni**: $74.00\text{ mm} \times 55.00\text{ mm}$ conforme allo standard unificato delle Cartucce Tape Master v2.
- **Intagli Meccanici di Blocco**: Due intagli precisi su layer `Edge.Cuts` ($6.0\text{ mm} \times 8.0\text{ mm}$) per l'alloggiamento delle leve di ritenuta del connettore `J1` della Mainboard.
- **Complanarità**: Connettore maschio ad angolo retto sulla Mainboard e connettore femmina ad angolo retto sulla Cartuccia (`J1`) garantiscono una perfetta complanarità tra le due schede.
- **Serigrafia di Copyright**: Prescritta e presente su `F.Silkscreen` con la dicitura ufficiale `© 2026 by Alessio Iodice`.

---

## 5. File di Rilascio e Produzione

- Schema Elettrico KiCad: `Tape_Master_Cartridge_TI99.kicad_sch`
- Layout PCB KiCad: `Tape_Master_Cartridge_TI99.kicad_pcb`
- Modello 3D Meccanico Solido PCB Assemblato: `Tape_Master_Cartridge_TI99.step`
- Schema Elettrico Vettoriale: `Tape_Master_Cartridge_TI99.pdf` e `Tape_Master_Cartridge_TI99_Sch.svg`
- Disegno PCB Top Layer: `Tape_Master_Cartridge_TI99_Top.pdf` e `Tape_Master_Cartridge_TI99_Top.svg`
- Disegno PCB Bottom Layer: `Tape_Master_Cartridge_TI99_Bottom.pdf`
- Pacchetto Gerbers & Drills Produzione: cartella `gerbers/`
- Report di Validazione KiCad 9:
  - ERC: `Tape_Master_Cartridge_TI99-erc.rpt` (**0 errori / 0 warning**)
  - DRC: `Tape_Master_Cartridge_TI99-drc.rpt` (**0 violazioni / 0 unconnected / 0 parity**)
