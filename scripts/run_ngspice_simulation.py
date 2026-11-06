import os, subprocess, ctypes

# Check if ngspice.dll is available in KiCad bin
kicad_bin = r"C:\Program Files\KiCad\9.0\bin"
ngspice_dll = os.path.join(kicad_bin, "ngspice.dll")

spice_deck = """* Sallen-Key 4th-Order Bandpass Filter Simulation
* Alessio Iodice - Tape Master Exerciser

VCC 5V 0 DC 5.0
VBIAS VBIAS 0 DC 2.5
VIN IN_AC 0 DC 0 AC 1.0

* Input AC coupling to Stage 1 non-inverting pre-amp (Gain = 10 / 20dB)
C_IN IN_AC IN_OP 1uF
R_IN IN_OP VBIAS 100k

* Preamp (VCVS model for op-amp with GBW 10MHz, AOL 100k)
E_AMP1 OUT1 0 VALUE = { 2.5 + LIMIT(100000 * (V(IN_OP) - V(FB1)), -2.4, 2.4) }
* Feedback network: Gain = 1 + R_F / R_G = 1 + 9k/1k = 10
R_G FB1 VBIAS 1k
R_F OUT1 FB1 9k

* HPF Sallen-Key Stage (fc ~ 300 Hz)
* C1=C2=47nF, R1=8.2k, R2=16k referenced to VBIAS
C1_H OUT1 N_H1 47nF
C2_H N_H1 IN_HPF_P 47nF
R1_H N_H1 OUT_HPF 8.2k
R2_H IN_HPF_P VBIAS 16k
E_HPF OUT_HPF 0 VALUE = { 2.5 + LIMIT(100000 * (V(IN_HPF_P) - V(OUT_HPF)), -2.4, 2.4) }

* LPF Sallen-Key Stage (fc ~ 12 kHz)
* R1=R2=12k, C1=1.5nF, C2=680pF
R1_L OUT_HPF N_L1 12k
R2_L N_L1 IN_LPF_P 12k
C1_L N_L1 OUT_LPF 1.5nF
C2_L IN_LPF_P VBIAS 680pF
E_LPF OUT_LPF 0 VALUE = { 2.5 + LIMIT(100000 * (V(IN_LPF_P) - V(OUT_LPF)), -2.4, 2.4) }

.ac dec 20 10 100k
.print ac vdb(OUT_LPF) vp(OUT_LPF)
.end
"""

deck_file = os.path.join(os.path.dirname(__file__), "bandpass_filter.cir")
with open(deck_file, "w", encoding="utf-8") as f:
    f.write(spice_deck)

print(f"Generated SPICE netlist at: {deck_file}")
