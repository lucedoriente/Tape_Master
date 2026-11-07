# Tape Master v2 - Cartuccia 12: Sharp MZ Series (MZ-700 / MZ-800 / MZ-80K)

| Proprietà | Dettaglio / Valore |
| :--- | :--- |
| **Progetto** | Tape Master Exerciser & Signal Digitizer v2 |
| **Modulo** | Cartuccia Espansione #12 - Sharp MZ Series (`12_Sharp_MZ`) |
| **Piattaforme Compatibili** | Sharp MZ-80K, MZ-80C, MZ-80A, MZ-80B, MZ-700 (MZ-711, MZ-721, MZ-731), MZ-800 (MZ-811, MZ-821, MZ-831), MZ-1500, MZ-2000 |
| **Periferiche Supportate** | Registratori a cassette dedicati Sharp (data recorder serie MZ-1T01), registratori esterni standard via cavi 3.5mm EAR/MIC, cavo di collegamento interno/esterno porta CMT (header P-12 a 9 pin) |
| **Autore & Hardware Designer** | Alessio Iodice (`alessio67@gmail.com`) |
| **Data di Rilascio** | 2026-11-06 |
| **Revisione** | 2.0 (KiCad 9.0 Nativo) |
| **Licenza** | CC BY-NC-SA 4.0 |
| **Stato Validazione KiCad 9** | **0 Violazioni ERC / 0 Violazioni DRC / 0 Net Non Connesse / 0 Parity Issues** |

---

## 1. Descrizione Architetturale

La **Cartuccia 12: Sharp MZ Series** interfaccia l'architettura **Tape Master v2** alla porta a cassetta della serie di celebri personal computer giapponesi **Sharp MZ**, coprendo sia la storica generazione MZ-80 sia le diffuse famiglie MZ-700 ed MZ-800.
Nei sistemi Sharp MZ il sistema di registrazione a nastro è hardware-driven: la scheda madre include l'hardware di modulazione/demodulazione temporale basato sui controller programmabili Intel 8255 PPI e 8253 PIT, permettendo una velocità di trasferimento nominale di **1200 baud** (PWM con impulsi di $32\ \mu\text{s}$ per il bit '0' e $64\ \mu\text{s}$ per il bit '1').

Il modulo cartuccia offre **tripla interfaccia fisica**:
1. **Connettore CMT 9-Pin standard (`J4`, Header maschio 2.54 mm passo standard P-12)** per il collegamento diretto al cavo a nastro del registratore interno Sharp (o alla porta CMT posteriore dei modelli muniti di presa Molex/header).
2. **Doppia presa Jack audio standard da 3.5 mm (`J2` EX-READ, `J3` EX-WRITE)** conforme alle uscite/ingressi dei modelli Sharp MZ-711 ed MZ-811.
3. **Pin-header maschio passo 2.54 mm di Breakout a banco (`J5`, 1x08)** per il monitoraggio contemporaneo di tutti i segnali logici e analogici tramite sonde di oscilloscopio e analizzatore di stati logici.

---

### Caratteristiche Elettriche Chiave
1. **Canale Riproduzione Dati (READ / EX-READ)**:
   - **Uscita Logica TTL (`READ_BUF_OUT` - Pin 8 CMT)**: Pilotata dal buffer esadecimale ad alta velocità open-collector **74HCT06** (`U2`) configurato a doppio stadio logico con resistenze di pull-up da $4.7\text{ k}\Omega$ (`R7`, `R8`) verso `+5V`, per iniettare impulsi digitali privi di jitter direttamente all'ingresso `PB4` della PPI 8255 dello Sharp MZ.
   - **Uscita Audio Analogica (`SHARP_READ` - Pin 2 CMT e Tip Jack `J2`)**: Rete di disaccoppiamento AC e attenuazione passiva ($R_9 = 1\text{ k}\Omega$, $C_3 = 4.7\ \mu\text{F}$, $R_{10} = 10\text{ k}\Omega$) per l'interfacciamento line-level a $1.0\text{ V}_{pp}$ verso i comparatori audio analogici dell'MZ.
   - **Ingresso DAC Ausiliario**: Canale analogico continuo proveniente dal DAC della scheda madre (`AUDIO_DAC_L`) via disaccoppiamento AC ($C_6 = 4.7\ \mu\text{F}$) e resistenza serie $2.2\text{ k}\Omega$ (`R6`).
