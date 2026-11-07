# Tape Master v2.0 — Embedded Firmware (RP2040 Dual-Core)

Firmware ufficiale di controllo, emulazione e acquisizione per **Tape Master Exerciser & Signal Digitizer v2.0** basato su microcontrollore Raspberry Pi Pico (RP2040 a 133 MHz).

---

## 1. Architettura a Doppio Core e Zero-Jitter

Per garantire la massima precisione temporale durante la riproduzione e l'acquisizione di segnali a nastro magnetico (tolleranza $< 50\text{ ns}$):

```
┌─────────────────────────────────────────────────────────────┐
│                       RP2040 MCU                            │
├──────────────────────────────┬──────────────────────────────┤
│    CORE 0 (Application & UI) │    CORE 1 (Real-Time Engine) │
├──────────────────────────────┼──────────────────────────────┤
│ • File System FAT (MicroSD)  │ • State Machine PIO 0 (TX)   │
│ • Display OLED (SSD1306/SH)  │ • State Machine PIO 1 (RX)   │
│ • Rotary Encoder & Pulsanti  │ • DMA Ring Buffer temporali  │
│ • I2C Auto-ID Cartucce 24C02 │ • PLL Digitale Inseguimento  │
│ • Gestione Menu & Config     │ • Zero-Jitter Timer (<50 ns) │
│ • Pilotaggio TLC5916 (LEDs)  │ • Tone Gen & Burst Exerciser │
│ • Decodifica Formati File    │ • Buffer di acquisizione RAW │
└──────────────────────────────┴──────────────────────────────┘
```

* **Core 0 (Applicazione, UI & Storage)**: Esegue il rendering grafico su display OLED 128x64, gestisce il debounce dei pulsanti fisici e dell'encoder rotativo, controlla l'inserimento hot-plug delle cartucce via I2C, scorre le directory e legge/scrive i file sulla scheda MicroSD via bus SPI ad alta velocità (12.5 MHz).
* **Core 1 (Motore Real-Time)**: Dedicato al 100% alla gestione delle macchine a stati **PIO (Programmable I/O)**, campionando o emulando i fronti d'onda con precisione al sub-microsecondo senza subire interruzioni o jitter dal file system o dal display.

---

## 2. Struttura del Codice

```
firmware/
├── CMakeLists.txt                 # Script di build Pico-SDK C/C++
├── pico_sdk_import.cmake          # Import automatico Pico-SDK
├── config/
│   ├── hardware_pins.h            # Definizione hardware 1:1 dei 30 GPIO RP2040
│   └── version.h                  # Versione firmware (v2.0.0) e build info
├── drivers/
│   ├── oled_display.h/.c          # Driver SSD1306/SH1106 128x64 I2C con font 5x7
│   ├── tlc5916_leds.h/.c          # Driver dual-cascata 16 canali (VU-meter + 5 Status LED)
│   ├── cartridge_id.h/.c          # Lettura I2C Auto-ID EEPROM 24C02 & Hot-Plug
│   ├── buttons.h/.c               # Debounce tasti PLAY, REC, PREV, NEXT, ENC_SW
│   ├── encoder.h/.c               # Decodifica in quadratura Rotary Encoder con tabella a stati
│   ├── analog_frontend.h/.c       # ADC0 (Peak detector Azimut) & ADC1 (Raw Tape)
│   ├── motor_control.h/.c         # Gestione linee MOTOR SENSE, MOTOR CTRL e TAPE SENSE
│   ├── sd_card.h/.c               # Driver SPI a blocchi per MicroSD (SD, SDHC, SDXC)
│   └── fat_fs.h/.c                # Stack leggero FAT16/FAT32 con file browser e streaming
├── formats/
│   ├── tap_c64.h/.c               # Parser e decodificatore impulsi Commodore .TAP (v0 e v1)
│   ├── tzx_spectrum.h/.c          # Parser TZX v1.20 (Standard, Turbo, Pure Tone, Pause)
│   └── csw_raw.h/.c               # Parser e generatore Compressed Square Wave (.CSW v2)
├── engine/
│   ├── virtual_deck.h/.c          # Emulatore registratore virtuale con pausa automatica host MOTOR
│   ├── signal_digitizer.h/.c      # Acquisizione impulsi sub-microsecondo e dump stream su SD
│   └── exerciser_engine.h/.c      # Generatore toni calibrazione (1/2 kHz), burn-in motore e loopback
├── pio/
│   ├── pulse_timer_rx.pio         # Cattura temporale ad alta precisione intervalli impulsi
│   ├── pulse_gen_tx.pio           # Generatore impulsi digitali calibrati (C2N, Sharp)
│   └── audio_pwm_tx.pio           # Toggler half-period per onde audio (Spectrum, MSX, Apple)
├── ui/
│   └── ui_menu.h/.c               # Macchina a stati interfaccia grafica (Home, Browser, Azimut, Test)
└── main.c                         # Inizializzazione periferiche e coordinamento dual-core
```

