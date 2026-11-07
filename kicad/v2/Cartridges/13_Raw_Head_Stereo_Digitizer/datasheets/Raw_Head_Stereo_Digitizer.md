# Raw Head Probing & Stereo Digitizer Specification
**Tape Master Exerciser & Signal Digitizer v2 — Cartridge #13 (Lab Instrument)**

**Author / Hardware Designer**: Alessio Iodice (`alessio67@gmail.com`)  
**Context**: MuDIsTInf (Museo Didattico di Storia dell'Informatica Padova) — Laboratorio di Restauro Magnetico  
**Target Hardware**: Degraded Vintage Cassettes, Sticky-Shed Syndrome, De-Azimuth Tape Restoration  
**License**: CC BY-NC-SA 4.0  

---

## 1. Technical Rationale & Restoration Physics

During historical tape preservation at computer museums and archives, attempting to read 40-year-old magnetic cassettes through standard consumer vintage tape recorders almost invariably fails due to three compounding failure modes:
1. **Mechanical Azimuth Tilt ($\theta_{error}$)**:
   The recording azimuth angle of the original mastering deck rarely matches the playback head angle. At high frequencies, even an angular tilt of $\Delta \theta \approx 0.1^\circ$ induces destructive phase interference across the $0.6\text{ mm}$ track width, severely rolling off signals above $4\text{ kHz}$ according to the gap loss formula:
   $$\text{Loss}_\text{azimuth} = 20 \log_{10} \left| \frac{\sin\left(\frac{\pi W \tan \theta}{\lambda}\right)}{\frac{\pi W \tan \theta}{\lambda}} \right|$$
2. **Electronic Non-Linear Slicing**:
   Original deck electronics (e.g. Commodore C2N op-amp/comparator or Sinclair ULA) apply severe hard clipping or fixed hysteresis threshold slicing. If the signal is weak ($< 100\text{ mV}$) or degraded, the slicing destroys the weak zero-crossing transitions.
3. **Internal Noise & Head Loading**:
   Vintage playback electronics introduce mains hum ($50/60\text{ Hz}$), motor RF noise, and electrolytic capacitor distortion.

### The Solution: Direct Head Ingest
By opening the cassette transport and probing the **raw magnetic head pins directly** (bypassing all internal deck circuitry):
- The head delivers a pure, uncolored magnetic flux derivative signal ($V = -N \frac{d\Phi}{dt} \approx 1 \dots 2\text{ mV}_\text{rms}$).
- **Cartridge #13** provides configurable $R/C$ loading, ultra-low-noise amplification ($+40\text{ dB} \dots +60\text{ dB}$), and routes the calibrated analog waveforms to `AUDIO_RAW_L` and `AUDIO_RAW_R` on the Tape Master bus.
- The front-panel **10-LED Bargraph (`AZIMUTH / VU-METER`)** acts as an optical peak indicator: as the restorer turns the azimuth screw on the cassette mechanism, the LED bar peaks exactly at the point of maximum high-frequency alignment, ensuring a 100% faithful digital archive transfer.

---

## 2. Electrical Architecture & Load Matrix

### A. Selectable Load & Resonance Tuning (DIP-Switch `SW1` / `SW2`)
A cassette tape head possesses an inherent inductance ($L_\text{head} \approx 100 \dots 200\text{ mH}$) and winding resistance ($R_\text{dc} \approx 200 \dots 400\ \Omega$).
Together with the input load capacitance, it forms a parallel resonant tank:
$$f_\text{resonance} = \frac{1}{2\pi \sqrt{L_\text{head} \cdot C_\text{load}}}$$

By tuning the resonance peak to the critical frequency band ($8 \dots 14\text{ kHz}$), weak harmonic energy is naturally boosted before amplification:

| DIP Switch Pole | Component Value | Function & Tuning Profile |
| :---: | :---: | :--- |
| **Pole 1** | $47\text{ k}\Omega$ Shunt | Standard NAB/IEC magnetic tape loading |
| **Pole 2** | $100\text{ k}\Omega$ Shunt | Extended high-frequency bandwidth mode (light damping) |
| **Pole 3** | $100\text{ pF}$ Shunt | Shifts resonance peak toward $\approx 14\text{ kHz}$ |
| **Pole 4** | $220\text{ pF}$ Shunt | Shifts resonance peak toward $\approx 10\text{ kHz}$ |
| **Poles 3 & 4 ON** | $320\text{ pF}$ Shunt | Deep resonance tuning for low-inductance heads ($\approx 8\text{ kHz}$) |
| **All OFF** | $1\text{ M}\Omega$ / $\approx 20\text{ pF}$ | Ultra-High-Z flat buffer mode |

### B. Ultra-Low-Noise Dual Instrumentation Preamplifier (`U2` TLV2372 / OPA2134)
- **Topolgy**: AC-coupled non-inverting dual operational amplifier.
- **Bandwidth**: Flat from $20\text{ Hz}$ to $34\text{ kHz}$ (subsonic high-pass filter blocks DC and motor rumble; active feedback low-pass capacitor $47\text{ pF}$ suppresses RF interference).
- **Gain**: Nominal $\times 100$ ($+40\text{ dB}$), elevating $1\text{ mV}_\text{rms}$ head voltage to $100\text{ mV}_\text{rms}$ / $\approx 1.5\text{ V}_\text{pp}$ dynamic range.
- **Virtual Ground Bias**: Precision low-noise $+2.5\text{V}$ reference generator decoupled with $10\ \mu\text{F}$ tantalum and $100\text{ nF}$ ceramic.

---

## 3. Physical Connectivity & Bench Header

1. **`J2` — 4-Position Screw Terminal Block (Phoenix MPT 0,5/4-2,54)**:
   - Pin 1: `HEAD_L+` (Left track / Main audio)
   - Pin 2: `HEAD_L-` (Left shield / `AGND`)
   - Pin 3: `HEAD_R+` (Right track / Secondary / Stereo)
   - Pin 4: `HEAD_R-` (Right shield / `AGND`)
2. **`J3` & `J4` — Dual 3.5 mm TRS Coaxial Jack (CUI SJ-3523-SMT)**:
   - For coaxial shielded cables from external preamplifiers or line-level test gear.
3. **`J5` — 1x06 Bench Probing Header (2.54 mm)**:
   - Pin 1: `AGND`
   - Pin 2: `L_RAW` (Direct raw head Left)
   - Pin 3: `L_AMP` (Amplified output Left)
   - Pin 4: `R_RAW` (Direct raw head Right)
   - Pin 5: `R_AMP` (Amplified output Right)
   - Pin 6: `+5V_ANA` (Filtered analog power)

---

## 4. Smart Plug & Play

- **EEPROM I2C 24C02 (`U1`)**: Programmed with ID `0x0C` (Profile: `LAB_RAW_HEAD_STEREO_INGEST`).
- **Cartridge Detect**: Pin 26 `CART_DETECT_N` grounded to automatically trigger azimuth VU-meter mode on the Tape Master UI Panel.
