# Tape Master v2 — Cartuccia 06: MSX Standard Tape Interface

| Proprietà | Dettaglio / Valore |
| :--- | :--- |
| **Progetto** | Tape Master Exerciser & Signal Digitizer v2 |
| **Modulo** | Cartuccia Espansione #06 — MSX Standard (`06_MSX_Standard`) |
| **Piattaforme Compatibili** | Standard MSX1, MSX2, MSX2+, MSX Turbo R (Sony HitBit, Philips NMS/VG, Yamaha CX, Panasonic FS, Sanyo, National, Canon, Pioneer, Spectravideo, Casio, etc.) |
| **Periferiche Supportate** | Registratori a cassetta MSX dedicati (Sony SDC-500/600, Philips NMS-1515, Panasonic RQ-8300, etc.), registratori portatili generici via cavo DIN-8 a 3 jack (EAR, MIC, REM), interfacce turbo (CasLink, etc.) |
| **Autore & Hardware Designer** | Alessio Iodice (`alessio67@gmail.com`) |
| **Data di Rilascio** | 2026-11-06 |
| **Revisione** | 2.0 (KiCad 9.0 Nativo) |
| **Licenza** | CC BY-NC-SA 4.0 |
| **Stato Validazione KiCad 9** | **0 Violazioni ERC / 0 Violazioni DRC / 0 Net Non Connesse / 0 Parity Issues** |

---

## 1. Descrizione Architetturale

La **Cartuccia 06: MSX Standard** interfaccia il sistema **Tape Master v2** alla porta a cassetta universale standardizzata per l'intero ecosistema **MSX** (costruttori giapponesi ed europei), adottando il connettore circolare **DIN 8-Pin 270°** (standard MSX e connettore CUI/Same Sky SDS-80J).

### Caratteristiche Elettriche Chiave
1. **Canale Riproduzione Dati (CMTIN - Pin 5 DIN)**:
   - Ingresso del registratore nel computer MSX (modulazione audio FSK: $1200\text{ baud} \rightarrow 1200/2400\text{ Hz}$, oppure $2400\text{ baud} \rightarrow 2400/4800\text{ Hz}$).
   - Pilotaggio ad alta velocità e precisione tramite buffer open-collector **74HCT06** (`U2`) configurato a doppio stadio logico con pull-up da $4.7\text{ k}\Omega$ (`R7`, `R8`) a `+5V`.
   - Rete di attenuazione, disaccoppiamento AC e calibrazione del livello audio verso il circuito comparatore/amplificatore interno dell'MSX: resistenza serie $1\text{ k}\Omega$ (`R9`), condensatore di disaccoppiamento AC $4.7\ \mu\text{F}$ (`C3`) e resistenza di carico $10\text{ k}\Omega$ (`R10`) a massa.
2. **Canale Registrazione Dati (CMTOUT - Pin 4 DIN)**:
   - Uscita audio analogica generata dal computer MSX durante il comando `CSAVE` o `SAVE "CAS:"` (ampiezza tipica $\approx 1 \dots 2\text{ V}_{pp}$ centrata a $0\text{ V}$ o livello logico con componente DC).
   - Traslazione di livello verso il bus a 3.3V tramite partitore resistivo ($R_1 = 2.2\text{ k}\Omega$, $R_2 = 3.3\text{ k}\Omega$) protetto da clamp a doppio diodo Schottky ultra-veloce **BAT54S** (`D1`) verso `+3.3V` e `GND`, collegato alla linea `TAPE_REC_IN` del microcontrollore Tape Master.
   - Derivazione audio analogica AC con condensatore di blocco da $4.7\ \mu\text{F}$ (`C4`), filtro RC passa-basso anti-aliasing ($R_{11} = 1\text{ k}\Omega$, $C_5 = 10\text{ nF}$) e resistenza di carico $10\text{ k}\Omega$ (`R12`) collegata al canale ADC `AUDIO_RAW_L` per il monitoraggio continuo sul display OLED e sul VU-meter a 10 segmenti del pannello frontale.