---

## 3. Mappatura Hardware GPIO

| GPIO RP2040 | Segnale Scheda Madre | Descrizione Hardware |
| :---: | :--- | :--- |
| **GP0** | `/CART_IRQ_N` | Interrupt hardware slot cartuccia |
| **GP1** | `/CART_DETECT_N` | Rilevamento presenza cartuccia (GND su J1.26) |
| **GP2** | `/ENC_A` | Canale A Rotary Encoder frontale |
| **GP3** | `/ENC_B` | Canale B Rotary Encoder frontale |
| **GP4** | `/I2C_SDA` | I2C0 Dati: OLED 128x64 + EEPROM 24C02 Cartuccia |
| **GP5** | `/I2C_SCL` | I2C0 Clock: OLED 128x64 + EEPROM 24C02 Cartuccia |
| **GP6** | `/ENC_SW` | Tasto a pressione Rotary Encoder |
| **GP7** | `/BTN_PLAY` | Tasto tattile frontale PLAY |
| **GP8** | `/BTN_REC` | Tasto tattile frontale REC |
| **GP9** | `/BTN_PREV` | Tasto tattile frontale PREV / REW |
| **GP10** | `/BTN_NEXT` | Tasto tattile frontale NEXT / FFWD |
| **GP11** | `/AUX_GPIO2` | Espansione bus cartuccia |
| **GP12** | `/MOTOR_SENSE` | Rilevamento linea motore dal computer vintage |
| **GP13** | `/MOTOR_CTRL` | Comando relè / FET motore esterno |
| **GP14** | `/TAPE_SENSE` | Linea rilevamento tasto Play / Sense |
| **GP15** | `/TAPE_DIGITIZED` | Uscita digitale squadrata dal comparatore LM393 |
| **GP16** | `/SD_MISO` | SPI0 RX MicroSD |
| **GP17** | `/SD_CS` | SPI0 Chip Select MicroSD |
| **GP18** | `/SD_SCK` | SPI0 Clock MicroSD + Shift Clock TLC5916 LED Bar |
| **GP19** | `/SD_MOSI` | SPI0 TX MicroSD + Serial Data TLC5916 LED Bar |
| **GP20** | `/LEDBAR_LE` | Latch Enable shift register LED Bar |
| **GP21** | `/TAPE_EMU_OUT` | Uscita impulsi Virtual Tape Deck via PIO |
| **GP22** | `/TAPE_REC_IN` | Ingresso impulsi da computer via PIO |
| **GP26 / ADC0** | `/AZIMUTH_PEAK_ADC` | Tensione analogica Peak Detector per barra Azimut |
| **GP27 / ADC1** | `/TAPE_RAW_ADC` | Ingresso analogico diretto da testina |
| **GP28 / ADC2** | `/AUX_GPIO` | Ingresso ausiliario |

---

## 4. Compilazione e Flashing

### Prerequisiti
* **Pico-SDK** (v1.5.0 o superiore) con variabile d'ambiente `PICO_SDK_PATH` configurata.
* **CMake** (v3.13+) e toolchain GNU `arm-none-eabi-gcc`.

### Build
```bash
cd firmware
mkdir build
cd build
cmake ..
make -j4
```

Verrà generato il binario `tape_master_v2.uf2`.

### Flashing su Raspberry Pi Pico
1. Tenere premuto il tasto **BOOTSEL** sulla scheda RP2040 mentre si collega il cavo USB al computer.
2. La scheda verrà montata come unità disco rimovibile `RPI-RP2`.
3. Trascinare il file `tape_master_v2.uf2` nell'unità: il Pico si riavvierà automaticamente avviando Tape Master v2.
