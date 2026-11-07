# Tape Master v2 - Cartuccia 01: Commodore C2N Datassette (PET / VIC-20 / C64 / C128 / C16)

| Proprietà | Dettaglio / Valore |
| :--- | :--- |
| **Progetto** | Tape Master Exerciser & Signal Digitizer v2 |
| **Modulo** | Cartuccia Espansione #01 - Commodore C2N Datassette (`01_Commodore_C2N`) |
| **Piattaforme Compatibili** | Commodore PET 2001/3000/4000/8000, VIC-20, Commodore 64, Commodore 128, Commodore 16, Plus/4 (con adattatore mini-DIN standard) |
| **Periferiche Supportate** | Datassette Commodore 1530 / 1531, cavi di prolunga per registratore originale a cassetta |
| **Autore & Hardware Designer** | Alessio Iodice (`alessio67@gmail.com`) |
| **Data di Rilascio** | 2026-11-06 |
| **Revisione** | 2.0 (KiCad 9.0 Nativo) |
| **Licenza** | CC BY-NC-SA 4.0 |
| **Stato Validazione KiCad 9** | **0 Violazioni ERC / 0 Violazioni DRC / 0 Net Non Connesse / 0 Parity Issues** |

---

## 1. Descrizione Architetturale

La **Cartuccia 01: Commodore C2N Datassette** interfaccia il sistema **Tape Master v2** al bus a cassetta proprietario Commodore (*Cassette Port*).
Il bus Commodore a 6 pin presenta un'interfaccia edge-connector con segnali logici digitali TTL a 5V:
- `GND` (Pin A-1 / B-1)
- `+5V` (Pin A-2 / B-2)
- `MOTOR` (Pin A-3 / B-3): Alimentazione del motore (9V/6V switched da computer)
- `READ` (Pin A-4 / B-4): Segnale dati in lettura verso il computer
- `WRITE` (Pin A-5 / B-5): Segnale dati in scrittura dal computer
- `SENSE` (Pin A-6 / B-6): Rilevamento pressione tasti Play/Record/Rew/FF

Il modulo cartuccia integra:
1. Connettore Card-Edge maschio sagomato su PCB (`J2`) con smussatura a 45° per innesto diretto nella porta cassetta del computer Commodore.
2. Connettore a pettine femmina (`J3`) per il collegamento passante di un vero registratore Commodore 1530 a scopo di sniffer/analizzatore.
3. Buffer open-collector ad alta velocità 74HCT06 per il pilotaggio della linea `READ`.
4. Condizionatori di livello e protezioni TVS/clamping Schottky per `WRITE`, `MOTOR` e `SENSE`.
5. EEPROM I2C 24C02 per Auto-ID Smart Plug & Play.

---

## 2. Centralizzazione Diagnostica sul Front Panel (Daughterboard)

Conformemente alle regole di progetto `tape-master-rules.md`, tutti i LED diagnostici sono centralizzati sull'UI Panel:
- **D2 (`PLAY`)**: Linea `READ` attiva verso il computer Commodore.
- **D3 (`REC`)**: Linea `WRITE` attiva proveniente dal computer Commodore.
- **D4 (`MOTOR`)**: Tensione motore abilitata dal computer.
- **D5 (`SIGNAL`)**: Feedback `SENSE` / impulsi di clock.
- **D6 (`PWR`)**: Alimentazione di sistema attiva.
- **D10..D19**: VU-meter analogico / regolazione azimut testina.
