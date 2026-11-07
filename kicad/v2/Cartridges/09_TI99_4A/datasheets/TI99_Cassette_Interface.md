# Texas Instruments TI-99/4A — Specifiche Porta e Interfaccia Cassetta (DE-9)

| Parametro | Valore / Specifica |
| :--- | :--- |
| **Computer Console** | Texas Instruments TI-99/4 e TI-99/4A (TMS9900 CPU @ 3.0 MHz) |
| **Connettore Console** | D-Sub 9-pin Maschio (DE-9M) posizionato sul retro della console |
| **Cavo Ufficiale TI** | Cavo a Y a doppia cassetta TI PHA2000 (connettore DE-9F verso console, terminato con jack 3.5mm e 2.5mm) |
| **Registratore Ufficiale** | TI Program Recorder PHP2700 |
| **Gestione I/O** | Chip TMS9901 Programmable Systems Interface (PSI) tramite bus seriale CRU (Communications Register Unit) |
| **Velocità di Trasmissione** | 1200 baud nominali |
| **Modulazione Dati** | Audio FSK (Frequency Shift Keying): `1` (Mark) $\approx 1379\text{ Hz}$, `0` (Space) $\approx 689\text{ Hz}$ |
| **Architettura a Due Deck** | Supporto nativo simultaneo per 2 registratori: **CS1** (Lettura) e **CS2** (Lettura e Scrittura) |
| **Isolamento Elettrico** | Fotoaccoppiatori / optoisolatori integrati sulla scheda madre del computer |

---

## 1. Piedinatura Connettore Console TI-99/4A (DE-9 Maschio)

Vista frontale del connettore maschio sul retro del computer:
```
       1       2       3       4       5
     o       o       o       o       o
         o       o       o       o
         6       7       8       9
```

| Pin | Nome Segnale TI | Direzione (Console $\rightarrow$ Tape) | Registro CRU | Descrizione Funzionale |
| :---: | :--- | :---: | :---: | :--- |
| **1** | `CS1_MOTOR_P` | OUT | CRU Bit 22 | Comando relè motore registratore 1 (CS1). Quando attivo, la linea viene chiusa a massa. |
| **2** | `CS1_MOTOR_M` | OUT / GND | — | Ritorno di massa per il motore 1 (riferimento a massa console). |
| **3** | `CS2_OUT` (Mag Tape Out) | OUT | CRU Bit 25 | Uscita audio FSK dal computer verso l'ingresso microfono del registratore 2 (MIC). |
| **4** | `AUDIO_GATE` | OUT | CRU Bit 24 | Segnale di abilitazione e gating del percorso audio da/per la cassetta. |
| **5** | `CS2_OUT_RET` | OUT / GND | — | Ritorno di massa per l'uscita dati cassetta 2. |
| **6** | `CS2_MOTOR_P` | OUT | CRU Bit 23 | Comando relè motore registratore 2 (CS2). Quando attivo, la linea viene chiusa a massa. |
| **7** | `CS2_MOTOR_M` | OUT / GND | — | Ritorno di massa per il motore 2 (riferimento a massa console). |
| **8** | `TAPE_IN` (Mag Tape In) | IN | CRU Bit 27 | Ingresso audio FSK dal registratore verso il computer (jack EAR di CS1 o CS2). |
| **9** | `TAPE_IN_RET` | IN / GND | — | Ritorno di massa per il canale di lettura cassetta. |

---

## 2. Dettaglio Funzionamento Segnali Elettrici

### A. Canale Lettura Dati (`TAPE_IN` - Pin 8)
- Il computer TI-99/4A riceve onde quadre/sinusoidali centrate attorno a $0\text{ V}$ o con ampiezza tipica $\approx 1 \dots 2\text{ V}_{pp}$.
- Sulla scheda madre del TI-99, il segnale entra in un comparatore/amplificatore operazionale che squadratura gli impulsi e li presenta al bit 27 del TMS9901.
- In emulazione con **Tape Master v2**:
  - Il segnale digitale generato dall'RP2040 (`TAPE_EMU_OUT`) viene bufferizzato tramite open-collector **74HCT06** (`U2`), tirato a +5V con resistore di pull-up.
  - La rete RC ($R_9 = 1\text{ k}\Omega$, $C_3 = 4.7\ \mu\text{F}$, $R_{10} = 10\text{ k}\Omega$) provvede al disaccoppiamento AC e alla calibrazione dell'ampiezza a livello linea/cuffie per il comparatore del TI-99.

