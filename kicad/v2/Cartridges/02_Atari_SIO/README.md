# Tape Master v2 — Cartuccia 02: Atari 8-Bit SIO Tape Interface

| Proprietà | Dettaglio / Valore |
| :--- | :--- |
| **Progetto** | Tape Master Exerciser & Signal Digitizer v2 |
| **Modulo** | Cartuccia Espansione #02 — Atari SIO (`02_Atari_SIO`) |
| **Piattaforme Compatibili** | Atari 400, 800, 800XL, 65XE, 130XE, XEGS, XE Game System |
| **Periferiche Supportate** | Atari 410, 1010, XC11, XC12, CA-12, XCA12, XC13, registratori compatibili Turbo (KSO, Silesia, Turbo 2000) |
| **Autore & Hardware Designer** | Alessio Iodice (`alessio67@gmail.com`) |
| **Data di Rilascio** | 2026-11-06 |
| **Revisione** | 2.0 (KiCad 9.0 Nativo) |
| **Licenza** | CC BY-NC-SA 4.0 |
| **Stato Validazione KiCad 9** | **0 Violazioni ERC / 0 Violazioni DRC / 0 Net Non Connesse / 0 Parity Issues** |

---

## 1. Descrizione Architetturale

La cartuccia **Cartuccia 02: Atari SIO** interfaccia il sistema **Tape Master v2** al bus seriale proprietario **Atari SIO (Serial Input/Output)** a 13 pin, utilizzato dall'intera famiglia di personal computer a 8-bit Atari (400, 800, serie XL, serie XE) per il pilotaggio dei registratori a cassette (modelli 410, 1010, XC11, XC12 e derivati con turbo tape).

### Caratteristiche Elettriche Chiave
1. **Trasmissione Dati Asincrona SIO (DATA IN - Pin 3)**:
   - La linea `DATA IN` dell'Atari opera a 600 baud (standard Atari FSK audio demodulato) o a bitrate superiori (sistemi Turbo fino a $4800\text{ baud}$).
   - Pilotata tramite doppio stadio invertitore Open-Collector ad alta velocità **74HCT06** (`U2`), con resistenza di pull-up locale da $1\text{ k}\Omega$ verso `+5V_SIO` (host console) e resistenza di pull-up da $10\text{ k}\Omega$ sull'ingresso logico collegato alla Mainboard.
2. **Ricezione Dati (DATA OUT - Pin 5)**:
   - Traslazione di livello da 5V a 3.0V tramite partitore resistivo di precisione ($R_1 = 2.2\text{ k}\Omega$, $R_2 = 3.3\text{ k}\Omega$) con clamp a doppio diodo Schottky a commutazione ultra-rapida **BAT54S** (`D2`) verso `+3.3V` e `GND`, proteggendo l'ingresso MCU `TAPE_REC_IN`.
3. **Controllo & Rilevamento Motore (MOTOR - Pin 8)**:
   - L'Atari attiva il motore tirando la linea a livello logico basso / massa (transistor open-collector sul computer).
   - Resistenza di pull-up da $10\text{ k}\Omega$ (`R3`) verso `+5V_SIO`, partitore $2.2\text{ k}\Omega / 3.3\text{ k}\Omega$ (`R4`, `R5`) e clamp Schottky **BAT54S** (`D4`) verso la linea `MOTOR_SENSE` della scheda madre.
4. **Acquisizione Audio / Traccia Stereo Ingest (AUDIO IN - Pin 11)**:
   - Il bus SIO prevede sul Pin 11 una traccia audio ausiliaria (usata nei nastri didattici Atari per audio parlato o musica mentre la traccia dati viene caricata in RAM).
   - Circuito di condizionamento dedicato con condensatore di disaccoppiamento DC da $4.7\ \mu\text{F}$ (`C3`), filtro passa-basso RC passivo ($R_6 = 1\text{ k}\Omega$, $C_4 = 10\text{ nF}$, frequenza di taglio $f_c \approx 15.9\text{ kHz}$) e resistenza di carico shunt da $10\text{ k}\Omega$ (`R7`), inviata alla linea `AUDIO_RAW_L` per il campionamento ADC / digitalizzazione stereo.
