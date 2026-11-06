import os
from smart_sch_builder import SmartSchematic

kicad_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kicad"))
root_uuid = "a1000000-0000-4000-8000-000000000000"
s1_uuid   = "a1000000-0000-4000-8000-000000000001"

s1 = SmartSchematic(s1_uuid, root_uuid,
    "Power Supply & Precision Bias Reference Subsystem",
    "USB-C / C2N +5V Dual Input, 3.3V Ultra-Low-Noise LDO & 2.5V Stiff Analog VBIAS")

# J1 USB-C
s1.add_component("J1", "Connector", "USB_C_Receptacle_USB2.0_16P", "USB-C",
    "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal", 40.0, 60.0)

# Connect USB CC pins to 5.1k resistors
s1.add_component("R1", "Device", "R", "5.1k", "Resistor_SMD:R_0805_2012Metric", 70.0, 50.0, rot=90)
s1.connect_pins("J1", "A5", "R1", "1")
s1.connect_pin_stub("R1", "2", "GND", is_pwr=True)

s1.add_component("R2", "Device", "R", "5.1k", "Resistor_SMD:R_0805_2012Metric", 70.0, 56.0, rot=90)
s1.connect_pins("J1", "B5", "R2", "1")
s1.connect_pin_stub("R2", "2", "GND", is_pwr=True)

# USB GND and Shield to GND
s1.connect_pin_stub("J1", "A1", "GND", is_pwr=True)
s1.connect_pin_stub("J1", "S1", "GND", is_pwr=True)
s1.connect_pin_stub("J1", "A12", "GND", is_pwr=True)
s1.connect_pin_stub("J1", "B1", "GND", is_pwr=True)
s1.connect_pin_stub("J1", "B12", "GND", is_pwr=True)

# Unused USB pins -> no_connect
for p in ["A6", "A7", "A8", "B6", "B7", "B8"]:
    s1.add_no_connect("J1", p)

# F1 Polyfuse in series with VBUS
s1.add_component("F1", "Device", "Polyfuse", "PTC 1A", "Fuse:Fuse_1206_3216Metric", 70.0, 44.76, rot=90)
s1.connect_pins("J1", "A4", "F1", "1")
s1.connect_pins("J1", "B4", "F1", "1")
s1.connect_pins("J1", "A9", "F1", "1")
s1.connect_pins("J1", "B9", "F1", "1")

# C2N Power selection JP1
s1.add_component("JP1", "Connector_Generic", "Conn_01x02", "C2N_PWR_SEL",
    "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", 70.0, 75.0)
s1.connect_pin_stub("JP1", "1", "C2N_5V_IN", is_global=True, shape="input")

# D1 Dual Schottky BAT54C (Cathode Pin 3 is +5V)
s1.add_component("D1", "Device", "D_Schottky_Dual_CommonCathode_AAK", "BAT54C",
    "Package_TO_SOT_SMD:SOT-23", 95.0, 60.0)
s1.connect_pins("F1", "2", "D1", "1")
s1.connect_pins("JP1", "2", "D1", "2")
p3_x, p3_y = s1.connect_pin_stub("D1", "3", "+5V", is_pwr=True)
# Connect PWR_FLAG to this exact +5V node
s1.add_pwr_flag(p3_x, p3_y)

# Also connect PWR_FLAG to GND
s1.add_pwr_flag(40.0, 87.94)

# Bulk caps C1, C2, C3
for i, (val, ref, fp) in enumerate([("100uF", "C1", "Capacitor_Tantalum_SMD:CP_EIA-3528-21_Kemet-B"), 
                                    ("10uF", "C2", "Capacitor_SMD:C_0805_2012Metric"), 
                                    ("100nF", "C3", "Capacitor_SMD:C_0805_2012Metric")]):
    cx = 115.0 + i * 12.0
    s1.add_component(ref, "Device", "C_Polarized" if "100" in val else "C", val, fp, cx, 60.0)
    s1.connect_pin_stub(ref, "1", "+5V", is_pwr=True)
    s1.connect_pin_stub(ref, "2", "GND", is_pwr=True)

# U1 AP2112K-3.3 LDO
s1.add_component("U1", "Regulator_Linear", "AP2112K-3.3", "AP2112K-3.3",
    "Package_TO_SOT_SMD:SOT-23-5", 160.0, 60.0)
s1.connect_pin_stub("U1", "1", "+5V", is_pwr=True)
s1.connect_pin_stub("U1", "3", "+5V", is_pwr=True)
s1.connect_pin_stub("U1", "2", "GND", is_pwr=True)
vout_x, vout_y = s1.connect_pin_stub("U1", "5", "+3V3", is_pwr=True)
s1.add_pwr_flag(vout_x, vout_y)
s1.add_no_connect("U1", "4")