2. **Canale Registrazione Dati (WRITE / EX-WRITE)**:
   - Riceve sia il segnale audio proveniente dalla presa jack `J3` sia il flusso logico a 5V TTL proveniente dalla porta CMT (Pin 1 / Pin 7).
   - Condizionamento di livello verso la logica 3.3V tramite partitore resistivo ($R_1 = 2.2\text{ k}\Omega$, $R_2 = 3.3\text{ k}\Omega$) e doppio diodo di clamping Schottky ad altissima velocità **BAT54S** (`D1`) collegato a `+3.3V` e `GND`, instradato su `TAPE_REC_IN`.
   - Ramo di campionamento analogico ad alta impedenza ($C_4 = 4.7\ \mu\text{F}$, $R_{11} = 1\text{ k}\Omega$, $C_5 = 10\text{ nF}$, $R_{12} = 10\text{ k}\Omega$) collegato a `AUDIO_RAW_L` per la digitalizzazione ADC e il pilotaggio del VU-meter frontale.
3. **Rilevamento e Controllo Motore (`SHARP_MOTOR`)**:
   - Collegato al Pin 4 dell'header CMT: include pull-up a +5V (`R3` da $10\text{ k}\Omega$), partitore di livello ($R_4 = 2.2\text{ k}\Omega$, $R_5 = 3.3\text{ k}\Omega$) e diodo di protezione Schottky **BAT54S** (`D2`) verso `MOTOR_SENSE`.
   - Controllo attivo automatico tramite MOSFET N-Channel **2N7002** (`Q1`) pilotato da `MOTOR_CTRL` (con resistenza di gate $100\ \Omega$ `R13` e pull-down $100\text{ k}\Omega$ `R14`) per simulare a banco il relè motore o consentire lo start/stop controllato dal PC.
4. **Interblocco Automatico Tasto PLAY (`SHARP_SENSE`)**:
   - Sulle macchine Sharp MZ, la ROM di sistema controlla la linea hardware `SENSE` (Pin 5 CMT): se il tasto PLAY del registratore a cassette non è abbassato (segnale a livello alto), la ROM si arresta visualizzando la scritta "PLAY" su schermo.
   - Sulla cartuccia #12, la linea è governata dal MOSFET N-Channel **2N7002** (`Q2`), comandato dal segnale `TAPE_SENSE` del microcontrollore tramite gate resistor $100\ \Omega$ (`R15`) e pull-down $100\text{ k}\Omega$ (`R16`), con clamping di protezione **BAT54S** (`D4`): il Tape Master forza a massa la linea all'avvio dell'emulazione, sbloccando istantaneamente il caricamento automatico senza richiedere l'intervento dell'utente.
   - **Jumper Forzatura Hardware (`JP1` - FORCE PLAY)**: Jumper a 2 pin passo 2.54 mm per forzare permanentemente a massa la linea `SENSE` durante prove manuali a banco.
5. **Monitoraggio Alimentazione Host (`D5` - HOST 5V)**:
   - Conforme alle regole di progetto per cartucce di espansione: micro-LED verde a basso assorbimento `D5` con resistenza di polarizzazione `R17` ($1\text{ k}\Omega$) collegato al Pin 6 (`+5V_HOST`) del connettore CMT, per verificare visivamente l'erogazione di alimentazione da parte del computer acceso.