3. **Controllo e Monitoraggio Motore (REMOTE - Pin 6 REM+ & Pin 7 REM-)**:
   - Nello standard MSX, il controllo motore è affidato a un relè interno pilotato dal chip PPI (8255, porta C, bit 4). I due terminali del relè sono attestati su Pin 6 (`REM+`) e Pin 7 (`REM-`).
   - **Rilevamento Chiamata Motore (`MOTOR_SENSE`)**: Pin 6 (`REM+`) è vincolato a massa tramite jumper/resistore da $0\ \Omega$ (`R15`). Pin 7 (`REM-`) è polarizzato a +5V con pull-up da $10\text{ k}\Omega$ (`R3`) e collegato al partitore resistivo ($R_4 = 2.2\text{ k}\Omega$, $R_5 = 3.3\text{ k}\Omega$) con clamp Schottky **BAT54S** (`D2`) verso `MOTOR_SENSE`. Quando il computer MSX attiva il comando `MOTOR ON`, il relè interno chiude il circuito tra REM+ e REM-, portando Pin 7 a massa e segnalando al microcontrollore lo stato attivo a livello basso ($0\text{ V}$).
   - **Pilotaggio Motore Attivo Registratore Esterno (`MOTOR_CTRL`)**: N-MOSFET di commutazione **2N7002** (`Q1`) collegato tra Pin 7 e Pin 6 (massa), con gate pilotato da `MOTOR_CTRL` tramite resistenza di gate da $100\ \Omega$ (`R13`) e resistenza di pull-down da $100\text{ k}\Omega$ (`R14`). Consente al Tape Master di azionare autonomamente il motore di un registratore MSX reale durante le procedure di taratura, acquisizione automatizzata o test di durata.
4. **Protezione ESD / Transitori (TVS Diode Array)**:
   - Array di diodi TVS ultra-rapido a bassa capacità **USBLC6-4SC6** (`U3`, package SOT-23-6L) a protezione diretta di tutte le linee esposte verso l'esterno (`CMTOUT`, `CMTIN`, `REM+`, `REM-`).
5. **Smart Plug & Play (Auto-ID Cartridge)**:
   - EEPROM seriale I2C **24C02** (`U1`) configurata all'indirizzo `0x50` (`A0=0, A1=0, A2=0`), contenente il descrittore binario univoco della cartuccia MSX Standard (Vendor ID, Board Revision, pin mapping e baud rate predefiniti).
   - Pin 26 del connettore bus principale `CART_DETECT_N` collegato permanentemente a massa per rilevamento hardware istantaneo all'inserimento.

---

## 2. Centralizzazione Diagnostica sul Front Panel (Daughterboard)

In ottemperanza alle regole di progetto `tape-master-rules.md`, tutti gli indicatori di stato e la diagnostica visiva sono centralizzati sul pannello frontale (`Tape_Master_UI_Panel`), evitando LED duplicati sulla cartuccia che risulterebbero coperti a banco dall'innesto del cavo DIN e dei connettori.

I 5 LED diagnostici standardizzati sul pannello frontale riflettono il funzionamento della cartuccia MSX Standard:

| Riferimento UI | Colore | Serigrafia Standard | Segnale Mappato per MSX Standard | Funzione Operativa |
| :---: | :---: | :---: | :--- | :--- |
| **D2** | Verde | **`PLAY`** | `CMTIN` (Pin 5 DIN) | Trasmissione dati verso il computer MSX (emulazione nastro / riproduzione file CAS / WAV) |
| **D3** | Rosso | **`REC`** | `CMTOUT` (Pin 4 DIN) | Ricezione dati dal computer MSX verso il Tape Master (salvataggio dump da `CSAVE`) |
| **D4** | Giallo | **`MOTOR`** | `REM-` / `REM+` (Pin 6/7 DIN) | Relè motore chiuso dal comando `MOTOR ON` dell'MSX o forzatura motore attiva |
| **D5** | Blu | **`SIGNAL`** | Rilevamento portante FSK | Leader tone $1200/2400\text{ Hz}$ o modulazione dati MSX rilevata |
| **D6** | Verde | **`PWR`** | Alimentazione Tape Master | Alimentazione principale di sistema attiva (+5V / +3.3V) e MCU operativo |
| **D10..D19** | 8V/1G/1R | **`AZIMUTH / VU-METER`** | Livello picco ADC `AUDIO_RAW_L` | Barra VU-meter per regolazione azimut / ampiezza segnale audio analogico `CMTOUT` |

---

## 3. Doppia Connettività Esterna

