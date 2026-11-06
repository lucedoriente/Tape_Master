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
