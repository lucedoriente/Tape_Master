# Thomson MO5 / TO7 & Olivetti Prodest PC 128 Cassette Interface

## 1. Overview
The **Thomson MO5, TO7, TO7/70, MO6, TO8, TO8D, TO9, TO9+** and **Olivetti Prodest PC 128** (an Italian MO6 rebadge) share a standardized 5-pin 180° DIN cassette interface for external tape storage (*Lecteur Enregistreur de Programmes* - LEP).

## 2. DIN 5-Pin (180°) Connector Pinout

| Pin | Symbol | Function | Signal Direction | Electrical Standard |
| :---: | :---: | :--- | :--- | :--- |
| **1** | **`REM`** | Motor Remote Control | Computer $\rightarrow$ Tape Recorder | Open-Collector / Relay control |
| **2** | **`GND`** | Ground / Cable Shield | Power / Ground reference | 0V |
| **3** | **`AUDIO`** | Analog Audio Channel / Sound | Tape Recorder $\rightarrow$ Computer | Analog Audio line ($~1\text{V}_{pp}$) |
| **4** | **`READ`** | Cassette Data In (EAR) | Tape Recorder $\rightarrow$ Computer | Digital TTL / Level-detected pulse stream |
| **5** | **`WRITE`** | Cassette Data Out (MIC) | Computer $\rightarrow$ Tape Recorder | Digital TTL / 5V square wave modulation |

## 3. Tape Master Interface Architecture
1. **Bus Connection (`J1`)**: Universal $2 \times 20$ right-angle socket complanar to Mainboard. Pin 26 `CART_DETECT_N` hardwired to GND.
2. **DIN Port (`J2`)**: DIN 5 (180°) female socket for standard original cables.
3. **Bench-Test Header (`J3`)**: 6-pin 2.54 mm pin-header in parallel with all DIN lines for oscilloscope, logic analyzer, and bench prototyping.
4. **Smart Auto-ID EEPROM (`U1`)**: 24C02 on I2C bus identifying Cartridge ID #03.
5. **Level Buffering & Conditioning**:
   - `READ` line buffered with 74HCT / 74LVC driver towards the computer.
   - `WRITE` line conditioned with ESD protection and level translation towards RP2040.
   - `REM` (Motor Remote) detected with transistor/diode clamp towards RP2040 `MOTOR_SENSE` and pass-through relay.
   - `AUDIO` routed directly to Tape Master auxiliary audio input / digitizer.
6. **ESD Protection (`D2`)**: USBLC6-2SC6 TVS array on all exposed lines.
7. **Host Power Monitor (`D4`, `R10`)**: Green micro-LED monitoring host +5V supply.
