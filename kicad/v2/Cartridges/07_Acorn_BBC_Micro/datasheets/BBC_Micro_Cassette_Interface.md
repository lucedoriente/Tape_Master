# Specifiche Tecniche Interfaccia Cassetta Acorn BBC Micro & Electron
**Autore / Hardware Designer**: Alessio Iodice (<alessio67@gmail.com>)  
**Contesto Operativo**: Tape Master Exerciser & Signal Digitizer v2 — Cartuccia #07  
**Toolchain Target**: KiCad 9.0 (`version 20250114`)  
**Licenza**: CC BY-NC-SA 4.0  

---

## 1. Panoramica dello Standard Acorn Cassette
L'architettura dei computer ad 8-bit Acorn Computers Ltd (BBC Micro Model A, Model B, B+ 64/128, Master 128 e Acorn Electron) adotta per il registratore a cassette un'interfaccia standardizzata su connettore femmina **DIN 7-Pin 270°** (standard industriale DIN 45329 / IEC 60130-9, connettore serie CUI / Same Sky SDS-70J).

Tale interfaccia gestisce:
1. **Canale Audio di Registrazione (Save/Mic)** dal computer verso il registratore (Pin 1 e Pin 4);
2. **Canale Audio di Riproduzione (Load/Ear)** dal registratore verso il computer (Pin 3);
3. **Massa di Riferimento Audio e Digitale** (Pin 2);
4. **Controllo Motore Hardware a Relè Elettromeccanico** (Pin 6 e Pin 7), pilotabile da sistema operativo tramite i comandi `*MOTOR 1` (chiusura) e `*MOTOR 0` (apertura).

---

## 2. Pinout Ufficiale Connettore DIN 7-Pin 270° (BBC Micro / Electron Cassette Port)

```text
       Presa Femmina sul Computer / Cartuccia       Connettore Maschio sul Cavo
                      __ 6   7 __                           __ 7   6 __
                    /             \                       /             \
                   /  4         5  \                     /  5         4  \
                  |   1    2    3   |                   |   3    2    1   |
                   \     \   /     /                     \     \   /     /
                    \      V      /                       \      V      /
                      -----------                           -----------
```

| Pin DIN 7 | Nome Segnale Acorn | Direzione (BBC $\leftrightarrow$ Tape) | Descrizione Tecnica e Livelli Elettrici |
| :---: | :--- | :---: | :--- |
| **1** | `CASSETTE_OUT` | Computer $\rightarrow$ Tape | Uscita audio/dati da registrare su cassetta (collegata a `MIC` registratore). Livello $200\text{ mV}_{\text{pp}} \dots 1\text{ V}_{\text{pp}}$ AC generato dal sintetizzatore ULA / ACIA |
| **2** | `GND` | — | Massa comune di segnale e ritorno alimentazione |
| **3** | `CASSETTE_IN` | Tape $\rightarrow$ Computer | Ingresso audio/dati letto da nastro (collegato a `EAR` registratore). Livello $200\text{ mV}_{\text{pp}} \dots 2.5\text{ V}_{\text{pp}}$ verso comparatore interno LM324 |
| **4** | `CASSETTE_OUT_ALT` | Computer $\rightarrow$ Tape | Seconda linea di uscita audio/dati (internamente collegata al Pin 1 sulla scheda madre) |
| **5** | `N/C` | — | Non connesso |
| **6** | `MOTOR_REM_A` | Computer $\leftrightarrow$ Tape | Polo A contatto pulito relè comando motore interno BBC Micro |
| **7** | `MOTOR_REM_B` | Computer $\leftrightarrow$ Tape | Polo B contatto pulito relè comando motore interno BBC Micro |

---

## 3. Protocollo di Codifica Dati Acorn (CUTS / Kansas City Standard)
Il sistema operativo Acorn MOS (Machine Operating System) implementa una codifica a modulazione a spostamento di frequenza (FSK) compatibile con lo standard CUTS (*Computer Users Tape Standard*):
1. **Frequenze Portanti FSK**:
   - Frequenza **Mark** (Logico `1`): $2400\text{ Hz}$ (tono ad alta frequenza);
   - Frequenza **Space** (Logico `0`): $1200\text{ Hz}$ (tono a bassa frequenza).
2. **Velocità di Trasmissione (Baud Rate)**:
   - **300 baud standard**: 8 cicli completi di $2400\text{ Hz}$ per bit '1'; 4 cicli completi di $1200\text{ Hz}$ per bit '0'.
   - **1200 baud veloce**: 2 cicli completi di $2400\text{ Hz}$ per bit '1'; 1 ciclo completo di $1200\text{ Hz}$ per bit '0'.
