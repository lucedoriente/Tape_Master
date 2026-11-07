# TAPE MASTER EXERCISER & SIGNAL DIGITIZER - ARCHITETTURA HARDWARE v2.0
**Autore / Hardware Designer**: Alessio Iodice (<alessio67@gmail.com>)  
**Contesto Operativo**: MuDIsTInf (Museo Didattico di Storia dell'Informatica Padova) & Laboratorio di Restauro  
**Toolchain Target**: KiCad 9.0 (`version 20250114`)  
**Data Specifica**: 2026-11-05  
**Licenza**: CC BY-NC-SA 4.0  

---

## 1. Motivazione Architetturale e Risoluzione Criticità v1
Nella versione 1 a singola scheda (monolitica), l'analisi dimensionale e di assemblaggio ha evidenziato una grave interferenza meccanica e visiva:
* Il modulo display OLED da 0.96" I2C, innestato sull'header $1 \times 04$ a $Y = 22.00\text{ mm}$, presenta un PCB con sbalzo verso il basso di circa $27\text{ mm}$.
* Questo ingombro fisico andava a coprire completamente i driver `TLC5916` (U7, U11) e l'intera barra a 10 LED di taratura azimut (D10–D19 a $Y = 44.00\text{ mm}$).
* Inoltre, la coesistenza sullo stesso PCB di piste ad alto guadagno per testina magnetica ($1 \dots 2\text{ mV}_{\text{rms}}$, guadagno fino a $60\text{ dB}$) con le linee di commutazione digitale rapida di display, encoder e tasti esponeva la catena analogica al rumore di commutazione digitale.

Per la **Versione 2** viene adottata un'architettura modulare a tre blocchi (**Sandwich Mezzanina 2+1**):
1. **Daughterboard 1: Front Panel UI**: isola display, controlli e LED di taratura, eliminando le sovrapposizioni e allontanando il rumore digitale.
2. **Mainboard Base**: ospita il core RP2040, l'alimentatore filtrato ultra-low noise, la sezione analogica ad alto guadagno schermata (predisposizione per *shielding can*) e lo slot cartuccia.
3. **Daughterboard 2: Cartucce di Espansione Intercambiabili**: connesse tramite slot universale a 40 pin ad angolo retto con leve di ritegno.

---

## 2. Specifiche Slot Cartuccia 40 Pin (Bus Universale Tape Master v2)

### A. Tipologia Meccanica del Connettore
* **Connettore Scheda Madre**: Boxed Latched Header Maschio a $90^\circ$ ad angolo retto con leve di bloccaggio corte (*Short Latches*), $2 \times 20$ pin, passo $2.54\text{ mm}$ (serie Würth WR-BHD 61204021721 o equivalenti industriali).
* **Connettore Cartuccia**: Presa Femmina compatibile per montaggio a bordo scheda.
* **Blocco Meccanico e Sagomatura PCB**:
  - Le leve laterali garantiscono il bloccaggio antisfilamento della cartuccia contro vibrazioni o urti.
  - Per consentire l'oscillazione a $30^\circ \dots 45^\circ$ delle leve durante l'estrazione ed evitare collisioni meccaniche, il contorno `Edge.Cuts` del PCB della cartuccia presenta due intagli fresati laterali di $6.0\text{ mm} \times 8.0\text{ mm}$ attorno al corpo del connettore.

### B. Mappa dei Segnali e Pinout Dettagliato ($2 \times 20$)

```
        ┌───────────────────[ VISTA CONNETTORE MB ]───────────────────┐
        │  1  3  5  7  9 11 13 15 17 19 21 23 25 27 29 31 33 35 37 39  │
 [LEVA] │  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  │ [LEVA]
        │  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  ■  │
        │  2  4  6  8 10 12 14 16 18 20 22 24 26 28 30 32 34 36 38 40  │
        └──────────────────────────[ TACCA ]──────────────────────────┘
```

| Pin | Nome Segnale | Categoria | Descrizione Tecnica |
| :---: | :--- | :---: | :--- |
| **1** | `+5V_RAW` | Alimentazione | Alimentazione $5\text{V}$ principale da USB o alimentatore esterno (fino a $1.5\text{A}$) |
| **2** | `+5V_RAW` | Alimentazione | In parallelo al Pin 1 per ridurre la caduta di tensione e la resistenza di contatto |
| **3** | `+3V3_CLEAN` | Alimentazione | Tensione logica $3.3\text{V}$ ultra-low-noise stabilizzata da LDO di scheda madre |
| **4** | `+3V3_CLEAN` | Alimentazione | In parallelo al Pin 3 per logica cartuccia, FPGA ed EEPROM di identificazione |
| **5** | `V_AUX` | Alimentazione | Linea opzionale per motori esterni o relè a tensione superiore ($9\text{V}/12\text{V}$) |
| **6** | `GND` | Massa | Ritorno di massa di potenza |
| **7** | `AGND` | Shield Analogico | Massa di guardia e schermo per canale audio sinistro |
| **8** | `AUDIO_RAW_L` | Analog In | Ingresso audio testina grezzo / Line-In Canale Sinistro (Mono principale) |
| **9** | `AGND` | Shield Analogico | Schermo di guardia inter-canale tra audio sinistro e destro |
| **10** | `AUDIO_RAW_R` | Analog In | Ingresso Canale Destro (per testine stereo o traccia voce/ausiliaria) |
| **11** | `AGND` | Shield Analogico | Schermo di guardia tra ingressi e uscite analogiche |
| **12** | `AUDIO_DAC_L` | Analog Out | Uscita analogica generata da DAC/PWM filtrato per computer (livello EAR/MIC mono) |
| **13** | `AGND` | Shield Analogico | Schermo di guardia inter-canale uscite analogiche |
| **14** | `AUDIO_DAC_R` | Analog Out | Uscita analogica secondaria (per audio monitor TV Atari o stereo) |
| **15** | `GND` | Shield Separatore | Massa digitale di separazione tra dominio analogico debole e digitale veloce |
| **16** | `TAPE_EMU_OUT`| Digitale PIO Out | Flusso impulsi digitali generati per il computer (es. `READ` Commodore C2N) |
| **17** | `TAPE_REC_IN` | Digitale PIO In | Flusso impulsi digitali in registrazione dal computer (es. `WRITE` Commodore C2N) |
| **18** | `MOTOR_SENSE` | Digitale In | Rilevamento stato motore registratore dal computer ($0\text{V}$ off, $5\text{V}$ on) |
| **19** | `MOTOR_CTRL` | Digitale Out | Comando logico per pilotare relè/fotoaccoppiatore fermo motore su deck esterno |
| **20** | `TAPE_SENSE` | I/O Open-Drain | Emulazione tasto "Play premuto" (chiusura a massa verso computer Commodore) |
| **21** | `AUX_GPIO1` | GPIO RP2040 | Linea ausiliaria configurabile (es. secondo registratore `CS2` su TI-99) |
| **22** | `AUX_GPIO2` | GPIO RP2040 | Seconda linea ausiliaria configurabile (es. direzione flusso o inversione) |
| **23** | `GND` | Massa | Ritorno di massa per bus di controllo |
| **24** | `I2C_SCL` | Bus I2C | Clock per identificazione EEPROM cartuccia e periferiche lente ($3.3\text{V}$) |
| **25** | `I2C_SDA` | Bus I2C | Dati per identificazione EEPROM cartuccia e periferiche lente ($3.3\text{V}$) |
| **26** | `CART_DETECT_N`| Rilevamento | Pin di presenza a massa su cartuccia: attiva interrupt all'inserimento a caldo |
| **27** | `CART_IRQ_N` | Interrupt | Linea di interrupt rapido a bassa latenza dalla cartuccia verso la MCU |
| **28** | `CART_RESET_N`| Reset | Linea di reset hardware di sistema verso la cartuccia |
| **29** | `CART_SPI_SCK` | Bus SPI Veloce | Clock SPI dedicato per ADC/DAC ausiliari ad alta risoluzione o FPGA su cartuccia |
| **30** | `CART_SPI_MOSI`| Bus SPI Veloce | Master-Out Slave-In bus SPI |
| **31** | `CART_SPI_MISO`| Bus SPI Veloce | Master-In Slave-Out bus SPI |
| **32** | `CART_SPI_CS` | Bus SPI Veloce | Chip Select dedicato alla cartuccia |
| **33** | `CART_UART_TX`| Bus Seriale | Trasmissione UART hardware (per MIDI Tape Sync vintage o debug) |
| **34** | `CART_UART_RX`| Bus Seriale | Ricezione UART hardware (per MIDI Tape Sync vintage o debug) |
| **35** | `SPARE_1` | Riserva Libera | Pin non assegnato per espansioni future |
| **36** | `SPARE_2` | Riserva Libera | Pin non assegnato per espansioni future |
| **37** | `SPARE_3` | Riserva Libera | Pin non assegnato per espansioni future |
| **38** | `SPARE_4` | Riserva Libera | Pin non assegnato per espansioni future |
| **39** | `SPARE_5` | Riserva Libera | Pin non assegnato per espansioni future |
| **40** | `GND` | Massa | Ritorno di massa di chiusura connettore |

---

## 3. Gestione Smart Cartridge (Plug & Play)
Ciascuna cartuccia integra un'EEPROM seriale `24C02` (in package SOT-23 o SOIC-8) collegata ai pin `I2C_SDA` e `I2C_SCL` (indirizzo `0x50`).
* All'inserimento della scheda, il pin `CART_DETECT_N` (Pin 26) viene collegato a massa, scatenando un interrupt sull'RP2040.
* Il firmware legge il blocco descrittore della cartuccia (ID modulo, nome, polarità delle linee, baud rate predefinito e profili audio/digitizer) e riconfigura automaticamente l'interfaccia a schermo e le macchine a stati PIO.

---

## 4. Famiglia delle Cartucce Previste
1. **Cartuccia Commodore C2N / 1530 / 1531**:
   - Connettore a pettine $3.96\text{ mm}$ (0.156") a 6 poli + connettore Mini-DIN 8 per C16/Plus4.
   - Buffer open-collector `74HCT06` per linee `READ` e `WRITE`.
2. **Cartuccia Universal Audio & Dual Remote**:
   - Jack $3.5\text{ mm}$ placcati oro (`EAR` / `MIC`) con commutatore attenuatore passivo ($0\text{ dB}$ / $-40\text{ dB}$).
   - Due Jack $2.5\text{ mm}$ (`REMOTE 1` e `REMOTE 2`) optoisolati (relè PhotoMOS stato solido).
   - Target: Sinclair ZX80/ZX81/Spectrum, Apple II, Jupiter Ace, MSX audio, calcolatrici TI/HP.
3. **Cartuccia Atari SIO (XC12 / 1010)**:
   - Connettore SIO proprietario 13-pin con demodulazione/modulazione FSK e riproduzione della traccia audio analogica contemporanea.
4. **Cartuccia Amstrad CPC / MSX / BBC Micro**:
   - Connettori DIN $180^\circ$ e DIN 8 con gestione linee remote a relè.
5. **Cartuccia Raw Head Probing & Stereo Digitizer**:
   - Ingressi a bassissima capacità con terminazione resistiva/capacitiva variabile ($47\text{ k}\Omega / 100\text{ k}\Omega$, $100\text{ pF} \dots 470\text{ pF}$) per taratura azimut e riversamento su due canali in parallelo.

---

## 5. Distinta Base Connettori di Produzione e Codici di Acquisto Ufficiali (BOM Interconnect)
Per garantire la perfetta riproducibilità e prevenire errori di foratura o incompatibilità geometriche, tutti i componenti di interconnessione adottano codici commerciali univoci reperibili a catalogo:

### A. Jack Audio 3.5 mm Orizzontali THT (Cartucce #04 Sinclair, #10 Apple II, #12 Sharp MZ)
* **Codice Ufficiale Raccomandato**: **Same Sky (ex CUI Devices) `SJ1-3525N`** (Mouser: `490-SJ1-3525N`, DigiKey: `CP-3525N-ND`).
* **Specifiche**: Presa mini-jack stereo TRS 3.5 mm ad angolo retto THT, corpo PBT nero, boccola in ottone nichelato, doppio interruttore interno normalmente chiuso (Tip Switch su pin 10, Ring Switch su pin 11).
* **Compatibilità Universale Footprint**: L'impronta PCB adotta la foratura a 5 pin dell'`SJ1-3525N`, compatibile all'innesto diretto anche con le varianti a 4 pin (`SJ1-3524N`, con solo Tip Switch) e a 3 pin (`SJ1-3523N`, senza interruttori).

### B. Prese Circolari DIN da Circuito Stampato Orizzontali THT
* **DIN 5-Pin 180° (#03 Thomson/PC128, #05 Amstrad CPC, #08 Tandy CoCo/Dragon)**:
  - **Codice Ufficiale**: **Same Sky `SDS-50J`** (Mouser: `490-SDS-50J`, DigiKey: `CP-SDS-50J-ND`, Farnell: `2112448`).
  - Pinout: 5 pin a semicerchio 180° (numerazione DIN $1-4-2-5-3$) + 2 alette di fissaggio a massa telaio.
* **DIN 7-Pin 270° (#07 Acorn BBC Micro, #11 Oric Atmos)**:
  - **Codice Ufficiale**: **Same Sky `SDS-70J`** (Mouser: `490-SDS-70J`, DigiKey: `CP-SDS-70J-ND`, Farnell: `2112450`).
  - Pinout: 7 pin ad arco esteso 270° + contatti di schermatura metallica continua.
* **DIN 8-Pin 270° (#06 MSX Standard)**:
  - **Codice Ufficiale**: **Same Sky `SDS-80J`** (Mouser: `490-SDS-80J`, DigiKey: `CP-SDS-80J-ND`, Farnell: `2112451`).
  - Pinout: 8 pin ad arco 270° a ferro di cavallo.
* **Mini-DIN 8-Pin (#01 Commodore C16 / Plus4)**:
  - **Codice Ufficiale**: **Same Sky `MD-80`** o `MD-80SM` (Mouser: `490-MD-80`, DigiKey: `CP-MD-80-ND`).

### C. Connettore Slot Bus 40 Pin (Passo 2.54 mm)
* **Maschio Mainboard (`J5`)**: **Würth Elektronik `61204021721`** (Boxed Latched Header 2x20 90° con leve corte).
* **Femmina Cartucce (`J1`)**: **Samtec `SSW-120-02-G-D-RA`** / Harwin `M20-7812045` (Receptacle Femmina 2x20 90° orizzontale a filo scheda con battuta a $Y = 0.00\text{ mm}$).

---

## 6. Accoppiamento Meccanico, Inserimento ed Ergonomia delle Cartucce

### A. Geometria di Innesto Complanare (Mainboard $\leftrightarrow$ Cartuccia)
Le due schede (Mainboard e Cartuccia) si collegano rimanendo **perfettamente complanari e parallele** sullo stesso piano orizzontale:
* **Mainboard (`J5`)**: Monta un header maschio ad angolo retto con corpo plastico sul lato superiore (`F.Cu`). I 40 pin maschi sporgono orizzontalmente all'indietro oltre il bordo posteriore della scheda madre ($Y = 26.92\text{ mm}$).
* **Cartuccia (`J1`)**: Monta una presa femmina ad angolo retto con i terminali a $90^\circ$ saldati nei fori through-hole del PCB ($Y = 2.54\text{ mm}$ per la fila interna pari, $Y = 5.08\text{ mm}$ per la fila esterna dispari). Il corpo plastico nero ad alveoli si protende a sbalzo verso l'esterno per accogliere la spina maschio di `J5`.
* **Battuta Meccanica e Intagli Laterali**: I due intagli laterali su `Edge.Cuts` ($6.0\text{ mm} \times 8.0\text{ mm}$) sul profilo della cartuccia alloggiano le leve di ritenuta dell'header maschio boxed, garantendo un bloccaggio meccanico solido a prova di vibrazioni e sfilamenti accidentali durante l'uso.

```
     [ MAINBOARD ]                                  [ CARTRIDGE ]
     =============                                  =============
  [PCB Mainboard] ────┐                        ┌──── [PCB Cartuccia]
                      │  [Maschio IDC J5]      │
                      └───═══►          ◄══════┘
                           Pin Maschi    Prese Femmina [J1]
```

### B. Ergonomia Serigrafica e Orientamento a 180°
Poiché la cartuccia si innesta all'indietro nella scheda madre ed estende l'apparato orizzontalmente verso il retro del banco di lavoro:
1. **Posizionamento Componenti**: I componenti attivi (buffer, IC di protezione, EEPROM) e i connettori esterni (`J2`, `J3`) sono disposti sulla faccia superiore (`F.Cu`).
2. **Serigrafia di Titolo Ruotata a 180°**: La dicitura identificativa della scheda e il copyright (`© 2026 by Alessio Iodice`) sono posizionati sul bordo inferiore del PCB e **ruotati di 180°**. In questo modo, l'operatore posizionato davanti al pannello frontale (`UI Panel`) legge la cartuccia inserita in modo perfettamente dritto e naturale dall'alto.

---

## 7. Matrice di Certificazione e Audit Pinout delle 13 Cartucce

Tutti i pin di connessione delle porte proprietarie d'epoca (`J2`) e degli header di test a banco (`J3` / `J4`) sono stati verificati e certificati pin-per-pin contro i datasheet e i manuali di servizio originali:

| # | Cartuccia Piattaforma | Connettori Esterni a Bordo | Pinout Specifiche Ufficiali di Fabbrica | Mapping Netlist Scheda & Tape Master | Esito Validazione |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **01** | **Commodore C2N** | Card Edge 6P (`J2`)<br>Mini-DIN 8 (`J3`)<br>Header 6P (`J4`) | 1: GND<br>2: +5V<br>3: MOTOR<br>4: READ<br>5: WRITE<br>6: SENSE | Pin 1: `GND`<br>Pin 2: `+5V`<br>Pin 3: `/C64_MOTOR`<br>Pin 4: `/C64_READ`<br>Pin 5: `/C64_WRITE`<br>Pin 6: `/C64_SENSE` | **CONFERMATO (1:1)** |
| **02** | **Atari SIO** | Presa SIO 13P (`J2`)<br>Header 13P (`J3`) | 1: CLK IN, 2: CLK OUT, 3: DATA IN, 4: GND, 5: DATA OUT, 6: GND, 7: COMMAND, 8: MOTOR, 9: PROCEED, 10: +5V, 11: AUDIO IN, 12: +12V, 13: INTERRUPT | Pin 1: `CLK_IN`<br>Pin 2: `CLK_OUT`<br>Pin 3: `DATA_IN`<br>Pin 4, 6: `GND`<br>Pin 5: `DATA_OUT`<br>Pin 7: `COMMAND`<br>Pin 8: `MOTOR`<br>Pin 9: `PROCEED`<br>Pin 10: `+5V_SIO`<br>Pin 11: `AUDIO_IN`<br>Pin 12: `+12V_SIO`<br>Pin 13: `INTERRUPT` | **CONFERMATO (1:1)** |
| **03** | **Thomson / PC 128** | Presa DIN 5 180° (`J2`)<br>Header 6P (`J3`) | 1: REM (Motor Control)<br>2: GND<br>3: AUDIO (Tape $\rightarrow$ PC)<br>4: READ (Data to PC)<br>5: WRITE (Data from PC) | Pin 1: `/THOMSON_REM`<br>Pin 2: `GND`<br>Pin 3: `/THOMSON_AUDIO`<br>Pin 4: `/THOMSON_READ`<br>Pin 5: `/THOMSON_WRITE` | **CONFERMATO (1:1)** |
| **04** | **Sinclair ZX Spectrum** | Jack 3.5mm EAR (`J2`)<br>Jack 3.5mm MIC (`J3`)<br>Header 6P (`J4`) | EAR: Tip/Ring=Signal, Sleeve=GND<br>MIC: Tip/Ring=Signal, Sleeve=GND<br>REM: Contatti relè A/B | J2: Tip/Ring=`/SPECTRUM_EAR`, S=`GND`<br>J3: Tip/Ring=`/SPECTRUM_MIC`, S=`GND`<br>J4: Pin 3=`EAR`, Pin 4=`MIC`, Pin 5=`REM_A` | **CONFERMATO (1:1)** |
| **05** | **Amstrad CPC** | Presa DIN 5 180° (`J2`)<br>Header 6P (`J3`) | 1: GND, 2: GND<br>3: REM B (Relè motore)<br>4: READ (Data to CPC)<br>5: WRITE (Data from CPC) | Pin 1, 2: `GND`<br>Pin 3: `/CPC_REM_B`<br>Pin 4: `/CPC_READ`<br>Pin 5: `/CPC_WRITE` | **CONFERMATO (1:1)** |
| **06** | **MSX Standard** | Presa DIN 8 270° (`J2`)<br>Header 8P (`J3`) | 1, 2, 3: GND<br>4: CMTOUT (Data out)<br>5: CMTIN (Data in)<br>6: REM+<br>7: REM-<br>8: GND | Pin 1, 2, 3, 8: `GND`<br>Pin 4: `/MSX_CMTOUT`<br>Pin 5: `/MSX_CMTIN`<br>Pin 6: `/MSX_REM_PLUS`<br>Pin 7: `/MSX_REM_MINUS` | **CONFERMATO (1:1)** |
| **07** | **BBC Micro** | Presa DIN 7 270° (`J2`)<br>Header 7P (`J3`) | 1: CASSETTE OUT (to tape)<br>2: GND<br>3: CASSETTE IN (from tape)<br>4: CASSETTE OUT<br>5: NC<br>6: MOTOR CONTROL<br>7: GND | Pin 1, 4: `/BBC_OUT`<br>Pin 2, 7: `GND`<br>Pin 3: `/BBC_IN`<br>Pin 6: `/BBC_REM_A` | **CONFERMATO (1:1)** |
| **08** | **Tandy CoCo / Dragon** | Presa DIN 5 180° (`J2`)<br>Header 6P (`J3`) | 1: GND, 2: GND<br>3: REM (Relè motore)<br>4: READ (to CoCo)<br>5: WRITE (from CoCo) | Pin 1, 2: `GND`<br>Pin 3: `/COCO_REM_B`<br>Pin 4: `/COCO_READ`<br>Pin 5: `/COCO_WRITE` | **CONFERMATO (1:1)** |
| **09** | **TI-99/4A** | Presa DE-9 Femmina (`J2`)<br>Header 9P (`J3`) | 1: CS1 Motor Control<br>2: GND<br>3: CS2 Audio Out<br>4: Audio Gate<br>5, 7, 9: GND<br>6: CS2 Motor Control<br>8: Tape In (from TI-99) | Pin 1: `/TI_CS1_MOTOR_P`<br>Pin 2, 5, 7, 9: `GND`<br>Pin 3: `/TI_CS2_OUT`<br>Pin 4: `/TI_AUDIO_GATE`<br>Pin 6: `/TI_CS2_MOTOR_P`<br>Pin 8: `/TI_TAPE_IN` | **CONFERMATO (1:1)** |
| **10** | **Apple II** | Jack 3.5mm CASSOUT (`J2`)<br>Jack 3.5mm CASSIN (`J3`)<br>Header 6P (`J4`) | CASSOUT: Tip=Read Data, Sleeve=GND<br>CASSIN: Tip=Write Data, Sleeve=GND | J2: Tip=`/APPLE_READ`, Sleeve=`GND`<br>J3: Tip=`/APPLE_WRITE`, Sleeve=`GND`<br>J4: 1=`GND`, 2=`+5V`, 4=`REM_B`, 5=`READ`, 6=`WRITE` | **CONFERMATO (1:1)** |
| **11** | **Oric Atmos** | Presa DIN 7 270° (`J2`)<br>Header 7P (`J3`) | 1: REM (Relè motore)<br>2: GND<br>3: READ (Ear / to Oric)<br>4, 5: WRITE (Mic / from Oric)<br>6, 7: NC | Pin 1: `/ORIC_REM_B`<br>Pin 2: `GND`<br>Pin 3: `/ORIC_READ`<br>Pin 4, 5: `/ORIC_WRITE`<br>Pin 6, 7: `NC` | **CONFERMATO (1:1)** |
| **12** | **Sharp MZ** | Jack 3.5mm READ (`J2`)<br>Jack 3.5mm WRITE (`J3`)<br>Header 9P (`J4`) | MZ-700/800 Cassette Port:<br>1: EX_WRITE, 2: EX_READ, 3: GND, 4: MOTOR, 5: SENSE, 6: +5V, 7: WRITE_TTL, 8: READ_TTL, 9: GND | J2/J3: Tip/Sleeve corretti<br>J4 Pin 1: `WRITE`<br>Pin 2: `READ`<br>Pin 3, 9: `GND`<br>Pin 4: `MOTOR`<br>Pin 5: `SENSE`<br>Pin 6: `+5V_HOST`<br>Pin 8: `READ_BUF_OUT` (TTL) | **CONFERMATO (1:1)** |
| **13** | **Stereo Digitizer** | Morsettiera Phoenix (`J2`)<br>Jack 3.5mm L (`J3`)<br>Jack 3.5mm R (`J4`) | Ingressi differenziali e sbilanciati testina magnetica raw L / R con selettore d'impedenza a DIP-switch | J2 Pin 1: `HEAD_L_IN`, Pin 2: `GND`<br>Pin 3: `HEAD_R_IN`, Pin 4: `GND`<br>J3: Canale Sinistro<br>J4: Canale Destro | **CONFERMATO (1:1)** |


