import os, sys
from test_all_resolved import resolve_symbol
from sch_builder import SchematicBuilder

kicad_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kicad"))
os.makedirs(kicad_dir, exist_ok=True)

root_uuid = "a1000000-0000-4000-8000-000000000000"
s1_uuid   = "a1000000-0000-4000-8000-000000000001"
s2_uuid   = "a1000000-0000-4000-8000-000000000002"
s3_uuid   = "a1000000-0000-4000-8000-000000000003"
s4_uuid   = "a1000000-0000-4000-8000-000000000004"

# ==============================================================================
# ROOT SHEET
# ==============================================================================
root = SchematicBuilder(root_uuid, root_uuid, 
    "Tape Master Exerciser & Signal Digitizer - System Architecture",
    "Modular Vintage Tape Deck Exerciser, Azimuth Tuning & Signal Digitizer")

root.add_subsheet("01_Power_Supply", "01_Power_Supply.kicad_sch", s1_uuid, 40.0, 45.0, 80.0, 45.0, 2)
root.add_subsheet("02_MCU_Core", "02_MCU_Core.kicad_sch", s2_uuid, 145.0, 45.0, 95.0, 65.0, 3)
root.add_subsheet("03_Analog_Ingest", "03_Analog_Ingest.kicad_sch", s3_uuid, 40.0, 115.0, 80.0, 60.0, 4)
root.add_subsheet("04_Tape_Interfaces", "04_Tape_Interfaces.kicad_sch", s4_uuid, 145.0, 130.0, 95.0, 45.0, 5)

with open(os.path.join(kicad_dir, "Tape-Master.kicad_sch"), "w", encoding="utf-8") as f:
    f.write(root.render(resolve_symbol))

# ==============================================================================
# SHEET 1: 01_Power_Supply.kicad_sch
# ==============================================================================
s1 = SchematicBuilder(s1_uuid, root_uuid,
    "Power Supply & Precision Bias Reference Subsystem",
    "USB-C / C2N +5V Dual Input, 3.3V Ultra-Low-Noise LDO & 2.5V Stiff Analog VBIAS")

# J1 USB-C (at 40, 60)
s1.add_symbol("Connector", "USB_C_Receptacle_USB2.0_16P", "J1", "USB-C", 
    "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal", 40.0, 60.0)

# VBUS pins (55.24, 75.24) -> wire to (65.0, 75.24)
s1.add_wire(55.24, 75.24, 65.0, 75.24)

# F1 Polyfuse (at 75.0, 75.24, rot=90)
s1.add_symbol("Device", "Polyfuse", "F1", "PTC 1A", "Fuse:Fuse_1206_3216Metric", 75.0, 75.24, rot=90)
s1.add_wire(65.0, 75.24, 71.19, 75.24) # to F1 pin 1
s1.add_wire(78.81, 75.24, 85.0, 75.24) # from F1 pin 2 to D1 pin 1
s1.add_wire(85.0, 75.24, 85.0, 82.46)
s1.add_wire(85.0, 82.46, 88.0, 82.46)

# C2N 5V input selection: JP1 Conn_01x02 at (70.0, 100.0)
s1.add_symbol("Connector_Generic", "Conn_01x02", "JP1", "C2N_PWR_SEL", 
    "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", 70.0, 100.0)
s1.add_wire(64.92, 100.0, 55.0, 100.0)
s1.add_global_label("C2N_5V_IN", 55.0, 100.0, rot=180, shape="input")
s1.add_wire(64.92, 97.46, 85.0, 97.46)
s1.add_wire(85.0, 97.46, 85.0, 87.54)
s1.add_wire(85.0, 87.54, 88.0, 87.54) # to D1 pin 2

# D1 Dual Schottky BAT54C (at 95.0, 85.0)
s1.add_symbol("Device", "D_Schottky_Dual_CommonCathode_AAK", "D1", "BAT54C", 
    "Package_TO_SOT_SMD:SOT-23", 95.0, 85.0)
# Pin 3 is cathode at (102.62, 85.0) -> main +5V
s1.add_wire(102.62, 85.0, 115.0, 85.0)
s1.add_pwr("+5V", 115.0, 85.0)
s1.add_pwr_flag(115.0, 85.0)

# CC resistors for USB-C
# CC1 (55.24, 70.16) -> R1 (5.1k) at (65.0, 70.16, rot=90) -> GND
s1.add_symbol("Device", "R", "R1", "5.1k", "Resistor_SMD:R_0805_2012Metric", 65.0, 70.16, rot=90)
s1.add_wire(55.24, 70.16, 61.19, 70.16)
s1.add_wire(68.81, 70.16, 75.0, 70.16)
s1.add_pwr("GND", 75.0, 70.16)

