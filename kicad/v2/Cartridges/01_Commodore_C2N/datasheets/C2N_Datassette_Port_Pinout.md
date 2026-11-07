# DATASHEET SPECIFICATION: C2N CASSETTE PORT INTERFACE & COMMODORE TAPE PROTOCOL
**Reference**: Commodore PET / VIC-20 / C64 / C128 Cassette Interface Specification  
**Connector Type**: 6-Position (12-contact dual-sided) 0.156" (3.96 mm) Edge Card Connector with key notch between pin 2 and 3  

## 1. Pinout & Electrical Characteristics

| Pin | Name | Direction | Voltage / Levels | Description |
| :---: | :--- | :---: | :---: | :--- |
| **A-1 / B-1** | `GND` | Power | 0 V | System Ground Reference |
| **A-2 / B-2** | `+5V` | Power Out / In | +5.0 V ± 5% (up to 500 mA) | C64 internal +5V logic supply. Can supply board or be fed. |
| **A-3 / B-3** | `MOTOR` | Input from Host | +5V (stopped) / ~0.3V (running) | Controlled by C64 internal PNP pass transistor (typically 2N3906 or BD136). Active LOW switches tape motor ON. |
| **A-4 / B-4** | `READ` | Output to Host | 5V TTL (Open-Collector) | Negative-going logic pulses from tape deck to CIA 6526 (FLAG pin, active edge falling). Must be Open-Collector driver. |
| **A-5 / B-5** | `WRITE` | Input from Host | 5V TTL | Serial PWM pulses from CIA 6526 (PB3 / PB4) during SAVE operation. High ~4.5V, Low ~0.2V. |
| **A-6 / B-6** | `SENSE` | Output to Host | Active Low (GND) | Switch contact in tape deck closed when PLAY, RECORD, F.FWD, or REW is pressed. Pulled up to +5V inside host. |

---

## 2. Timing Protocol (Commodore TAP Encoding)
Commodore tape encoding represents data as time intervals between successive falling edges on the `READ` line:
* **Short Pulse (S)**: $352\text{ }\mu\text{s}$ (Bit 0 half-wave)
* **Medium Pulse (M)**: $512\text{ }\mu\text{s}$ (Bit 1 half-wave / sync marker)
* **Long Pulse (L)**: $672\text{ }\mu\text{s}$ (Byte boundary marker)

Bit encoding is pulse-pair encoded:
* Bit `0`: Short followed by Medium (S + M = $864\text{ }\mu\text{s}$)
* Bit `1`: Medium followed by Short (M + S = $864\text{ }\mu\text{s}$)
* Byte Sync / Marker: Long followed by Medium (L + M) or (L + S).

The RP2040 PIO state machine generates these exact timings with < 10 ns jitter.
