# Tape Master v2 — Expansion Cartridge #03
## Thomson MO5 / TO7 / MO6 / TO8 / TO9 & Olivetti Prodest PC 128 Interface

---

### 1. Overview & Supported Systems
This hardware cartridge provides full bidirectional cassette emulation, high-speed acquisition, motor control sensing, and analog soundtrack digitization for the entire family of Thomson 8-bit computers and their international counterparts:
- **Thomson MO Series**: MO5, MO5E, MO5NR, MO6.
- **Thomson TO Series**: TO7, TO7/70, TO8, TO8D, TO9, TO9+.
- **Olivetti Prodest PC 128**: Licensed Italian rebadged version of the Thomson MO6.

The cartridge features:
1. **Universal 40-Pin Right-Angle Bus (`J1`)**: Perfectly coplanar to the Tape Master Mainboard.
2. **Standard 5-Pin DIN 180° Female Socket (`J2`)**: Compatible with original Thomson LEP (*Lecteur Enregistreur de Programmes*) DIN cables.
3. **Bench Test Header (`J3`)**: 6-pin 2.54 mm header in parallel with detailed silkscreen pinout labels for easy logic analyzer, oscilloscope, and bench testing.
4. **Smart Auto-ID EEPROM (`U1`)**: 24C02 on I2C bus identifying Cartridge ID `#03`.
5. **Bidirectional Signal Conditioning**:
   - `READ` (Cassette In to Computer): Buffered with 74HCT06 open-collector inverter stage with 4.7kΩ pull-up for sharp 5V TTL rise/fall times.
   - `WRITE` (Cassette Out from Computer): Scaled via 2.2kΩ / 3.3kΩ voltage divider and clamped to +3.3V/GND via high-speed Schottky diode BAT54S (`D1`).
   - `REM` (Motor Remote Control): Pull-up to +5V (10kΩ) and level scaled/clamped via BAT54S (`D2`) to feed RP2040 `MOTOR_SENSE`.
   - `AUDIO` (Soundtrack / Secondary channel): AC-coupled via 4.7µF capacitor `C3` into the auxiliary analog digitizer `AUDIO_RAW_L`.
6. **ESD TVS Array (`D3`)**: USBLC6-2SC6 protecting all externally exposed lines against electrostatic discharge.

---

### 2. Connector Pinouts

#### DIN 5-Pin 180° Female Receptacle (`J2`)
Standard DIN 41524 / IEC 60130-9 socket:

| Pin | Net Name | Function | Direction | Electrical Standard |
| :---: | :---: | :--- | :--- | :--- |
| **1** | `THOMSON_REM` | Motor Remote Control | Host $\rightarrow$ Tape Master | Open-Collector / Relay control |
| **2** | `GND` | Ground & Shield reference | Common Power Reference | 0V |
| **3** | `THOMSON_AUDIO`| Analog Audio Channel | Tape Master $\rightarrow$ Host | Analog Audio ($~1\text{V}_{pp}$) |
| **4** | `THOMSON_READ` | Cassette Data In (EAR) | Tape Master $\rightarrow$ Host | 5V TTL Digital Pulses |
| **5** | `THOMSON_WRITE`| Cassette Data Out (MIC)| Host $\rightarrow$ Tape Master | 5V TTL Digital Square Waves |

#### Bench Test Pin-Header (`J3`)
6-pin 2.54 mm right-angle pin-header:

| Pin | Net Name | Description |
| :---: | :---: | :--- |
| **1** | `GND` | Ground reference |
| **2** | `+5V` | Tape Master System +5V Supply |
| **3** | `THOMSON_REM` | Motor Remote Control Sense line |
| **4** | `THOMSON_AUDIO`| Analog Audio soundtrack ingest |
| **5** | `THOMSON_READ` | Buffered 5V Cassette Data In to Host |
| **6** | `THOMSON_WRITE`| Scaled Cassette Data Out from Host |

---

### 3. Production Deliverables Summary

| Artifact | File Name | Description |
| :--- | :--- | :--- |
| **Schematic (PDF)** | `Tape_Master_Cartridge_Thomson_PC128.pdf` | Complete single-sheet schematic with standard page settings |
| **Schematic (SVG)** | `Tape_Master_Cartridge_Thomson_PC128_Sch.svg` | Vector schematic graphic |
| **3D CAD Model (STEP)**| `Tape_Master_Cartridge_Thomson_PC128.step` | Full 3D solid mechanical model |
| **PCB Layout (Top PDF)**| `Tape_Master_Cartridge_Thomson_PC128_Top.pdf` | Vector drawing of Top Copper, Silk, Mask & Edge.Cuts |
| **PCB Layout (Bottom PDF)**| `Tape_Master_Cartridge_Thomson_PC128_Bottom.pdf` | Vector drawing of Bottom Copper, Silk, Mask & Edge.Cuts |
| **PCB Layout (Top SVG)**| `Tape_Master_Cartridge_Thomson_PC128_Top.svg` | Vector layout graphic |
| **Gerber & Drill Files** | `gerbers/` (26 files) | Standard RS-274X Gerbers and Excellon drill files |
| **ERC Report** | `Tape_Master_Cartridge_Thomson_PC128-erc.rpt` | **0 Violations / 0 Warnings** |
| **DRC Report** | `Tape_Master_Cartridge_Thomson_PC128-drc.rpt` | **0 Violations / 0 Unconnected / 0 Parity Issues** |

---

### 4. Verification & Validation Gate
- **KiCad 9.0 CLI ERC**: Passed with **0 errors, 0 warnings**.
- **KiCad 9.0 CLI DRC**: Passed with **0 violations, 0 unconnected items, 0 schematic parity issues**.
- **Compliance Rules**:
  - Mechanical profile $74.00\text{ mm} \times 55.00\text{ mm}$ with $6.00\text{ mm} \times 8.00\text{ mm}$ retention cutouts on `Edge.Cuts`.
  - Zero redundant activity LEDs on cartridge; full UI diagnostics central on Daughterboard.
  - Cartouche with Alessio Iodice, CC BY-NC-SA 4.0 license, and `© 2026 by Alessio Iodice` silkscreen copyright.
