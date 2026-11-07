# Specifiche Tecniche Interfaccia Cassetta Tandy CoCo & Dragon 32/64
**Autore / Hardware Designer**: Alessio Iodice (<alessio67@gmail.com>)  
**Contesto Operativo**: Tape Master Exerciser & Signal Digitizer v2 — Cartuccia #08  
**Toolchain Target**: KiCad 9.0 (`version 20250114`)  
**Licenza**: CC BY-NC-SA 4.0  

---

## 1. Panoramica dello Standard Cassetta CoCo & Dragon
La linea personal computer a microprocessore Motorola 6809 di Radio Shack / Tandy (**TRS-80 Color Computer 1, 2 e 3**, **Tandy MC-10**) e la famiglia britannica compatibile **Dragon Data (Dragon 32 e Dragon 64)** condividono lo stesso standard di connessione registratore su connettore femmina **DIN 5-Pin 180°** (standard industriale DIN 41524 / IEC 60130-9, connettore serie CUI / Same Sky SDS-50J).

Tale interfaccia è inoltre elettricamente compatibile con la piedinatura del cavo a nastro dei celebri computer Z80 **TRS-80 Model I, Model III e Model 4**.

---

## 2. Pinout Ufficiale Connettore DIN 5-Pin 180° (CoCo / Dragon Cassette Port)

```text
       Presa Femmina sul Computer / Cartuccia       Connettore Maschio sul Cavo
                      __ 1   3 __                           __ 3   1 __
                    /             \                       /             \
                   /  4    2    5  \                     /  5    2    4  \
                  |                 |                   |                 |
                   \     \   /     /                     \     \   /     /
                    \      V      /                       \      V      /
                      -----------                           -----------
```

| Pin DIN 5 | Nome Segnale | Direzione (Computer $\leftrightarrow$ Tape) | Descrizione Tecnica e Livelli Elettrici |
| :---: | :--- | :---: | :--- |
| **1** | `MOTOR_REM_A` | Computer $\leftrightarrow$ Tape | Primo polo contatto relè comando motore interno (collegato a massa su cavo) |
| **2** | `GND` | — | Massa comune di segnale e schermo cavi |
| **3** | `MOTOR_REM_B` | Computer $\leftrightarrow$ Tape | Secondo polo contatto relè comando motore interno |
| **4** | `CASSETTE_IN` | Tape $\rightarrow$ Computer | Ingresso audio/dati al computer (collegato a `EAR` registratore). Livello $1 \dots 2.5\text{ V}_{\text{pp}}$ verso comparatore SAM / multiplexer |
| **5** | `CASSETTE_OUT` | Computer $\rightarrow$ Tape | Uscita audio/dati dal computer (collegata a `MIC` registratore). Livello $1 \dots 2\text{ V}_{\text{pp}}$ AC generato dal DAC 6-bit / PIA 6821 |

---

## 3. Protocollo di Codifica Dati (CoCo / Dragon / TRS-80)
1. **Modulazione FSK CoCo / Dragon (Color BASIC & Dragon OS)**:
   - Frequenza **Mark** (Logico `1`): $2400\text{ Hz}$ (1 ciclo intero di $416\text{ }\mu\text{s}$ per bit a 1200/1500 baud);
   - Frequenza **Space** (Logico `0`): $1200\text{ Hz}$ (1 ciclo intero di $833\text{ }\mu\text{s}$ per bit a 1200/1500 baud);
   - Baud Rate nominale: circa $1500\text{ baud}$ (modalità standard);
   - Preambolo sincrono (*Leader Tone*): segnale continuo sinusoidale/quadro alternato a $1200/2400\text{ Hz}$ seguito dal byte di sincronizzazione `0x55` e dal byte di intestazione `0x3C`.
2. **Compatibilità TRS-80 Model I/III**:
   - Codifica a treno d'impulsi e transizioni di zero (*zero-crossing pulse length*);
   - Velocità standard: $500\text{ baud}$ (Level I e Level II standard) e $1500\text{ baud}$ (Model III/4 ad alta velocità).

---

## 4. Controllo Motore (`REM_A` / `REM_B`)
- All'interno del computer CoCo e Dragon è presente un relè a lamelle (*reed relay*) comandato dal microprocessore tramite bit di uscita della PIA 6821.
- Comandi BASIC:
  - `MOTOR ON` (chiusura contatti tra Pin 1 e Pin 3, resistenza $R_{\text{on}} \approx 0\ \Omega$);
  - `MOTOR OFF` (apertura contatti).
- **Interfacciamento Tape Master**:
  - Pin 1 collegato a massa permanente (`GND`);
  - Pin 3 tirato a `+5V` via resistenza di pull-up ($10\text{ k}\Omega$) con partitore $2.2\text{ k}\Omega / 3.3\text{ k}\Omega$ e diodo di clamp Schottky **BAT54S** verso `MOTOR_SENSE` (relè chiuso $\rightarrow$ 0V, indicando motore attivo);
  - Transistor MOSFET `2N7002` in parallelo comandato da `MOTOR_CTRL` per simulare o forzare il motore durante test a banco.

---

## 5. Mappatura Segnali su Bus Cartuccia 40 Pin Tape Master v2

| Pin Bus 40P | Segnale Cartuccia | Direzione | Funzione |
| :---: | :--- | :---: | :--- |
| **1, 2** | `+5V_RAW` | Alimentazione | Alimentazione buffer `74HCT06`, pull-up relè e TVS |
| **3, 4** | `+3V3_CLEAN` | Alimentazione | Alimentazione EEPROM `24C02` e clamp Schottky `BAT54S` |
| **6, 15, 23, 40** | `GND` | Massa | Masse digitali e ritorni di potenza |
| **7, 9, 11, 13** | `AGND` | Shield Analogico | Massa analogica filtrata di guardia per audio IN/OUT |
| **8** | `AUDIO_RAW_L` | Analog Out | Segnale `COCO_WRITE` AC-coupled verso preamp/VU-meter azimut |
| **12** | `AUDIO_DAC_L` | Analog In | Segnale FSK analogico dal DAC RP2040 verso `COCO_READ` |
| **16** | `TAPE_EMU_OUT`| Digitale In | Impulsi digitali FSK dal PIO RP2040 tramite buffer 74HCT06 verso `COCO_READ` |
| **17** | `TAPE_REC_IN` | Digitale Out | Uscita logica condizionata da `COCO_WRITE` verso timer capture PIO |
| **18** | `MOTOR_SENSE` | Digitale Out | Stato motore rilevato dal relè CoCo/Dragon (Low = attivo) |
| **19** | `MOTOR_CTRL` | Digitale In | Pilotaggio opzionale per chiusura forzata circuito relè a banco |
| **24, 25** | `I2C_SCL`, `I2C_SDA` | I2C Bidirezionale | Bus di auto-riconoscimento per EEPROM `24C02` (Indirizzo `0x50`) |
| **26** | `CART_DETECT_N`| Output a GND | Presenza cartuccia (collegato permanentemente a massa) |
