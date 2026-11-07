# Tape Master v2 - Cartuccia 13: Raw Head Probing & Stereo Digitizer

| Proprietà | Dettaglio / Valore |
| :--- | :--- |
| **Progetto** | Tape Master Exerciser & Signal Digitizer v2 |
| **Modulo** | Cartuccia Espansione #13 - Raw Head Probing & Stereo Digitizer (`13_Raw_Head_Stereo_Digitizer`) |
| **Piattaforme Compatibili** | Strumentazione universale di laboratorio: qualsiasi registratore magnetico a cassetta vintage (meccanica nuda, deck Hi-Fi, walkman, datassette senza elettronica di amplificazione o con testina sfilata/intercettata) |
| **Applicazione Primaria** | Riversamento archeologico di precisione, digitalizzazione stereofonica a 24-bit/192kHz del segnale raw captato direttamente dalla bobina della testina magnetica, calibrazione azimut e de-azimutting software con compensazione della fase tra i due canali |
| **Autore & Hardware Designer** | Alessio Iodice (`alessio67@gmail.com`) |
| **Data di Rilascio** | 2026-11-06 |
| **Revisione** | 2.0 (KiCad 9.0 Nativo) |
| **Licenza** | CC BY-NC-SA 4.0 |
| **Stato Validazione KiCad 9** | **0 Violazioni ERC / 0 Violazioni DRC / 0 Net Non Connesse / 0 Parity Issues** |

---

## 1. Descrizione Architetturale

La **Cartuccia 13: Raw Head Probing & Stereo Digitizer** è il modulo di front-end analogico di precisione per il sistema **Tape Master v2**, progettato specificamente per il restauro archivistico, l'analisi spettrografica e la decodifica software di nastri magnetici gravemente deteriorati, parzialmente smagnetizzati o registrati con errori critici di azimut meccanico.

