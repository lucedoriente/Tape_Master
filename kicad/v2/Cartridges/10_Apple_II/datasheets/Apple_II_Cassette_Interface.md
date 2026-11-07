# Apple II / II+ / IIe Cassette Hardware Interface Specification

## 1. Overview and Architecture
The Apple II personal computer family (Apple II, Apple II Plus, Apple IIe) designed by Steve Wozniak incorporated a sophisticated, software-timed cassette tape interface capable of reliable data storage at ~1500 baud (~180 bytes/s). The interface on the motherboard terminates in two 3.5 mm (1/8") mono miniature phone jacks located on the back panel:
- **`CASSETTE IN`**: Receives recorded audio from the cassette recorder's `EAR` / `MONITOR` (headphone) jack.
- **`CASSETTE OUT`**: Sends recorded audio pulses to the cassette recorder's `MIC` (microphone) jack.

---

## 2. Modulation and Audio Encoding
The Apple II cassette protocol is zero-crossing interval modulated:
- **Leader / Sync Tone**: $770\text{ Hz}$ square/sine wave ($1300\ \mu\text{s}$ period; $650\ \mu\text{s}$ per half-cycle).
- **Sync Bit**: A truncated sync transition ($200\ \mu\text{s}$ half-cycle followed by $250\ \mu\text{s}$ half-cycle).
- **Logic '0' Bit**: 1 full cycle of $2000\text{ Hz}$ ($500\ \mu\text{s}$ total period; two half-cycles of $250\ \mu\text{s}$).
- **Logic '1' Bit**: 1 full cycle of $1000\text{ Hz}$ ($1000\ \mu\text{s}$ total period; two half-cycles of $500\ \mu\text{s}$).
- **Checksum**: 8-bit XOR checksum appended at the end of each record.

---

## 3. Electrical Characteristics and Signal Conditioning

### A. Input (Apple II to Tape Master — `APPLE_WRITE` / Cassette Out)
- **Motherboard Generation**: Triggered by accessing `$C020` (`SPKR`/`CASSOUT`), which toggles a flip-flop.
- **Motherboard Attenuation**: A resistive divider ($100\ \Omega$ series, $100\ \Omega$ shunt) drops the 5V logic signal down to mic-level ($\approx 50\text{ mV} \dots 500\text{ mV}_{pp}$).
- **Tape Master Conditioning**:
  - Divided by $2.2\text{ k}\Omega / 3.3\text{ k}\Omega$ (`R1`, `R2`) and clamped by fast Schottky diode **BAT54S** (`D1`) to `+3.3V` / `GND` into `TAPE_REC_IN`.
  - AC-coupled through $4.7\ \mu\text{F}$ (`C4`), low-pass filtered by $1\text{ k}\Omega$ (`R11`) / $10\text{ nF}$ (`C5`), and shunted by $10\text{ k}\Omega$ (`R12`) into `AUDIO_RAW_L` for real-time azimuth alignment and VU-meter bargraph display.

### B. Output (Tape Master to Apple II — `APPLE_READ` / Cassette In)
- **Apple II Input Circuit**: Uses an AC-coupled ($0.1\ \mu\text{F}$) zero-crossing detector based on an inverter (74LS04 biased with $1\text{ M}\Omega$) or operational amplifier/comparator (LM324/NE558). The output state is read by the CPU at address `$C060` bit 7.
- **Tape Master Conditioning**:
  - Open-collector high-speed buffer **74HCT06** (`U2`) in dual-inverter configuration with pull-up resistors $10\text{ k}\Omega$ (`R7`, `R8`) to `+5V`.
  - Attenuated and AC-coupled via series $1\text{ k}\Omega$ (`R9`), DC-blocking $4.7\ \mu\text{F}$ (`C3`), and shunt $10\text{ k}\Omega$ (`R10`) to GND, injecting a clean, calibrated $\approx 1.0\dots 1.5\text{ V}_{pp}$ signal into the Apple II `CASSETTE IN` port.
  - Secondary analog path directly from `AUDIO_DAC_L` via DC-blocking cap $4.7\ \mu\text{F}$ (`C6`) and series resistor $2.2\text{ k}\Omega$ (`R6`).

### C. Motor Remote Control & Sense
- While standard Apple II computers do not incorporate a cassette motor relay jack on the chassis, bench exerciser testing and standard tape decks (e.g. Panasonic RQ-2102) utilize a $2.5\text{ mm}$ remote plug.
- The cartridge provides a full remote motor control and sense circuit on the bench test header (`J4`) and internal lines:
  - Pull-up $10\text{ k}\Omega$ (`R3`) to +5V, divider $2.2\text{ k}\Omega / 3.3\text{ k}\Omega$ (`R4`, `R5`), and Schottky clamp **BAT54S** (`D2`) into `MOTOR_SENSE`.
  - Low-$R_{DS(on)}$ N-channel MOSFET **2N7002** (`Q1`) driven by `MOTOR_CTRL` via $100\ \Omega$ gate resistor (`R13`) and $100\text{ k}\Omega$ pulldown (`R14`).

---

## 4. Connectors
1. **`J2` (CASSETTE IN / EAR)**: 3.5 mm mono audio phone jack (CUI `SJ1-3533NG` horizontal circular holes).
2. **`J3` (CASSETTE OUT / MIC)**: 3.5 mm mono audio phone jack (CUI `SJ1-3533NG` horizontal circular holes).
3. **`J4` (Bench Test Header)**: $1 \times 06$ male pin header 2.54 mm pitch:
   - Pin 1: `GND`
   - Pin 2: `+5V`
   - Pin 3: `GND`
   - Pin 4: `REM` (`APPLE_REM_B` / Motor control line)
   - Pin 5: `RD` (`APPLE_READ` / Cassette In to Apple II)
   - Pin 6: `WR` (`APPLE_WRITE` / Cassette Out from Apple II)
4. **`J1` (Tape Master Bus)**: $2 \times 20$ right-angle female header with `CART_DETECT_N` (Pin 26) tied to `GND`.