5. **Protezione ESD / Transitori**:
   - Array di soppressione TVS a bassa capacità parassita **USBLC6-2SC6** (`D1`) su tutte e 4 le linee esposte (`SIO_DATA_IN`, `SIO_DATA_OUT`, `SIO_MOTOR`, `SIO_AUDIO_IN`).
6. **Smart Plug & Play (Auto-ID Cartridge)**:
   - EEPROM I2C **24C02** (`U1`) configurata all'indirizzo `0x51` (`A0=1, A1=0, A2=0`), contenente il descrittore hardware con magic byte, revisione, pinout e parametri di campionamento.
   - Pin 26 del connettore bus principale `CART_DETECT_N` collegato a massa per rilevamento hardware automatico dell'inserimento scheda.
7. **Monitor Alimentazione Atari Console**:
   - Micro-LED verde 0805 `D3` (`+5V_SIO_OK`) con resistenza di zavorra da $1.5\text{ k}\Omega$ (`R10`), unico LED ammesso sulla cartuccia come da regole di progetto per visualizzare a colpo d'occhio la presenza dell'alimentazione erogata dalla console vintage.

---

## 2. Centralizzazione Diagnostica sul Front Panel (Daughterboard)

Come prescritto dalle regole ufficiali di progetto `tape-master-rules.md`, l'intera interfaccia diagnostica e di stato per l'operatore è centralizzata sul pannello frontale (`Tape_Master_UI_Panel`), evitando LED duplicati non visibili a banco.

I 5 LED diagnostici standardizzati sul pannello operatore riflettono il funzionamento della cartuccia Atari SIO:

| Riferimento UI | Colore | Serigrafia Standard | Segnale Mappato per Atari SIO | Funzione Operativa |
| :---: | :---: | :---: | :--- | :--- |
| **D2** | Verde | **`PLAY`** | `SIO_DATA_IN` (Pin 3) | Trasmissione dati dal Tape Master verso la console Atari (emulazione nastro CAS / dump) |
| **D3** | Rosso | **`REC`** | `SIO_DATA_OUT` (Pin 5) | Ricezione dati e salvataggio dump dal computer Atari verso il Tape Master |
| **D4** | Giallo | **`MOTOR`** | `SIO_MOTOR` (Pin 8) | Linea motore abilitata dall'Atari (computer in attesa di caricamento o salvataggio) |
| **D5** | Blu | **`SIGNAL`** | `SIO_AUDIO_IN` (Pin 11) | Presenza traccia audio analogica / sincronismo portante SIO / turbo pulse |
| **D6** | Verde | **`PWR`** | Alimentazione Tape Master | Alimentazione principale di sistema attiva e MCU operativo |
| **D10..D19** | 8V/1G/1R | **`AZIMUTH / VU-METER`** | Livello di picco ADC `AUDIO_RAW_L` | Barra VU-meter per regolazione azimut / livello volume traccia parlato |

---

## 3. Doppia Connettività Esterna

La cartuccia adotta la configurazione a **doppia porta**:
1. **`J2` — Presa Femmina Proprietaria Atari SIO 13-Pin**: Connettore a guscio originale per l'inserimento diretto del cavo SIO standard proveniente dal computer o dal registratore.
2. **`J3` — Pin-Header Maschio Breakout 1x13 passo 2.54 mm**: Pin header montato a bordo scheda con serigrafia esplicita di ciascun pin, ideale per test a banco, oscilloscopio, analizzatore logico o cablaggi rapidi.

### Piedinatura Connettori SIO (`J2` e `J3`)