# CC2 (55.24, 67.62) -> R2 (5.1k) at (65.0, 67.62, rot=90) -> GND
s1.add_symbol("Device", "R", "R2", "5.1k", "Resistor_SMD:R_0805_2012Metric", 65.0, 67.62, rot=90)
s1.add_wire(55.24, 67.62, 61.19, 67.62)
s1.add_wire(68.81, 67.62, 75.0, 67.62)
s1.add_pwr("GND", 75.0, 67.62)

# USB GND pins (40.0, 37.14) -> GND
s1.add_wire(40.0, 37.14, 40.0, 30.0)
s1.add_pwr("GND", 40.0, 30.0)
s1.add_pwr_flag(40.0, 30.0)

# USB Shield (32.38, 37.14) -> GND
s1.add_wire(32.38, 37.14, 32.38, 30.0)
s1.add_pwr("GND", 32.38, 30.0)

# 5V Bulk capacitors C1, C2, C3 at (130, 85), (140, 85), (150, 85)
for i, (val, ref, fp) in enumerate([("100uF", "C1", "Capacitor_Tantalum_SMD:CP_EIA-3528-21_Kemet-B"), 
                                    ("10uF", "C2", "Capacitor_SMD:C_0805_2012Metric"), 
                                    ("100nF", "C3", "Capacitor_SMD:C_0805_2012Metric")]):
    cx = 125.0 + i * 12.0
    s1.add_symbol("Device", "C_Polarized" if "uF" in val and "100" in val else "C", ref, val, fp, cx, 95.0)
    s1.add_wire(cx, 91.19, cx, 85.0)
    s1.add_pwr("+5V", cx, 85.0)
    s1.add_wire(cx, 98.81, cx, 105.0)
    s1.add_pwr("GND", cx, 105.0)

# 3.3V LDO U1 (AP2112K-3.3) at (180.0, 85.0)
s1.add_symbol("Regulator_Linear", "AP2112K-3.3", "U1", "AP2112K-3.3", 
    "Package_TO_SOT_SMD:SOT-23-5", 180.0, 85.0)
# Pin 1 VIN (172.38, 87.54) -> +5V
s1.add_wire(172.38, 87.54, 165.0, 87.54)
s1.add_pwr("+5V", 165.0, 87.54)
# Pin 3 EN (172.38, 82.46) -> +5V
s1.add_wire(172.38, 82.46, 165.0, 82.46)
s1.add_pwr("+5V", 165.0, 82.46)
# Pin 2 GND (180.0, 95.16) -> GND
s1.add_wire(180.0, 95.16, 180.0, 102.0)
s1.add_pwr("GND", 180.0, 102.0)
# Pin 5 VOUT (187.62, 87.54) -> +3V3
s1.add_wire(187.62, 87.54, 195.0, 87.54)
s1.add_pwr("+3V3", 195.0, 87.54)
s1.add_pwr_flag(195.0, 87.54)

# 3.3V Filtering C5 (2.2uF), C6 (100nF) at (205, 95), (215, 95)
for i, (val, ref) in enumerate([("2.2uF", "C5"), ("100nF", "C6")]):
    cx = 205.0 + i * 12.0
    s1.add_symbol("Device", "C", ref, val, "Capacitor_SMD:C_0805_2012Metric", cx, 95.0)
    s1.add_wire(cx, 91.19, cx, 87.54)
    s1.add_pwr("+3V3", cx, 87.54)
    s1.add_wire(cx, 98.81, cx, 105.0)
    s1.add_pwr("GND", cx, 105.0)

# Input bypass cap C4 (1uF) at (172.0, 115.0)
s1.add_symbol("Device", "C", "C4", "1uF", "Capacitor_SMD:C_0805_2012Metric", 172.0, 115.0)
s1.add_wire(172.0, 111.19, 172.0, 105.0)
s1.add_pwr("+5V", 172.0, 105.0)
s1.add_wire(172.0, 118.81, 172.0, 125.0)
s1.add_pwr("GND", 172.0, 125.0)

# Precision VBIAS 2.5V Generator:
# Divider R3 (10k 0.1%), R4 (10k 0.1%) at (60.0, 150.0)
s1.add_symbol("Device", "R", "R3", "10k 0.1%", "Resistor_SMD:R_0805_2012Metric", 60.0, 140.0)
s1.add_wire(60.0, 136.19, 60.0, 130.0)
s1.add_pwr("+5V", 60.0, 130.0)
s1.add_wire(60.0, 143.81, 60.0, 151.19)

