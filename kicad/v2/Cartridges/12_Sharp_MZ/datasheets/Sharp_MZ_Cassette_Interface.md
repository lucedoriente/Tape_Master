# Sharp MZ Series Cassette & CMT Interface Technical Datasheet
**Cartridge #12 — Tape Master Exerciser & Signal Digitizer v2**
**Author:** Alessio Iodice <alessio67@gmail.com>  
**Revision:** 2.0 (KiCad 9.0)  
**Date:** 2026-11-06  
**License:** CC BY-NC-SA 4.0  

---

## 1. Overview & Supported Platforms
The **Sharp MZ Series Cartridge (#12)** provides comprehensive hardware emulation, signal digitization, and automated exerciser control for the legendary **Sharp MZ** family of 8-bit computers.

### Supported Systems:
- **Sharp MZ-80K / MZ-80C / MZ-80A / MZ-80B**
- **Sharp MZ-700 Series**: MZ-711 (clean rear jack version), MZ-721 (with MZ-1T01 built-in data recorder), MZ-731 (with plotter)
- **Sharp MZ-800 Series**: MZ-811, MZ-821, MZ-831
- **Sharp MZ-1500 Series**
- **Sharp MZ-2000 / MZ-2200 Series**

---

## 2. CMT & Audio Interface Connectors

### A. Internal / External CMT Connector (`P-12` Style / `J4`)
Standard 9-pin single-row 2.54 mm pitch keyed header (`J4`) matching the factory Sharp internal tape data recorder cable:

| Pin | Signal | Direction (from MZ) | Description | Tape Master Bus Mapping |
| :---: | :---: | :---: | :--- | :--- |
| **1** | `EX_WRITE` | Output | Audio / Mic output to recorder | `TAPE_REC_IN` / `AUDIO_RAW_L` (via divider/AC) |
| **2** | `EX_READ` | Input | Audio / Ear input to MZ | `TAPE_EMU_OUT` / `AUDIO_DAC_L` (AC coupled) |
| **3** | `GND` | Power | System Ground | `GND` |
| **4** | `MOTOR_REM` | Output | Motor Control / Remote relay line | `MOTOR_SENSE` (divider) / `MOTOR_CTRL` (Q1 MOSFET) |
| **5** | `SENSE` | Input | Play key sense switch (Active LOW) | `TAPE_SENSE` (Q2 MOSFET) / `JP1` (Force Play) |
| **6** | `+5V` | Power | Host +5V Supply | Host Monitor LED `D_PWR` / Bench Power |
| **7** | `WRITE_TTL` | Output | Direct digital TTL write data (8255 PC1) | `TAPE_REC_IN` (via divider/clamp D1) |
| **8** | `READ_TTL` | Input | Direct digital TTL read data (8255 PB4) | `READ_BUF_OUT` (74HCT06 open-drain buffer) |
| **9** | `GND` | Power | System Ground | `GND` |

### B. Dual 3.5 mm Phone Jacks (`J2` and `J3`)
Standard audio mini-jacks for MZ-711, MZ-811, or external cassette tape recorder decks:
- **`J2` (`EX-READ` / Earphone)**: Calibrated audio output from Tape Master into Sharp MZ external tape read input.
  - Tip: `SHARP_READ` (AC coupled signal)
  - Ring: `GND`
  - Sleeve: `GND`
- **`J3` (`EX-WRITE` / Microphone)**: Cassette record input from Sharp MZ into Tape Master digitizer.
  - Tip: `SHARP_WRITE`
  - Ring: `GND`
  - Sleeve: `GND`

### C. Bench Breakout Header (`J5`, 1x08 2.54 mm Pin Header)
Exposes all primary diagnostic signals for workbench oscilloscope probes, logic analyzers, and multi-meter checks:
- Pin 1: `GND`
- Pin 2: `+5V` (Host power)
- Pin 3: `SHARP_READ` (AC Audio Read)
- Pin 4: `READ_BUF_OUT` (5V TTL Read Data)
- Pin 5: `SHARP_WRITE` (Write Data)
- Pin 6: `SHARP_MOTOR` (Motor Control)
- Pin 7: `SHARP_SENSE` (Play Sense Line)
- Pin 8: `+3V3` (Tape Master 3.3V Logic Rail)

### D. Force Play Override Jumper (`JP1`, 1x02 2.54 mm)
- **Pins 1-2 Shorted**: Permanently asserts `SHARP_SENSE` to GND, allowing automated software loading without waiting for manual PLAY key interaction.
- **Pins 1-2 Open**: `SHARP_SENSE` is fully controlled dynamically by Tape Master MCU via MOSFET `Q2`.

---

## 3. Tape Modulation & Protocol Details
- **Modulation Standard**: Manchester-like Pulse Width Modulation (PWM) with high noise immunity.
- **Nominal Baud Rate**: 1200 baud (approx. 150 bytes/second, significantly faster than Commodore 300 baud).
- **Pulse Timing**:
  - Bit '0': $32\ \mu\text{s}$ pulse interval.
  - Bit '1': $64\ \mu\text{s}$ pulse interval.
  - Lead Tone: 2000 Hz continuous carrier tone.
- **Hardware Architecture**:
  - The Sharp MZ uses an Intel 8255 PPI (Programmable Peripheral Interface) and 8253 PIT (Programmable Interval Timer) to directly generate and measure pulse intervals in hardware, bypassing software polling timing loops.

---

## 4. Signal Conditioning & Electrical Design
1. **TTL Read Buffer (`U2` 74HCT06)**:
   - Level shifts 3.3V `TAPE_EMU_OUT` logic pulses to fast, high-drive 5V open-drain levels with $4.7\text{ k}\Omega$ pull-up resistors.
   - Dual-stage cascading delivers non-inverted `READ_BUF_OUT` TTL pulses to CMT Pin 8.
   - Low-pass and resistive attenuation network ($R_9 = 1\text{ k}\Omega$, $C_3 = 4.7\ \mu\text{F}$, $R_{10} = 10\text{ k}\Omega$) feeds the analog audio read jack `J2`.
2. **Audio Write Conditioning**:
   - Resistor divider ($R_1 = 2.2\text{ k}\Omega$, $R_2 = 3.3\text{ k}\Omega$) reduces 5V logic pulses to 3.0V level.
   - Dual Schottky clamp BAT54S (`D1`) prevents voltage spikes exceeding $+3.3\text{ V} + 0.3\text{ V}$ or falling below $-0.3\text{ V}$.
   - AC coupled monitoring branch ($C_4 = 4.7\ \mu\text{F}$, $R_{11} = 1\text{ k}\Omega$, $C_5 = 10\text{ nF}$, $R_{12} = 10\text{ k}\Omega$) connects to `AUDIO_RAW_L` for real-time digitizer ADC and front panel VU-meter.
3. **Motor Remote Control & Sense**:
   - Voltage divider ($R_4 = 2.2\text{ k}\Omega$, $R_5 = 3.3\text{ k}\Omega$) with BAT54S (`D2`) delivers safe 3.3V logic level to `MOTOR_SENSE`.
   - N-channel MOSFET 2N7002 (`Q1`) actively sinks the `MOTOR_REM` line when enabled by `MOTOR_CTRL`.
4. **Sense Automation**:
   - N-channel MOSFET 2N7002 (`Q2`) pulls `SHARP_SENSE` to GND when commanded by `TAPE_SENSE`, satisfying the Sharp MZ Monitor ROM PLAY interlock.
5. **ESD Protection**:
   - USBLC6-2SC6 TVS diode array (`D3`) shields all four external I/O lines against human-body electrostatic discharge.
6. **Smart Plug & Play EEPROM (`U1` 24C02)**:
   - 2-Kbit I2C EEPROM at address `0x50` storing cartridge identification, hardware revision, and default timing parameters.