| Pin # | Segnale SIO | Connessione su Cartuccia | Direzione | Descrizione |
| :---: | :--- | :--- | :---: | :--- |
| **1** | `CLK_I` (Clock In) | Header Breakout `J3` / `J2` | Ingresso Atari | Segnale di clock esterno per periferiche sincrone |
| **2** | `CLK_O` (Clock Out) | Header Breakout `J3` / `J2` | Uscita Atari | Clock generato dalla CPU/POKEY |
| **3** | `DATA_IN` | Buffer Open-Collector `74HCT06` | Ingresso Atari | Ricezione seriale dati dal registratore (600+ baud) |
| **4** | `GND` | Piano di Massa Scheda (`GND`) | Riferimento | Massa logica e potenza |
| **5** | `DATA_OUT` | Partitore $2.2\text{k}/3.3\text{k}$ $\rightarrow$ `TAPE_REC_IN` | Uscita Atari | Dati seriali trasmessi dalla console verso la cassetta |
| **6** | `GND` | Piano di Massa Scheda (`GND`) | Riferimento | Massa logica e potenza |
| **7** | `COMMAND` | Pull-up $10\text{ k}\Omega$ $\rightarrow$ Header Breakout `J3` | Uscita Atari | Linea di comando attiva bassa (abilitazione bus per disk drive) |
| **8** | `MOTOR` | Pull-up + Partitore $\rightarrow$ `MOTOR_SENSE` | Uscita Atari | Controllo motore registratore (attivo a 0V) |
| **9** | `PROCEED` | Header Breakout `J3` / `J2` | Ingresso Atari | Linea di interrupt / handshake periferiche |
| **10** | `+5V_SIO` | Monitor LED `D3` & Pull-up buffer | Uscita Atari | Tensione +5V erogata dall'Atari (max $100\text{ mA}$) |
| **11** | `AUDIO_IN` | Filtro passa-basso $15.9\text{ kHz}$ $\rightarrow$ `AUDIO_RAW_L` | Ingresso Atari | Traccia audio analogica ausiliaria cassetta |
| **12** | `+12V` | Header Breakout `J3` / `J2` | Non connesso | Presente solo su Atari 400/800 per alimentatori d'epoca |
| **13** | `INTERRUPT` | Header Breakout `J3` / `J2` | Ingresso Atari | Linea di richiesta interruzione al computer |

---

## 4. Specifiche Meccaniche e Bordo Scheda

- **Dimensioni**: $74.00\text{ mm} \times 55.00\text{ mm}$.
- **Intagli Meccanici**: Due intagli su `Edge.Cuts` ($6.0\text{ mm} \times 8.0\text{ mm}$) per l'alloggiamento delle leve di ritenuta del connettore `J1` della Mainboard.
- **Complanarità**: Connettore maschio ad angolo retto sulla Mainboard e connettore femmina ad angolo retto sulla Cartuccia (`J1`) permettono alle due schede di rimanere **perfettamente parallele e complanari**, con la cartuccia che estende orizzontalmente all'indietro il corpo principale del Tape Master.

---

## 5. File di Rilascio e Produzione

- Schema Elettrico KiCad: `Tape_Master_Cartridge_Atari_SIO.kicad_sch`
- Layout PCB KiCad: `Tape_Master_Cartridge_Atari_SIO.kicad_pcb`
- Modello 3D Meccanico Solido PCB Assemblato: `Tape_Master_Cartridge_Atari_SIO.step`
- Schema Elettrico Vettoriale: `Tape_Master_Cartridge_Atari_SIO.pdf` e `Tape_Master_Cartridge_Atari_SIO_Sch.svg`
- Disegno PCB Top Layer: `Tape_Master_Cartridge_Atari_SIO_Top.pdf` e `Tape_Master_Cartridge_Atari_SIO_Top.svg`
- Disegno PCB Bottom Layer: `Tape_Master_Cartridge_Atari_SIO_Bottom.pdf`
- Report Collaudo ERC: `Tape_Master_Cartridge_Atari_SIO-erc.rpt` (0 errori, 0 warning)
- Report Collaudo DRC: `Tape_Master_Cartridge_Atari_SIO-drc.rpt` (0 errori, 0 warning, 0 unconnected, 0 parity issues)