s1.add_symbol("Device", "R", "R4", "10k 0.1%", "Resistor_SMD:R_0805_2012Metric", 60.0, 155.0)
s1.add_wire(60.0, 158.81, 60.0, 165.0)
s1.add_pwr("GND", 60.0, 165.0)

# VBIAS divider filtering: C7 (47uF Tantalum), C8 (100nF) at (72, 150), (84, 150)
s1.add_symbol("Device", "C_Polarized", "C7", "47uF", "Capacitor_Tantalum_SMD:CP_EIA-3528-21_Kemet-B", 72.0, 150.0)
s1.add_wire(72.0, 146.19, 72.0, 147.5)
s1.add_wire(60.0, 147.5, 72.0, 147.5)
s1.add_wire(72.0, 153.81, 72.0, 165.0)
s1.add_pwr("GND", 72.0, 165.0)

s1.add_symbol("Device", "C", "C8", "100nF", "Capacitor_SMD:C_0805_2012Metric", 84.0, 150.0)
s1.add_wire(84.0, 146.19, 84.0, 147.5)
s1.add_wire(72.0, 147.5, 84.0, 147.5)
s1.add_wire(84.0, 153.81, 84.0, 165.0)
s1.add_pwr("GND", 84.0, 165.0)

# U2 NE5532 Unit 1 (buffer for VBIAS) at (110.0, 150.0)
s1.add_symbol("Amplifier_Operational", "NE5532", "U2", "NE5532", 
    "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 110.0, 150.0, unit=1)
# Pin 3 (+) is at (102.38, 147.46) -> wire to VBIAS divider
s1.add_wire(102.38, 147.46, 84.0, 147.46)
s1.add_wire(84.0, 147.46, 84.0, 147.5)
# Pin 2 (-) is at (102.38, 152.54) -> wire to Pin 1 output at (117.62, 150.0)
s1.add_wire(102.38, 152.54, 98.0, 152.54)
s1.add_wire(98.0, 152.54, 98.0, 158.0)
s1.add_wire(98.0, 158.0, 122.0, 158.0)
s1.add_wire(122.0, 158.0, 122.0, 150.0)
s1.add_wire(117.62, 150.0, 122.0, 150.0)

# Output is VBIAS (122.0, 150.0) -> global net VBIAS
s1.add_wire(122.0, 150.0, 135.0, 150.0)
s1.add_global_label("VBIAS", 135.0, 150.0, rot=0, shape="output")
s1.add_pwr_flag(135.0, 150.0)

# VBIAS output decoupling C9 (10uF), C10 (100nF) at (145, 150), (155, 150)
for i, (val, ref) in enumerate([("10uF", "C9"), ("100nF", "C10")]):
    cx = 145.0 + i * 12.0
    s1.add_symbol("Device", "C", ref, val, "Capacitor_SMD:C_0805_2012Metric", cx, 155.0)
    s1.add_wire(cx, 151.19, cx, 150.0)
    s1.add_wire(cx, 150.0, 135.0, 150.0)
    s1.add_wire(cx, 158.81, cx, 165.0)
    s1.add_pwr("GND", cx, 165.0)

# U2 Power pins Unit 3 at (110.0, 180.0)
s1.add_symbol("Amplifier_Operational", "NE5532", "U2", "NE5532", 
    "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 110.0, 180.0, unit=3)
# Pin 8 V+ at (107.46, 172.38) -> +5V
s1.add_wire(107.46, 172.38, 107.46, 168.0)
s1.add_pwr("+5V", 107.46, 168.0)
# Pin 4 V- at (107.46, 187.62) -> GND
s1.add_wire(107.46, 187.62, 107.46, 192.0)
s1.add_pwr("GND", 107.46, 192.0)

# Decoupling C11 (100nF) at (120.0, 180.0)
s1.add_symbol("Device", "C", "C11", "100nF", "Capacitor_SMD:C_0805_2012Metric", 120.0, 180.0)
s1.add_wire(120.0, 176.19, 120.0, 168.0)
s1.add_pwr("+5V", 120.0, 168.0)
s1.add_wire(120.0, 183.81, 120.0, 192.0)
s1.add_pwr("GND", 120.0, 192.0)

with open(os.path.join(kicad_dir, "01_Power_Supply.kicad_sch"), "w", encoding="utf-8") as f:
    f.write(s1.render(resolve_symbol))

print("Sheet 1 generated.")