### B. Canale Scrittura Dati (`CS2_OUT` - Pin 3)
- Durante il salvataggio (`SAVE "CS2"`), il TI-99/4A genera il treno di impulsi FSK a 1200 baud su Pin 3.
- Condizionamento su **Tape Master v2**:
  - Partitore di tensione resistivo ($R_1 = 2.2\text{ k}\Omega$, $R_2 = 3.3\text{ k}\Omega$) per adattare la dinamica logica a 3.0V verso il microcontrollore.
  - Diodo Schottky a doppio elemento **BAT54S** (`D1`) collegato a `+3.3V` e `GND` per protezione da sovratensioni e sottotensioni.
  - Ramo analogico AC ($C_4 = 4.7\ \mu\text{F}$, filtro passa-basso $R_{11} = 1\text{ k}\Omega, C_5 = 10\text{ nF}$, carico $R_{12} = 10\text{ k}\Omega$) attestato su `AUDIO_RAW_L` (Pin 8 di `J1`) per il monitoraggio dinamico sul display OLED e sul VU-meter a 10 segmenti del front panel.

### C. Controllo Motori Remoti (CS1 e CS2)
- **Deck 1 (`CS1_MOTOR_P`, Pin 1)**:
  - Resistore di pull-up da $10\text{ k}\Omega$ (`R3`) a `+5V`.
  - Partitore resistivo ($R_4 = 2.2\text{ k}\Omega$, $R_5 = 3.3\text{ k}\Omega$) con clamp Schottky **BAT54S** (`D2`) verso la linea `MOTOR_SENSE` dell'RP2040.
  - Quando il TI-99 attiva il motore di CS1, il contatto interno del fotoaccoppiatore chiude Pin 1 a massa, portando `MOTOR_SENSE` a 0V (attivo basso).
  - MOSFET di pilotaggio esterno **2N7002** (`Q1`) pilotato dalla linea `MOTOR_CTRL` per azionare autonomamente un registratore esterno a banco.
- **Deck 2 (`CS2_MOTOR_P`, Pin 6)**:
  - Resistore di pull-up da $10\text{ k}\Omega$ (`R15`) a `+5V`.
  - Partitore resistivo ($R_{16} = 2.2\text{ k}\Omega$, $R_{17} = 3.3\text{ k}\Omega$) con clamp Schottky **BAT54S** (`D4`) attestato su `AUX_GPIO1` (Pin 21 del bus universale), consentendo al firmware del Tape Master di monitorare in modo totalmente indipendente anche la chiamata del secondo registratore.

### D. Audio Gate (`AUDIO_GATE` - Pin 4)
- Partitore resistivo ($R_{18} = 2.2\text{ k}\Omega$, $R_{19} = 3.3\text{ k}\Omega$) con clamp Schottky **BAT54S** (`D5`) attestato sulla linea ausiliaria `AUX_GPIO2` (Pin 22 del bus universale), consentendo al Tape Master di campionare lo stato di gating audio del computer.

---

## 3. Connettività Esterna & Test Breakout
- **`J2`**: Presa D-Sub 9-pin Femmina ad angolo retto (permette il collegamento diretto alla console TI-99/4A tramite cavo seriale maschio/femmina standard 1:1 dritto).
- **`J3`**: Pin header maschio orizzontale a passo 2.54 mm con 9 poli serigrafati (`GND`, `+5V`, `M1`, `OUT`, `GATE`, `M2`, `IN`, `GND`, `GND`) per collaudi rapidi a banco con oscilloscopio o analizzatore di stati logici.