6. **Protezione ESD / Transitori**:
   - Array di soppressione TVS a basso carico capacitivo **USBLC6-2SC6** (`D3`) su tutte le 4 linee esterne esposte (`SHARP_READ`, `SHARP_WRITE`, `SHARP_MOTOR`, `SHARP_SENSE`).
7. **Smart Plug & Play (Auto-ID Cartridge)**:
   - EEPROM seriale I2C **24C02** (`U1`) configurata all'indirizzo standard `0x50` (`A0=0, A1=0, A2=0`), contenente il descrittore hardware univoco del modulo Sharp MZ.
   - Pin 26 del connettore bus principale `CART_DETECT_N` vincolato permanentemente a massa per rilevamento hardware automatico dell'inserimento scheda.

---

## 2. Centralizzazione Diagnostica sul Front Panel (Daughterboard)

Come prescritto dalle regole ufficiali di progetto `tape-master-rules.md`, l'intera interfaccia diagnostica e di stato per l'operatore è centralizzata sul pannello frontale (`Tape_Master_UI_Panel`), evitando LED duplicati non visibili a banco.

I 5 LED diagnostici standardizzati sul pannello operatore riflettono il funzionamento della cartuccia Sharp MZ:

| Riferimento UI | Colore | Serigrafia Standard | Segnale Mappato per Sharp MZ | Funzione Operativa |
| :---: | :---: | :---: | :--- | :--- |
| **D2** | Verde | **`PLAY`** | `READ` / `EX-READ` (Pin 2/8 CMT) | Riproduzione dati verso lo Sharp MZ (emulazione nastro / riproduzione MZF / MZT / WAV) |
| **D3** | Rosso | **`REC`** | `WRITE` / `EX-WRITE` (Pin 1/7 CMT) | Acquisizione flusso audio/dati dallo Sharp MZ verso il Tape Master (salvataggio dump) |
| **D4** | Giallo | **`MOTOR`** | `SHARP_MOTOR` (Pin 4 CMT) | Linea motore abilitata dal computer o azionamento remoto attivo |
| **D5** | Blu | **`SIGNAL`** | Impulsi PWM / Transizioni dati | Rilevamento portante e transizioni di bit (1200 baud Manchester PWM) |
| **D6** | Verde | **`PWR`** | Alimentazione Tape Master | Alimentazione principale di sistema attiva (+5V / +3.3V) e MCU operativo |
| **D10..D19** | 8V/1G/1R | **`AZIMUTH / VU-METER`** | Livello di picco ADC `AUDIO_RAW_L` | Barra VU-meter per regolazione azimut / intensità segnale audio in riproduzione |

---

## 3. Piedinatura Connettori

### Connettore CMT 9-Pin Standard Sharp MZ (`J4`, Header 1x09 Passo 2.54 mm)
| Pin | Simbolo | Tipo | Descrizione | Collegamento Tape Master |
| :---: | :---: | :---: | :--- | :--- |
| **1** | `WR` | Uscita Host | Uscita audio a nastro (`EX_WRITE`) | Rete partitore / clamp `D1` $\rightarrow$ `TAPE_REC_IN` |
| **2** | `RD` | Ingresso Host | Ingresso audio da registratore (`EX_READ`) | Rete attenuatore / AC coupling `C3` $\leftarrow$ `SHARP_READ` |
| **3** | `GND` | Alimentazione | Massa di sistema | `GND` |
| **4** | `MOT` | Uscita Host | Comando accensione motore registratore | Partitore `R4/R5` $\rightarrow$ `MOTOR_SENSE` e MOSFET `Q1` |
| **5** | `SNS` | Ingresso Host | Rilevamento tasto PLAY premuto (Attivo BASSO) | MOSFET `Q2` (`TAPE_SENSE`) e Jumper `JP1` (Force Play) |
| **6** | `+5V` | Uscita Host | Alimentazione +5V proveniente dal computer | Monitor LED `D5` (`HOST 5V`) |
| **7** | `TTL_W` | Uscita Host | Uscita dati logica TTL diretta (8255 PPI PC1) | In parallelo a linea `SHARP_WRITE` |
| **8** | `TTL_R` | Ingresso Host | Ingresso dati logico TTL diretto (8255 PPI PB4) | Uscita buffer inverter `U2` (`READ_BUF_OUT`) |
| **9** | `GND` | Alimentazione | Massa di sistema | `GND` |

