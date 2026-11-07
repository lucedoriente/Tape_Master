# Amstrad CPC 464 / 664 / 6128 Cassette Interface Specification

| Proprietà | Valore / Riferimento |
| :--- | :--- |
| **Piattaforma Target** | Amstrad CPC 464 (porta esterna), CPC 664, CPC 6128, Schneider CPC |
| **Connettore Fisico Host** | Presa DIN 5-pin 180° femmina (standard DIN 41524 / IEC 60130-9) |
| **Modulo Tape Master** | Cartuccia 05 — Amstrad CPC (`05_Amstrad_CPC`) |
| **Autore** | Alessio Iodice (`alessio67@gmail.com`) |
| **Data** | 2026-11-06 |
| **Revisione** | 2.0 |

---

## 1. Panoramica del Bus Nastro Amstrad CPC

I computer della linea Amstrad CPC (CPC 464, CPC 664 e CPC 6128) utilizzano un'interfaccia a nastro standard basata su un connettore DIN a 5 poli a 180°.
- Sui modelli **CPC 664** e **CPC 6128**, la porta DIN posteriore etichettata `TAPE` è l'unico mezzo di collegamento per un registratore a cassette esterno.
- Sul modello **CPC 464**, dotato di deck interno incorporato, la porta DIN posteriore consente di collegare un deck ausiliario per operazioni di copia o riversamento.

### Standard di Codifica e Frequenze
L'Amstrad CPC utilizza una modulazione a frequenze FSK (Frequency Shift Keying) a due toni:
- **Velocità Standard (1000/2000 baud)**:
  - Tono di Sincronismo (Leader tone): $\approx 1300\text{ Hz}$
  - Bit '0': un semiperiodo a $\approx 2000\text{ Hz}$ e un semiperiodo a $\approx 1000\text{ Hz}$
  - Bit '1': due semiperiodi a $\approx 2000\text{ Hz}$
- **Baud Rate Effettivo**: $1000 \dots 2000\text{ baud}$ (fino a $4000\text{ baud}$ con turbo loader software come *Speedlock*).

---

## 2. Piedinatura Connettore DIN 5-Pin 180° (`J2`)

La numerazione dei pin segue lo standard ufficiale DIN 41524 (vista frontale della presa femmina):

| Pin | Nome Segnale | Funzione sul Computer | Direzione Elettrica | Descrizione Tecnica |
| :---: | :--- | :--- | :---: | :--- |
| **1** | `CPC_REM_A` | Contatto Relè Motore A | Ingresso/Uscita | Primo capo del contatto pulito del relè interno al CPC |
| **2** | `GND` | Massa e Schermo | Riferimento | 0V comune |
| **3** | `CPC_REM_B` | Contatto Relè Motore B | Ingresso/Uscita | Secondo capo del relè interno; quando il motore è attivo, il CPC chiude Pin 1 e Pin 3 |
| **4** | `CPC_DATA_IN` | **READ / EAR** | Verso CPC (Input) | Segnale dati audio riprodotto dalla cassetta verso il computer Amstrad ($\approx 1 \dots 2\text{V}_{pp}$) |
| **5** | `CPC_DATA_OUT`| **WRITE / MIC** | Dal CPC (Output) | Segnale dati registrato dal computer Amstrad verso la cassetta (TTL / $\approx 5\text{V}$) |

---

## 3. Gestione Elettronica sul Tape Master v2

### A. Rilevamento e Controllo Motore (`REMOTE`)
All'interno del computer Amstrad (pilotato dal gate array / PPI 8255), un relè a lamelle (*reed relay*) chiude i contatti tra **Pin 1** e **Pin 3** per accendere il motore del registratore.
1. **Rilevamento Stato Motore Amstrad (`MOTOR_SENSE`)**:
   - `Pin 1` è collegato permanentemente a massa `GND` sul Tape Master.
   - `Pin 3` ha una resistenza di pull-up da $10\text{ k}\Omega$ verso `+5V`.
   - Quando il CPC attiva il motore, il suo relè interno chiude Pin 3 su Pin 1 $\rightarrow$ Pin 3 scende a 0V.
   - Questa linea passa attraverso un partitore $2.2\text{ k}\Omega / 3.3\text{ k}\Omega$ e diodi di clamp Schottky `BAT54S` a +3.3V/GND, pilotando l'ingresso `MOTOR_SENSE` dell'RP2040.
2. **Pilotaggio Registratore Amstrad Esterno Reale (`MOTOR_CTRL`)**:
   - Un relè a stato solido PhotoMOS (o doppio MOSFET `BSS138`) pilotato dalla linea `MOTOR_CTRL` della Mainboard è collegato tra Pin 1 e Pin 3: quando il Tape Master opera come collaudatore di un registratore Amstrad a banco, può azionarne direttamente il motore.

### B. Canale Dati di Riproduzione (`READ` / `DATA IN` - Pin 4)
- Il Tape Master genera il flusso di impulsi tramite `TAPE_EMU_OUT`.
- Buffer open-collector ad alta velocità `74HCT06` con pull-up da $10\text{ k}\Omega$ sull'ingresso e pull-up da $4.7\text{ k}\Omega$ verso `+5V`.
- Partitore e filtro con condensatore di disaccoppiamento AC da $4.7\ \mu\text{F}$ e resistenza shunt da $10\text{ k}\Omega$ per iniettare un segnale audio pulito e calibrato su Pin 4.

### C. Canale Dati di Registrazione (`WRITE` / `DATA OUT` - Pin 5)
- Il CPC trasmette impulsi a 5V TTL su Pin 5.
- Partitore resistivo $2.2\text{ k}\Omega / 3.3\text{ k}\Omega$ e clamp di sicurezza `BAT54S` per interfacciare in piena sicurezza la linea `TAPE_REC_IN` (3.3V) dell'RP2040.
- Derivazione AC con condensatore da $4.7\ \mu\text{F}$ verso `AUDIO_RAW_L` per il monitoraggio dinamico con il VU-meter sul pannello frontale durante i salvataggi.

### D. Smart Auto-ID EEPROM (`U1`)
- EEPROM I2C `24C02` configurata all'indirizzo `0x52` (`A0=0, A1=1, A2=0`), identificante univocamente la Cartuccia 05 Amstrad CPC.
- Pin 26 `CART_DETECT_N` vincolato a massa sul connettore bus 40-pin.

---

## 4. Header Breakout per Prove a Banco (`J3`)

Header maschio passo $2.54\text{ mm}$ (1x06) montato a bordo scheda con serigrafia esplicita:

| Pin # | Serigrafia | Connessione |
| :---: | :--- | :--- |
| **1** | `GND` | Massa di riferimento (Pin 2 DIN) |
| **2** | `+5V` | Alimentazione Tape Master +5V |
| **3** | `REM_A` | Contatto relè motore A (Pin 1 DIN - GND) |
| **4** | `REM_B` | Contatto relè motore B (Pin 3 DIN - Motor Sense) |
| **5** | `READ` | Cassette Data In verso CPC (Pin 4 DIN) |
| **6** | `WRITE` | Cassette Data Out dal CPC (Pin 5 DIN) |
