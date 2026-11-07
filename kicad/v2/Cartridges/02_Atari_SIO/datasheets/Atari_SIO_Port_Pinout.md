# Specifiche Tecniche Connettore Atari SIO (Serial Input/Output)

## 1. Descrizione Generale
Il bus SIO (*Serial Input/Output*) è l'interfaccia seriale proprietaria a 13 poli introdotta da Atari nel 1979 con i computer 400 e 800, e mantenuta su tutte le famiglie successive a 8-bit (1200XL, 600XL, 800XL, 65XE, 130XE, 800XE, XEGS).
Gestisce la comunicazione seriale bidirezionale asincrona a margherita (*daisy-chain*) con periferiche quali floppy disk drive (Atari 810, 1050, XF551), registratori a nastro (Atari 410, 1010, XC12, XC11), stampanti (Atari 820, 1025, 1029) e modem.

---

## 2. Piedinatura Ufficiale Atari SIO (13 Poli)

```
        ┌──────────────────────────────────────────────┐
        │  (2)   (4)   (6)   (8)   (10)   (12)         │  (Riga Superiore: 6 Pin)
        │                                              │
        │   (1)   (3)   (5)   (7)   (9)   (11)   (13)  │  (Riga Inferiore: 7 Pin)
        └──────────────────────────────────────────────┘
                    [ Vista Frontale Connettore ]
```

| Pin | Nome Segnale | Livello Logico / Tipo | Direzione | Descrizione Funzionale nel Registratore a Nastro |
| :---: | :--- | :---: | :---: | :--- |
| **1** | `CLOCK IN` | TTL 5V (BiDir) | In (verso Atari) | Clock bidirezionale riservato a trasferimenti sincroni (non usato su tape). |
| **2** | `CLOCK OUT` | TTL 5V | Out (da Atari) | Clock generato dalla console per periferiche sincrone (non usato su tape). |
| **3** | `DATA IN` | TTL 5V (Seriale) | In (verso Atari) | **Flusso dati seriale asincrono a 600 baud** demodulato dal registratore verso il POKEY. |
| **4** | `GND` | Massa | Power | Riferimento di terra comune. |
| **5** | `DATA OUT` | TTL 5V (Seriale) | Out (da Atari) | Dati seriali e comandi inviati dalla console al registratore in registrazione. |
| **6** | `GND` | Massa | Power | Riferimento di terra secondario. |
| **7** | `COMMAND` | TTL 5V (Attivo Basso) | Out (da Atari) | Segnale di strobe comando per periferiche intelligenti (floppy/stampanti). |
| **8** | `MOTOR CONTROL` | Open-Collector / 5V | Out (da Atari) | **Controllo trascinamento nastro**: commutato basso/alto dalla console per stop inter-blocco. |
| **9** | `PROCEED` | TTL 5V (Attivo Basso) | In (verso Atari) | Handshake di interrupt per stampanti/modem (non usato su tape). |
| **10** | `+5V / READY` | Alimentazione (+5V) | Out (da Atari) | Alimentazione ausiliaria erogata dalla console (corrente max $\le 500\text{ mA}$). |
| **11** | `AUDIO IN` | Analogico Audio ($1\text{ V}_{\text{pp}}$) | In (verso Atari) | **Traccia audio analogica stereo**: iniettata direttamente nel mixer audio del POKEY. |
| **12** | `+12V DC` | Alimentazione (+12V) | Out (da Atari) | Alimentazione motore registratore Atari 410 (presente **solo** su 400/800; assente su XL/XE). |
| **13** | `INTERRUPT` | TTL 5V (Attivo Basso) | In (verso Atari) | Linea di richiesta interruzione asincrona (non usata su tape). |

---

## 3. Parametri del Segnale FSK e Seriale Tape
* **Modulazione Dati**: Frequency Shift Keying (FSK) asincrono:
  * **Mark (Bit 1)**: $3995\text{ Hz}$
  * **Space (Bit 0)**: $5327\text{ Hz}$
* **Baud Rate Standard**: $600\text{ bps}$ (1 start bit, 8 data bit LSB-first, nessun bit di parità, 2 stop bit).
* **Modalità Turbo**: Sistemi turbo regionali (es. *Turbo 2000*, *Blizzard*) operano tra $1200\text{ bps}$ e $2400\text{ bps}$.
* **Traccia Audio Ausiliaria**: Canale sinistro audio stereo per lezioni, corsi di lingua o musica/effetti durante il caricamento (es. nastri didattici o *Ballyhoo*).