3. **Formato del Frame Asincrono**:
   - 1 bit di Start (Space, `0`);
   - 8 bit di Dati (trasmessi dal bit meno significativo LSB al più significativo MSB);
   - 1 bit di Stop (Mark, `1`).
4. **Header e Blocco Dati**:
   - Preambolo sincrono (*Leader Tone*): tono continuo a $2400\text{ Hz}$ per almeno diversi secondi prima di ciascun blocco;
   - Carattere di sincronizzazione blocco: `0x2A` (carattere ASCII `*`);
   - Intestazione del file: nome del file (fino a 10 caratteri), indirizzo di caricamento (Load Address a 32-bit), indirizzo di esecuzione (Execution Address a 32-bit), numero di blocco progressivo, lunghezza blocco (fino a 256 byte per blocco), checksum CRC-16 CCITT.

---

## 4. Controllo Motore (`REM_A` / `REM_B`)
- All'interno del computer BBC Micro ed Electron è presente un relè elettromeccanico pilotato dal MOS tramite transistor buffer.
- Quando il software esegue `*MOTOR 1` (o durante le routine di `*LOAD`, `*SAVE`, `CHAIN`):
  - Il relè interno si **chiude**, stabilendo continuità a bassa resistenza ($R_{\text{on}} \approx 0\ \Omega$) tra Pin 6 e Pin 7.
- Quando il comando `*MOTOR 0` viene inviato (o al termine del trasferimento blocco):
  - Il relè interno si **apre**, interrompendo la continuità elettrica.
- **Interfacciamento Tape Master**:
  - Il Pin 7 è collegato alla massa `GND` della cartuccia;
  - Il Pin 6 è tirato a `+5V` tramite resistenza di pull-up ($10\text{ k}\Omega$);
  - Un inverter / circuito di sensing bufferizza lo stato verso `MOTOR_SENSE` del bus a 40 pin del Tape Master:
    - Relè chiuso (Motore Attivo): Pin 6 a $0\text{ V} \rightarrow \text{MOTOR\_SENSE} = 3.3\text{ V}$ (HIGH);
    - Relè aperto (Motore Fermo): Pin 6 a $5\text{ V} \rightarrow \text{MOTOR\_SENSE} = 0\text{ V}$ (LOW).
  - Un transistor MOSFET `BSS138` (pilotato da `MOTOR_CTRL`) è predisposto in parallelo per consentire il test a banco o il forzamento del motore.

---

## 5. Mappatura Segnali su Bus Cartuccia 40 Pin Tape Master v2

| Pin Bus 40P | Segnale Cartuccia | Direzione | Funzione |
| :---: | :--- | :---: | :--- |
| **1, 2** | `+5V_RAW` | Alimentazione | Alimentazione buffer `74HCT06`, pull-up relè e TVS |
| **3, 4** | `+3V3_CLEAN` | Alimentazione | Alimentazione EEPROM `24C02` e clamp Schottky `BAT54S` |
| **6, 15, 23, 40** | `GND` | Massa | Masse digitali e ritorni di potenza |
| **7, 9, 11, 13** | `AGND` | Shield Analogico | Massa analogica filtrata di guardia per audio IN/OUT |
| **8** | `AUDIO_RAW_L` | Analog Out | Segnale `CASSETTE_OUT` BBC Micro AC-coupled verso preamp/VU-meter azimut |
| **12** | `AUDIO_DAC_L` | Analog In | Segnale FSK analogico sintetizzato dal DAC RP2040 verso `CASSETTE_IN` |
| **16** | `TAPE_EMU_OUT`| Digitale In | Impulsi digitali FSK dal PIO RP2040 tramite buffer 74HCT06 verso `CASSETTE_IN` |
| **17** | `TAPE_REC_IN` | Digitale Out | Uscita logica condizionata da `CASSETTE_OUT` verso timer capture PIO |
| **18** | `MOTOR_SENSE` | Digitale Out | Stato motore rilevato dal relè BBC Micro (High = attivo) |
| **19** | `MOTOR_CTRL` | Digitale In | Pilotaggio opzionale per chiusura forzata circuito relè a banco |
| **24, 25** | `I2C_SCL`, `I2C_SDA` | I2C Bidirezionale | Bus di auto-riconoscimento per EEPROM `24C02` (Indirizzo `0x50`) |
| **26** | `CART_DETECT_N`| Output a GND | Presenza cartuccia (collegato permanentemente a massa) |