# LDO caps
s1.add_component("C4", "Device", "C", "1uF", "Capacitor_SMD:C_0805_2012Metric", 150.0, 75.0)
s1.connect_pin_stub("C4", "1", "+5V", is_pwr=True)
s1.connect_pin_stub("C4", "2", "GND", is_pwr=True)

for i, (val, ref) in enumerate([("2.2uF", "C5"), ("100nF", "C6")]):
    cx = 175.0 + i * 12.0
    s1.add_component(ref, "Device", "C", val, "Capacitor_SMD:C_0805_2012Metric", cx, 75.0)
    s1.connect_pin_stub(ref, "1", "+3V3", is_pwr=True)
    s1.connect_pin_stub(ref, "2", "GND", is_pwr=True)

# VBIAS precision divider R3, R4
s1.add_component("R3", "Device", "R", "10k 0.1%", "Resistor_SMD:R_0805_2012Metric", 50.0, 110.0)
s1.connect_pin_stub("R3", "1", "+5V", is_pwr=True)

s1.add_component("R4", "Device", "R", "10k 0.1%", "Resistor_SMD:R_0805_2012Metric", 50.0, 125.0)
s1.connect_pin_stub("R4", "2", "GND", is_pwr=True)
s1.connect_pins("R3", "2", "R4", "1")

# VBIAS filter caps C7, C8
s1.add_component("C7", "Device", "C_Polarized", "47uF", "Capacitor_Tantalum_SMD:CP_EIA-3528-21_Kemet-B", 65.0, 120.0)
s1.connect_pins("R4", "1", "C7", "1")
s1.connect_pin_stub("C7", "2", "GND", is_pwr=True)

s1.add_component("C8", "Device", "C", "100nF", "Capacitor_SMD:C_0805_2012Metric", 77.0, 120.0)
s1.connect_pins("C7", "1", "C8", "1")
s1.connect_pin_stub("C8", "2", "GND", is_pwr=True)

# U2 NE5532 Unit 1 follower
s1.add_component("U2", "Amplifier_Operational", "NE5532", "NE5532",
    "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 100.0, 120.0, unit=1)
s1.connect_pins("C8", "1", "U2", "3", u2=1)
s1.connect_pins("U2", "2", "U2", "1", u1=1, u2=1)
vb_x, vb_y = s1.connect_pin_stub("U2", "1", "VBIAS", is_global=True, shape="output", unit=1)
s1.add_pwr_flag(vb_x, vb_y)

# Decoupling for VBIAS output
s1.add_component("C9", "Device", "C", "10uF", "Capacitor_SMD:C_0805_2012Metric", 125.0, 120.0)
s1.connect_pin_stub("C9", "1", "VBIAS", is_global=True, shape="input")
s1.connect_pin_stub("C9", "2", "GND", is_pwr=True)

s1.add_component("C10", "Device", "C", "100nF", "Capacitor_SMD:C_0805_2012Metric", 137.0, 120.0)
s1.connect_pin_stub("C10", "1", "VBIAS", is_global=True, shape="input")
s1.connect_pin_stub("C10", "2", "GND", is_pwr=True)

# U2 NE5532 Unit 2 (unused unit properly configured as follower to VBIAS to prevent oscillation)
s1.add_component("U2", "Amplifier_Operational", "NE5532", "NE5532",
    "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 100.0, 140.0, unit=2)
s1.connect_pin_stub("U2", "5", "VBIAS", is_global=True, shape="input", unit=2)
s1.connect_pins("U2", "6", "U2", "7", u1=2, u2=2)

# U2 Unit 3 power
s1.add_component("U2", "Amplifier_Operational", "NE5532", "NE5532",
    "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 100.0, 160.0, unit=3)
s1.connect_pin_stub("U2", "8", "+5V", is_pwr=True, unit=3)
s1.connect_pin_stub("U2", "4", "GND", is_pwr=True, unit=3)

s1.add_component("C11", "Device", "C", "100nF", "Capacitor_SMD:C_0805_2012Metric", 115.0, 160.0)
s1.connect_pin_stub("C11", "1", "+5V", is_pwr=True)
s1.connect_pin_stub("C11", "2", "GND", is_pwr=True)

with open(os.path.join(kicad_dir, "01_Power_Supply.kicad_sch"), "w", encoding="utf-8") as f:
    f.write(s1.render())

print("Refined Sheet 1 generated.")