La cartuccia adotta l'architettura a **doppia porta**:
1. **`J2` — Presa DIN 8-Pin 270° Femmina (CUI SDS-80J)**: Connettore circolare orizzontale a montaggio su circuito stampato per il cavo originale MSX a 8 poli.
2. **`J3` — Pin-Header Maschio Breakout 1x08 passo 2.54 mm**: Pin-header orizzontale serigrafato posto sul bordo inferiore del PCB, progettato per collegamenti rapidi a banco, oscilloscopio, analizzatore di stati logici e cavi volanti.

### Piedinatura Connettori (`J2` e `J3`)

| Pin # J3 | Pin # J2 (DIN-8) | Serigrafia J3 | Segnale | Direzione Elettrica | Descrizione Tecnica MSX |
| :---: | :---: | :--- | :--- | :---: | :--- |
| **1** | **1, 2, 3, 8** | `GND` | `GND` | Riferimento | Massa comune di segnale e schermo del cavo |
| **2** | — | `+5V` | `+5V` | Potenza | Tensione alimentazione Tape Master per test a banco |
| **3** | **1, 2, 3, 8** | `GND` | `GND` | Riferimento | Massa di ritorno addizionale |
| **4** | **4** | `OUT` | `MSX_CMTOUT` | Dal computer (Output) | Uscita registratore MSX (Cassette Data Out dal computer al nastro) |
| **5** | **5** | `IN` | `MSX_CMTIN` | Al computer (Input) | Ingresso registratore MSX (Cassette Data In dal nastro al computer) |
| **6** | **6** | `R+` | `MSX_REM_PLUS` | Contatto relè MSX | Terminale positivo relè motore (a massa sulla scheda) |
| **7** | **7** | `R-` | `MSX_REM_MINUS` | Contatto relè MSX | Terminale negativo relè motore (pull-up + sense + switch MOSFET) |
| **8** | **1, 2, 3, 8** | `GND` | `GND` | Riferimento | Massa logica e riferimento schermatura |

---

## 4. Specifiche Meccaniche e Bordo Scheda

- **Dimensioni Form Factor**: $74.00\text{ mm} \times 55.00\text{ mm}$ conforme allo standard unificato delle Cartucce Tape Master v2.
- **Intagli Meccanici di Blocco**: Due intagli precisi su layer `Edge.Cuts` ($6.0\text{ mm} \times 8.0\text{ mm}$) per l'alloggiamento delle leve di ritenuta del connettore `J1` della Mainboard.
- **Complanarità e Disposizione**:
  - Connettore bus maschio ad angolo retto sulla Mainboard e connettore femmina ad angolo retto sulla Cartuccia (`J1`) garantiscono una perfetta complanarità tra le due schede.
  - La cartuccia estende la Mainboard orizzontalmente all'indietro, mantenendo i cavi e il connettore DIN-8 lontano dal campo visivo dell'operatore e dai comandi frontali dell'UI Panel.
- **Serigrafia di Copyright**: Prescritta e presente su `F.Silkscreen` con la dicitura ufficiale `© 2026 by Alessio Iodice`.

---

## 5. File di Rilascio e Produzione

- Schema Elettrico KiCad: `Tape_Master_Cartridge_MSX.kicad_sch`
- Layout PCB KiCad: `Tape_Master_Cartridge_MSX.kicad_pcb`
- Modello 3D Meccanico Solido PCB Assemblato: `Tape_Master_Cartridge_MSX.step`
- Schema Elettrico Vettoriale: `Tape_Master_Cartridge_MSX.pdf` e `Tape_Master_Cartridge_MSX_Sch.svg`
- Disegno PCB Top Layer: `Tape_Master_Cartridge_MSX_Top.pdf` e `Tape_Master_Cartridge_MSX_Top.svg`
- Disegno PCB Bottom Layer: `Tape_Master_Cartridge_MSX_Bottom.pdf`
- Pacchetto Gerbers & Drills Produzione: cartella `gerbers/`
- Report di Validazione KiCad 9:
  - ERC: `Tape_Master_Cartridge_MSX-erc.rpt` (**0 errori / 0 warning**)
  - DRC: `Tape_Master_Cartridge_MSX-drc.rpt` (**0 violazioni / 0 unconnected / 0 parity**)