### Pin Header Breakout Banco (`J5`, 1x08 Passo 2.54 mm)
- Pin 1: `GND` (Massa di sistema)
- Pin 2: `+5V` (Host computer power supply)
- Pin 3: `RD` (Segnale audio di lettura analogico)
- Pin 4: `TTL_R` (Segnale dati di lettura digitale TTL 5V)
- Pin 5: `WR` (Segnale dati di scrittura host)
- Pin 6: `MOT` (Segnale di controllo motore host)
- Pin 7: `SNS` (Segnale interblocco Play Sense)
- Pin 8: `+3V3` (Alimentazione Tape Master logica 3.3V)

### Jumper Forzatura PLAY (`JP1`, 1x02 Passo 2.54 mm)
- **Pin 1-2 Chiusi (Jumper inserito)**: Linea `SHARP_SENSE` collegata permanentemente a massa; consente l'avvio immediato della lettura sui monitor ROM MZ senza dover simulare la pressione meccanica del tasto PLAY.
- **Pin 1-2 Aperti (Jumper rimosso)**: Controllo automatico software della linea `SENSE` demandato interamente al Tape Master tramite MOSFET `Q2`.

---

## 4. File di Progetto e Deliverable di Fabbricazione

La cartella di progetto contiene l'intera suite di file di fabbricazione e documentazione:

| File | Tipo | Descrizione |
| :--- | :---: | :--- |
| `Tape_Master_Cartridge_Sharp_MZ.kicad_pro` | Progetto KiCad 9 | File configurazione impostazioni, regole DRC ed ERC |
| `Tape_Master_Cartridge_Sharp_MZ.kicad_sch` | Schema Elettrico | Schema elettrico gerarchico nativo KiCad 9 |
| `Tape_Master_Cartridge_Sharp_MZ.kicad_pcb` | Layout PCB | Layout sbrogliato a 2 layer con piani di massa continui |
| `Tape_Master_Cartridge_Sharp_MZ.step` | Modello 3D Meccanico | Solido CAD 3D completo di connettori 3.5mm, header, IC e passivi |
| `Tape_Master_Cartridge_Sharp_MZ_Top.pdf` | Vettoriale PDF | Master top layer serigrafia e rame per ispezione grafica |
| `Tape_Master_Cartridge_Sharp_MZ_Bottom.pdf` | Vettoriale PDF | Master bottom layer serigrafia e rame per ispezione grafica |
| `Tape_Master_Cartridge_Sharp_MZ_Top.svg` | Grafica Vettoriale SVG | Rendering SVG scalabile del circuito stampato assemblato |
| `Tape_Master_Cartridge_Sharp_MZ_Sch.svg` | Grafica Vettoriale SVG | Rendering vettoriale completo dello schema elettrico |
| `Tape_Master_Cartridge_Sharp_MZ.pdf` | Documento PDF | Schema elettrico stampato con cartiglio compilato |
| `Tape_Master_Cartridge_Sharp_MZ_erc.rpt` | Report Qualità ERC | Report di validazione elettrica (**0 Violazioni**) |
| `Tape_Master_Cartridge_Sharp_MZ_drc.rpt` | Report Qualità DRC | Report di verifica produzione PCB (**0 Violazioni / 0 Unconnected / 0 Parity Issues**) |
| `gerbers/` | Cartella Produzione CAM | File Gerber RS-274X e forature Excellon pronti per JLCPCB / PCBWay |
| `datasheets/` | Documentazione Tecnica | Specifiche tecniche di protocollo CMT ed interfaccia cassette Sharp MZ |