A differenza delle cartucce di emulazione standard (che si collegano alle porte dati logiche o alle uscite preamplificate line-level/earphone dei computer d'epoca), la Cartuccia #13 consente l'**acquisizione diretta a bassissimo rumore direttamente dai capi degli avvolgimenti induttivi della testina magnetica di lettura** (*magnetic tape head*), bypassando completamente l'elettronica analogica originale del registratore (spesso rumorosa, priva di linearità o affetta da condensatori elettrolitici degradati).

---

## 2. Caratteristiche Elettriche e Stadi di Condizionamento

### A. Stadio Preamplificatore Analogico Low-Noise Rail-to-Rail (`U2` - TLV2372)
- **Amplificatore Operazionale**: Doppio operazionale ad alte prestazioni **TLV2372** con ingressi CMOS ad altissima impedenza ($10^{12}\ \Omega$), bassissima corrente di polarizzazione di ingresso ($1\text{ pA}$) e capacità di uscita Rail-to-Rail su alimentazione singola a +5V.
- **Topologia di Guadagno**: Stadio non-invertente a due canali indipendenti (Ch1 Left / Ch2 Right) con guadagno calibrabile ($A_v \approx 20\text{ dB} \dots 34\text{ dB}$) configurato per amplificare i deboli segnali generati dalla testina magnetica (tipicamente nell'ordine di $0.5\text{ mV} \dots 5.0\text{ mV}_{pp}$) al livello di ingresso ottimale degli ADC della scheda madre ($1.0\text{ V} \dots 3.0\text{ V}_{pp}$).
- **Filtro Passa-Basso Anti-Aliasing e Reiezione RF**: Reti RC dedicate sui percorsi di retroazione e d'ingresso per sopprimere l'interferenza a radiofrequenza (RFI), il rumore di commutazione digitale e limitare la banda utile all'intervallo $10\text{ Hz} \dots 48\text{ kHz}$.

### B. Matrice di Accordatura e Terminazione di Impedenza (DIP-Switch `SW1` & `SW2`)
Le testine magnetiche sono trasduttori induttivi la cui risposta in frequenza dipende strettamente dal carico resistivo e capacitivo collegato. La cartuccia incorpora due banchi DIP-switch a 4 vie indipendenti per ciascun canale:
1. **Terminazione Resistiva ($R_{\text{load}}$)**:
   - **47 k$\Omega$** (`R1`, `R2`): Standard industriale IEC/NAB per testine audio a cassetta.
   - **100 k$\Omega$** (`R3`, `R4`): Alta impedenza per carichi minimi su testine ad alta induttanza o per connessione parallela ad alta impedenza a circuiti preesistenti.
2. **Accordo Capacitivo Risonante ($C_{\text{tune}}$)**:
   - **100 pF** (`C5`, `C6`): Compensazione capacitiva standard per cavi schermati corti.
   - **220 pF** (`C7`, `C8`): Sintonia di risonanza in banda alta ($8\text{ kHz} \dots 14\text{ kHz}$) per esaltare le armoniche deboli nei nastri ad alta densità.
   - **320 pF** (combinazione parallela $100\text{ pF} + 220\text{ pF}$): Massima compensazione per testine a bassa impedenza o nastri gravemente attenuati.

### C. Tripla Connettività Fisica Esterna
1. **Morsettiera a Vite 4 Poli (`J2`, Phoenix Passo 3.5 mm)**:
   - Ingresso bilanciato/flottante per connessione a filo diretto alla testina magnetica (CH1+, CH1-, CH2+, CH2-).
   - Ideale per cablaggi diretti a banco su meccaniche di trasporto nastro nude o registratori modificati da laboratorio.
2. **Doppia Presa Jack Stereo 3.5 mm a Basso Profilo (`J3` & `J4`)**:
   - `J3`: Ingresso stereo Ch1/Ch2 sbilanciato schermato (Tip = Ch1, Ring = Ch2, Sleeve = GND) per testine cablate con cavo coassiale stereo.
   - `J4`: Porta di monitoraggio loop-through / uscita analogica bufferizzata o secondo ingresso ausiliario line-level.
3. **Pin-Header Maschio Passo 2.54 mm di Breakout (`J5`, 1x06)**:
   - Accessibilità immediata per sonde di oscilloscopio e multimetro a banco:
     - Pin 1: `GND`
     - Pin 2: `CH1_RAW` (segnale diretto da testina Ch1)
     - Pin 3: `CH1_AMP` (segnale Ch1 amplificato e filtrato)
     - Pin 4: `CH2_RAW` (segnale diretto da testina Ch2)
     - Pin 5: `CH2_AMP` (segnale Ch2 amplificato e filtrato)
     - Pin 6: `+5V` (alimentazione a basso rumore)

### D. Protezioni ESD / TVS e Reiezione Disturbi
- Array di diodi TVS a bassissima capacità parassita **USBLC6-2SC6** (`D1`, `D2`, `D3`) su tutti i pin di ingresso per proteggere gli opamp sensibili da scariche elettrostatiche fino a $\pm 15\text{ kV}$ senza degradare il segnale ad alta frequenza.
- Piani di massa analogici solidi su entrambi i layer (`F.Cu` e `B.Cu`) per schermare la debole corrente indotta dalle testine da disturbi digitali e rumore di switching.

### E. Auto-Identificazione Smart Plug & Play
- **EEPROM I2C 24C02** (`U1`) pre-programmata con descrittore hardware conforme al protocollo Tape Master v2 all'indirizzo standard `0x50`.
- Pin 26 del connettore bus principale `CART_DETECT_N` collegato a massa per il rilevamento istantaneo dell'inserimento scheda.

---

## 3. Centralizzazione Diagnostica sul Front Panel (Daughterboard)

In piena conformità alle regole ufficiali di progetto `tape-master-rules.md`, la cartuccia #13 non monta LED diagnostici ridondanti: l'intero stato del campionamento e dell'alimentazione è centralizzato sull'interfaccia visiva frontale della scheda madre (`Tape_Master_UI_Panel`).

| Riferimento UI | Colore | Serigrafia Standard | Segnale Mappato per Cartuccia #13 | Funzione Operativa |
| :---: | :---: | :---: | :--- | :--- |
| **D2** | Verde | **`PLAY`** | `CH1_AMP` / `AUDIO_RAW_L` | Canale Sinistro (Ch1) attivo e in fase di acquisizione / streaming |
| **D3** | Rosso | **`REC`** | `CH2_AMP` / `AUDIO_RAW_R` | Canale Destro (Ch2) attivo e in fase di acquisizione / streaming |
| **D4** | Giallo | **`MOTOR`** | Linea di abilitazione o sense motore | Segnale di trasporto nastro / presenza portante |
| **D5** | Blu | **`SIGNAL`** | Lock di fase stereo / soglia di trigger | Segnale oltre la soglia di rumore di fondo (carrier detect) |
| **D6** | Verde | **`PWR`** | Alimentazione Tape Master (+5V/+3.3V) | Alimentazione analogica e logica attiva e stabilizzata |
| **D10..D19** | 8V/1G/1R | **`AZIMUTH / VU-METER`** | Differenza di fase o livello picco | **Visualizzazione diretta azimut / correlazione di fase stereo** |

---

## 4. Pinout del Connettore Bus Universale `J1` (2x20 Pin)

| Pin | Nome Net | Funzione Elettrica | Pin | Nome Net | Funzione Elettrica |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **1** | `GND` | Massa di riferimento | **2** | `GND` | Massa di riferimento |
| **3** | `+5V` | Alimentazione analogica +5V | **4** | `+5V` | Alimentazione analogica +5V |
| **5** | `+3.3V` | Alimentazione logica +3.3V | **6** | `+3.3V` | Alimentazione logica +3.3V |
| **7** | `I2C_SCL` | Clock I2C EEPROM Auto-ID | **8** | `I2C_SDA` | Dati I2C EEPROM Auto-ID |
| **9** | `AUDIO_RAW_L` | Uscita amplificata Ch1 (Left) verso ADC | **10** | `AUDIO_RAW_R` | Uscita amplificata Ch2 (Right) verso ADC |
| **11** | `CH1_RAW` | Linea analogica raw non amplificata Ch1 | **12** | `CH2_RAW` | Linea analogica raw non amplificata Ch2 |
| **13..25** | `GND` / `NC` | Linee digitali non utilizzate dal front-end raw | **14..24** | `GND` / `NC` | Linee digitali schermate a massa |
| **26** | `CART_DETECT_N`| Connesso a massa (Rilevamento Cartuccia) | **27..38** | `NC` | Riservati per bus digitale |
| **39** | `GND` | Massa di ritorno | **40** | `GND` | Massa di ritorno |

---

## 5. Elenco Componenti Principali (BOM Sintetica)

| Riferimento | Quantità | Valore / Modello | Package | Funzione |
| :--- | :---: | :--- | :--- | :--- |
| `U1` | 1 | **24C02** (SOIC-8) | SOIC-8 | EEPROM Smart Plug&Play Auto-ID |
| `U2` | 1 | **TLV2372** (SOIC-8) | SOIC-8 | Doppio amplificatore operazionale low-noise rail-to-rail |
| `D1`, `D2`, `D3` | 3 | **USBLC6-2SC6** | SOT-23-6 | Array soppressori TVS ESD ad alta velocità |
| `SW1`, `SW2` | 2 | **SW_DIP_x04** | DIP-8 SMD | Matrice DIP-switch per selezione $R_{\text{load}}$ e $C_{\text{tune}}$ |
| `J1` | 1 | **PinSocket_2x20_P2.54mm_Horizontal** | 2x20 Receptacle 90° | Connettore bus universale Tape Master |
| `J2` | 1 | **TerminalBlock_Phoenix_MPT-0,5-4-2.54** | Morsettiera 4P | Connessione diretta a vite per testine magnetiche |
| `J3`, `J4` | 2 | **Jack_3.5mm_CUI_SJ1-3523N** | SMD 3.5mm Jack | Ingressi/uscite stereo sbilanciati |
| `J5` | 1 | **PinHeader_1x06_P2.54mm_Vertical** | Header 1x06 | Test-point e breakout per oscilloscopio a banco |
| `R1`..`R15` | 15 | Resistenze varie (0805) | SMD 0805 | Reti di polarizzazione, guadagno, terminazione 47k/100k |
| `C1`..`C18` | 18 | Condensatori vari (0805 / 1206) | SMD 0805 / 1206 | Disaccoppiamento, filtri risonanza 100pF/220pF, bypass |

---

## 6. Risultati Ufficiali di Validazione Elettronica KiCad 9

```
======================================================================
KICAD 9.0 CLI VALIDATION REPORT
Progetto: Tape_Master_Cartridge_Raw_Head (Cartridge #13)
======================================================================
1. SCHEMATIC ELECTRICAL RULES CHECK (ERC):
   kicad-cli.exe sch erc Tape_Master_Cartridge_Raw_Head.kicad_sch
   -> Found 0 violations (0 Errors, 0 Warnings).

2. PCB DESIGN RULES CHECK (DRC):
   kicad-cli.exe pcb drc --schematic-parity Tape_Master_Cartridge_Raw_Head.kicad_pcb
   -> Found 0 DRC violations
   -> Found 0 unconnected items
   -> Found 0 schematic parity issues
   -> Found 0 Footprint errors

3. PRODUCTION DELIVERABLES VERIFIED:
   - RS-274X Extended Gerbers & Excellon Drills (in gerbers/)
   - Mechanical 3D Solid Model: Tape_Master_Cartridge_Raw_Head.step
   - Vector PCB Artwork: Top.pdf, Bottom.pdf, Top.svg
   - Vector Schematic Artwork: Tape_Master_Cartridge_Raw_Head_Schematic.pdf, Tape_Master_Cartridge_Raw_Head_Sch.svg
======================================================================
STATUS: PASSED - PRODUCTION READY (REV 2.0)
```
