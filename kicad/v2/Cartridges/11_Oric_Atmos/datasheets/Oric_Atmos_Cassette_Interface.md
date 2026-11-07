# Oric 1 / Oric Atmos / Telestrat Cassette Hardware Interface Specification

## 1. Overview and Architecture
The Oric personal computer family (Oric-1 in 1983, Oric Atmos in 1984, and Oric Telestrat in 1986), produced by Tangerine Computer Systems, utilizes a dedicated tape interface terminating in a standard **DIN 7-Pin 270° female socket** (DIN 45322 / IEC 60130-9, CUI / Same Sky series `SDS-70J`) on the rear panel.

The interface incorporates data playback from tape, data recording to tape, auxiliary audio output, and an automated motor start/stop control line.

---

## 2. Modulation and Audio Encoding
The Oric firmware supports two nominal recording speeds:
- **Standard Speed (Slow / 300 baud)**:
  - Space ($0$): $1200\text{ Hz}$ tone (1 full cycle).
  - Mark ($1$): $2400\text{ Hz}$ tone (1 full cycle).
  - Byte format: 1 start bit ($0$), 8 data bits (LSB first), 1 parity bit (even), 3 stop bits ($1$).
- **Hyper-Load Speed (Fast / 2400 baud)**:
  - Space ($0$): $2400\text{ Hz}$ tone.
  - Mark ($1$): $4800\text{ Hz}$ tone.
- **Sync Header**: 16-second tone train followed by sync bytes `$16 $16 $16 $24`.

---

## 3. Electrical Characteristics and Signal Conditioning

### A. Playback Channel (Tape to Oric — `ORIC_READ` / TAPE IN — Pin 3 DIN)
- **Oric Motherboard Input**: The signal enters through an AC coupling network into an LM3900 quad Norton operational amplifier (or discrete transistor on later boards) configured as a high-gain zero-crossing comparator.
- **Tape Master Output**:
  - High-speed open-collector buffer **74HCT06** (`U2`) in dual-inverter configuration with pull-up resistors $4.7\text{ k}\Omega$ (`R7`, `R8`) to `+5V`.
  - Attenuated and AC-coupled via series $1\text{ k}\Omega$ (`R9`), DC-blocking $4.7\ \mu\text{F}$ (`C3`), and shunt $10\text{ k}\Omega$ (`R10`) to GND, delivering a clean, calibrated $\approx 1.0\dots 1.5\text{ V}_{pp}$ signal to Pin 3.
  - Secondary analog path directly from `AUDIO_DAC_L` via DC-blocking cap $4.7\ \mu\text{F}$ (`C6`) and series resistor $2.2\text{ k}\Omega$ (`R6`).

### B. Recording Channel (Oric to Tape — `ORIC_WRITE` / TAPE OUT — Pin 4 & Pin 5 DIN)
- **Oric Motherboard Output**: Driven by the ULA and the AY-3-8912 programmable sound generator (PSG), producing an audio-level signal between $\approx 100\text{ mV}_{pp}$ and $500\text{ mV}_{pp}$.
- **Tape Master Input Conditioning**:
  - Divided by $2.2\text{ k}\Omega / 3.3\text{ k}\Omega$ (`R1`, `R2`) and clamped by fast Schottky diode **BAT54S** (`D1`) to `+3.3V` and `GND` into `TAPE_REC_IN`.
  - AC-coupled through $4.7\ \mu\text{F}$ (`C4`), low-pass filtered by $1\text{ k}\Omega$ (`R11`) / $10\text{ nF}$ (`C5`), and shunted by $10\text{ k}\Omega$ (`R12`) into `AUDIO_RAW_L` for real-time azimuth alignment and VU-meter bargraph display.

### C. Motor Remote Control (`ORIC_REM_B` — Pin 1 DIN)
- **Oric Motor Switching**: Controlled by the 6522 VIA port bit `PB3`. When active (motor running), the internal transistor switches Pin 1 to ground (`GND`). When inactive, Pin 1 is high-impedance.
- **Tape Master Sensing & Control**:
  - Pull-up $10\text{ k}\Omega$ (`R3`) to +5V, divider $2.2\text{ k}\Omega / 3.3\text{ k}\Omega$ (`R4`, `R5`), and Schottky clamp **BAT54S** (`D2`) into `MOTOR_SENSE`.
  - Low-$R_{DS(on)}$ N-channel MOSFET **2N7002** (`Q1`) driven by `MOTOR_CTRL` via $100\ \Omega$ gate resistor (`R13`) and $100\text{ k}\Omega$ pulldown (`R14`), allowing bench exerciser simulation and automated recorder control.

---

## 4. Connectors
1. **`J2` (TAPE Port)**: DIN 7-Pin 270° female socket (CUI / Same Sky `SDS-70J` horizontal):
   - Pin 1: `REM` (`ORIC_REM_B` / Motor control)
   - Pin 2: `GND` (Ground return and shield)
   - Pin 3: `IN` (`ORIC_READ` / TAPE IN from tape EAR)
   - Pin 4: `OUT` (`ORIC_WRITE` / TAPE OUT to tape MIC)
   - Pin 5: `OUT` (`ORIC_WRITE` / Auxiliary sound output tied in parallel)
   - Pin 6: `NC`
   - Pin 7: `NC`
2. **`J3` (Bench Test Header)**: $1 \times 06$ male pin header 2.54 mm pitch:
   - Pin 1: `GND`
   - Pin 2: `+5V`
   - Pin 3: `GND`
   - Pin 4: `REM` (`ORIC_REM_B` / Motor control line)
   - Pin 5: `RD` (`ORIC_READ` / Tape In to Oric)
   - Pin 6: `WR` (`ORIC_WRITE` / Tape Out from Oric)
3. **`J1` (Tape Master Bus)**: $2 \times 20$ right-angle female header with `CART_DETECT_N` (Pin 26) tied to `GND`.
