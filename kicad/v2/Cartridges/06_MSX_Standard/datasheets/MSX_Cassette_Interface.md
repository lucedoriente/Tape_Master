# Specifiche Tecniche Interfaccia Cassetta MSX (MSX 1 / MSX 2 / MSX 2+ / MSX Turbo-R)
**Autore / Hardware Designer**: Alessio Iodice (<alessio67@gmail.com>)  
**Contesto Operativo**: Tape Master Exerciser & Signal Digitizer v2 — Cartuccia #06  
**Toolchain Target**: KiCad 9.0 (`version 20250114`)  
**Licenza**: CC BY-NC-SA 4.0  

---

## 1. Panoramica dello Standard MSX Cassette
Lo standard MSX (definito da Microsoft e ASCII Corporation nel 1983) unifica l'architettura dei personal computer a 8-bit prodotti da dozzine di costruttori internazionali (Sony, Philips, Yamaha, Panasonic/Matsushita, Sanyo, Casio, Toshiba, Daewoo, GoldStar, Spectravideo, Gradiente).
Tutti i computer MSX adottano un'interfaccia a nastro standardizzata su connettore femmina **DIN 8-Pin 270°** (standard industriale DIN 45326 / IEC 60130-9, connettore serie CUI / Same Sky SDS-80J).

---

## 2. Pinout Ufficiale Connettore DIN 8-Pin 270° (MSX Cassette Port)

```text
       Presa Femmina sul Computer / Cartuccia       Connettore Maschio sul Cavo
                      __ 6   7 __                           __ 7   6 __
                    /     8     \                         /     8     \
                   /  4        5 \                       /  5        4 \
                  |   1   2   3   |                     |   3   2   1   |
                   \    \   /    /                       \    \   /    /
                    \     V     /                         \     V     /
                      ---------                             ---------
```

| Pin DIN 8 | Nome Segnale MSX | Direzione (MSX $\leftrightarrow$ Tape) | Descrizione Tecnica e Livelli Elettrici |
| :---: | :--- | :---: | :--- |
| **1** | `GND` | — | Massa di riferimento segnale e alimentazione |
| **2** | `GND` | — | Ritorno di massa aggiuntivo |
| **3** | `GND` | — | Ritorno di massa aggiuntivo |
| **4** | `CMTOUT` | Computer $\rightarrow$ Tape | Uscita audio/dati da registrare su cassetta (collegata a `MIC` registratore). Livello $1 \dots 2\text{ V}_{\text{pp}}$ AC o 5V TTL |
| **5** | `CMTIN` | Tape $\rightarrow$ Computer | Ingresso audio/dati letto da nastro (collegato a `EAR` registratore). Livello $500\text{ mV}_{\text{pp}} \dots 2.5\text{ V}_{\text{pp}}$ |
| **6** | `REM+` | Computer $\leftrightarrow$ Tape | Polo positivo contatto pulito relè comando motore interno MSX |
| **7** | `REM-` | Computer $\leftrightarrow$ Tape | Polo negativo contatto pulito relè comando motore interno MSX |
| **8** | `GND` | — | Massa di schermo centrale |

---

## 3. Protocollo di Codifica Dati MSX (BIOS FSK Kansas City Standard)
Il BIOS MSX implementa una modulazione a spostamento di frequenza (FSK):
1. **Baud Rate Standard (1200 baud)**:
   - Frequenza **Mark** (Bit `1`): $2400\text{ Hz}$ (2 periodi interi per bit);
   - Frequenza **Space** (Bit `0`): $1200\text{ Hz}$ (1 periodo intero per bit).
2. **Baud Rate Veloce (2400 baud)**:
   - Frequenza **Mark** (Bit `1`): $4800\text{ Hz}$ (2 periodi per bit);
   - Frequenza **Space** (Bit `0`): $2400\text{ Hz}$ (1 periodo per bit).
3. **Struttura del Frame**:
   - 1 bit di Start (Space, `0`);
   - 8 bit di Dati (LSB first);
   - 2 bit di Stop (Mark, `1`);
   - Header sincrono iniziale (*Leader Tone*): onda sinusoidale/quadra continua a $2400\text{ Hz}$ per sincronizzare il PLL e l'AGC della testina.

---

## 4. Controllo Motore (`REM+` / `REM-`)
- All'interno del computer MSX, il chip PPI 8255 (o MSX-Engine IC) pilota tramite transistor un relè elettromeccanico a contatti dorati.
- Quando il software esegue `MOTOR ON` (o operazioni di `CSAVE`, `CLOAD`, `BSAVE`, `BLOAD`):
  - Il relè si **chiude**, stabilendo continuità galvanica ($R_{\text{on}} \approx 0\ \Omega$) tra Pin 6 (`REM+`) e Pin 7 (`REM-`).
- Quando il software esegue `MOTOR OFF`:
  - Il relè si **apre**, interrompendo il circuito (resistenza infinita).
- Sulla Cartuccia Tape Master #06:
  - Il Pin 6 (`REM+`) è collegato a massa (`GND`);
  - Il Pin 7 (`REM-`) è polarizzato a +5V tramite pull-up $10\text{ k}\Omega$ (`R3`) e campionato tramite partitore di tensione protetto da diodi Schottky `BAT54S` verso la linea `MOTOR_SENSE` dell'RP2040.
  - In parallelo, un MOSFET N-channel `2N7002` (`Q1`) pilotato dalla linea `MOTOR_CTRL` consente alla Tape Master di emulare o comandare motori di deck esterni.
