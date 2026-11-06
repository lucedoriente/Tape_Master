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
# 0. ROOT SHEET
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
# 1. SHEET 1: 01_Power_Supply.kicad_sch
# ==============================================================================
s1 = SchematicBuilder(s1_uuid, root_uuid,
    "Power Supply & Precision Bias Reference Subsystem",
    "USB-C / C2N +5V Dual Input, 3.3V Ultra-Low-Noise LDO & 2.5V Stiff Analog VBIAS")

# J1 USB-C
s1.add_symbol("Connector", "USB_C_Receptacle_USB2.0_16P", "J1", "USB-C", 
    "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal", 40.0, 60.0)
s1.add_wire(55.24, 75.24, 65.0, 75.24)
s1.add_symbol("Device", "Polyfuse", "F1", "PTC 1A", "Fuse:Fuse_1206_3216Metric", 75.0, 75.24, rot=90)
s1.add_wire(65.0, 75.24, 71.19, 75.24)
s1.add_wire(78.81, 75.24, 85.0, 75.24)
s1.add_wire(85.0, 75.24, 85.0, 82.46)
s1.add_wire(85.0, 82.46, 87.38, 82.46)

# JP1 C2N Power Select
s1.add_symbol("Connector_Generic", "Conn_01x02", "JP1", "C2N_PWR_SEL", 
    "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", 70.0, 100.0)
s1.add_wire(64.92, 100.0, 55.0, 100.0)
s1.add_global_label("C2N_5V_IN", 55.0, 100.0, rot=180, shape="input")
s1.add_wire(64.92, 97.46, 85.0, 97.46)
s1.add_wire(85.0, 97.46, 85.0, 87.54)
s1.add_wire(85.0, 87.54, 87.38, 87.54)

# D1 Dual Schottky BAT54C
s1.add_symbol("Device", "D_Schottky_Dual_CommonCathode_AAK", "D1", "BAT54C", 
    "Package_TO_SOT_SMD:SOT-23", 95.0, 85.0)
s1.add_wire(102.62, 85.0, 115.0, 85.0)
s1.add_pwr("+5V", 115.0, 85.0)
s1.add_pwr_flag(115.0, 85.0)

# CC resistors
s1.add_symbol("Device", "R", "R1", "5.1k", "Resistor_SMD:R_0805_2012Metric", 65.0, 70.16, rot=90)
s1.add_wire(55.24, 70.16, 61.19, 70.16)
s1.add_wire(68.81, 70.16, 75.0, 70.16)
s1.add_pwr("GND", 75.0, 70.16)

s1.add_symbol("Device", "R", "R2", "5.1k", "Resistor_SMD:R_0805_2012Metric", 65.0, 67.62, rot=90)
s1.add_wire(55.24, 67.62, 61.19, 67.62)
s1.add_wire(68.81, 67.62, 75.0, 67.62)
s1.add_pwr("GND", 75.0, 67.62)

s1.add_wire(40.0, 37.14, 40.0, 30.0)
s1.add_pwr("GND", 40.0, 30.0)
s1.add_pwr_flag(40.0, 30.0)

s1.add_wire(32.38, 37.14, 32.38, 30.0)
s1.add_pwr("GND", 32.38, 30.0)

# 5V Bulk capacitors C1, C2, C3
for i, (val, ref, fp) in enumerate([("100uF", "C1", "Capacitor_Tantalum_SMD:CP_EIA-3528-21_Kemet-B"), 
                                    ("10uF", "C2", "Capacitor_SMD:C_0805_2012Metric"), 
                                    ("100nF", "C3", "Capacitor_SMD:C_0805_2012Metric")]):
    cx = 125.0 + i * 12.0
    s1.add_symbol("Device", "C_Polarized" if "uF" in val and "100" in val else "C", ref, val, fp, cx, 95.0)
    s1.add_wire(cx, 91.19, cx, 85.0)
    s1.add_pwr("+5V", cx, 85.0)
    s1.add_wire(cx, 98.81, cx, 105.0)
    s1.add_pwr("GND", cx, 105.0)

# U1 AP2112K-3.3 LDO
s1.add_symbol("Regulator_Linear", "AP2112K-3.3", "U1", "AP2112K-3.3", 
    "Package_TO_SOT_SMD:SOT-23-5", 180.0, 85.0)
s1.add_wire(172.38, 87.54, 165.0, 87.54)
s1.add_pwr("+5V", 165.0, 87.54)
s1.add_wire(172.38, 82.46, 165.0, 82.46)
s1.add_pwr("+5V", 165.0, 82.46)
s1.add_wire(180.0, 95.16, 180.0, 102.0)
s1.add_pwr("GND", 180.0, 102.0)
s1.add_wire(187.62, 87.54, 195.0, 87.54)
s1.add_pwr("+3V3", 195.0, 87.54)
s1.add_pwr_flag(195.0, 87.54)

# 3.3V Filtering C5, C6
for i, (val, ref) in enumerate([("2.2uF", "C5"), ("100nF", "C6")]):
    cx = 205.0 + i * 12.0
    s1.add_symbol("Device", "C", ref, val, "Capacitor_SMD:C_0805_2012Metric", cx, 95.0)
    s1.add_wire(cx, 91.19, cx, 87.54)
    s1.add_pwr("+3V3", cx, 87.54)
    s1.add_wire(cx, 98.81, cx, 105.0)
    s1.add_pwr("GND", cx, 105.0)

s1.add_symbol("Device", "C", "C4", "1uF", "Capacitor_SMD:C_0805_2012Metric", 172.0, 115.0)
s1.add_wire(172.0, 111.19, 172.0, 105.0)
s1.add_pwr("+5V", 172.0, 105.0)
s1.add_wire(172.0, 118.81, 172.0, 125.0)
s1.add_pwr("GND", 172.0, 125.0)

# Precision VBIAS 2.5V Divider & Follower U2
s1.add_symbol("Device", "R", "R3", "10k 0.1%", "Resistor_SMD:R_0805_2012Metric", 60.0, 140.0)
s1.add_wire(60.0, 136.19, 60.0, 130.0)
s1.add_pwr("+5V", 60.0, 130.0)
s1.add_wire(60.0, 143.81, 60.0, 151.19)

s1.add_symbol("Device", "R", "R4", "10k 0.1%", "Resistor_SMD:R_0805_2012Metric", 60.0, 155.0)
s1.add_wire(60.0, 158.81, 60.0, 165.0)
s1.add_pwr("GND", 60.0, 165.0)

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

# U2 Unit 1 follower
s1.add_symbol("Amplifier_Operational", "NE5532", "U2", "NE5532", 
    "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 110.0, 150.0, unit=1)
s1.add_wire(102.38, 147.46, 84.0, 147.46)
s1.add_wire(84.0, 147.46, 84.0, 147.5)
s1.add_wire(102.38, 152.54, 98.0, 152.54)
s1.add_wire(98.0, 152.54, 98.0, 158.0)
s1.add_wire(98.0, 158.0, 122.0, 158.0)
s1.add_wire(122.0, 158.0, 122.0, 150.0)
s1.add_wire(117.62, 150.0, 122.0, 150.0)

s1.add_wire(122.0, 150.0, 135.0, 150.0)
s1.add_global_label("VBIAS", 135.0, 150.0, rot=0, shape="output")
s1.add_pwr_flag(135.0, 150.0)

for i, (val, ref) in enumerate([("10uF", "C9"), ("100nF", "C10")]):
    cx = 145.0 + i * 12.0
    s1.add_symbol("Device", "C", ref, val, "Capacitor_SMD:C_0805_2012Metric", cx, 155.0)
    s1.add_wire(cx, 151.19, cx, 150.0)
    s1.add_wire(cx, 150.0, 135.0, 150.0)
    s1.add_wire(cx, 158.81, cx, 165.0)
    s1.add_pwr("GND", cx, 165.0)

# U2 Unit 3 power
s1.add_symbol("Amplifier_Operational", "NE5532", "U2", "NE5532", 
    "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 110.0, 180.0, unit=3)
s1.add_wire(107.46, 172.38, 107.46, 168.0)
s1.add_pwr("+5V", 107.46, 168.0)
s1.add_wire(107.46, 187.62, 107.46, 192.0)
s1.add_pwr("GND", 107.46, 192.0)

s1.add_symbol("Device", "C", "C11", "100nF", "Capacitor_SMD:C_0805_2012Metric", 120.0, 180.0)
s1.add_wire(120.0, 176.19, 120.0, 168.0)
s1.add_pwr("+5V", 120.0, 168.0)
s1.add_wire(120.0, 183.81, 120.0, 192.0)
s1.add_pwr("GND", 120.0, 192.0)

with open(os.path.join(kicad_dir, "01_Power_Supply.kicad_sch"), "w", encoding="utf-8") as f:
    f.write(s1.render(resolve_symbol))

# ==============================================================================
# 2. SHEET 2: 02_MCU_Core.kicad_sch
# ==============================================================================
s2 = SchematicBuilder(s2_uuid, root_uuid,
    "Microcontroller Core & User Interface",
    "Raspberry Pi Pico (RP2040), MicroSD SPI, I2C OLED 128x64, Rotary Encoder & Status LEDs")

# U3 Raspberry Pi Pico at (160.0, 120.0)
s2.add_symbol("MCU_Module", "RaspberryPi_Pico", "U3", "RaspberryPi_Pico", 
    "Module:RaspberryPi_Pico_Common_THT", 160.0, 120.0)

# Power & GND to Pico
s2.add_wire(154.92, 81.9, 154.92, 75.0) # Pin 39 VSYS
s2.add_pwr("+5V", 154.92, 75.0)
s2.add_wire(165.08, 81.9, 165.08, 75.0) # Pin 36 3V3
s2.add_pwr("+3V3", 165.08, 75.0)
s2.add_wire(160.0, 155.56, 160.0, 162.0) # Pin 3 GND
s2.add_pwr("GND", 160.0, 162.0)

# Pico RUN button (SW6) at (115.0, 97.14)
s2.add_symbol("Switch", "SW_Push", "SW6", "RESET", "Button_Switch_THT:SW_PUSH_6mm", 115.0, 97.14)
s2.add_wire(137.14, 97.14, 120.08, 97.14) # from RUN pin 30
s2.add_wire(109.92, 97.14, 102.0, 97.14)
s2.add_pwr("GND", 102.0, 97.14)

# I2C OLED Display DISP1 at (70.0, 75.0)
s2.add_symbol("Tape-Master", "OLED_0.96_I2C", "DISP1", "OLED_0.96_I2C", 
    "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", 70.0, 75.0)
s2.add_wire(61.11, 77.54, 52.0, 77.54) # GND
s2.add_pwr("GND", 52.0, 77.54)
s2.add_wire(61.11, 75.0, 52.0, 75.0)   # VCC
s2.add_pwr("+3V3", 52.0, 75.0)

# SCL Pin 3 at (61.11, 72.46) -> Pico GP1 (137.14, 107.3)
s2.add_wire(61.11, 72.46, 85.0, 72.46)
s2.add_wire(85.0, 72.46, 85.0, 107.3)
s2.add_wire(85.0, 107.3, 137.14, 107.3)
# Pullup R10 for SCL
s2.add_symbol("Device", "R", "R10", "4.7k", "Resistor_SMD:R_0805_2012Metric", 95.0, 72.46, rot=90)
s2.add_wire(85.0, 72.46, 91.19, 72.46)
s2.add_wire(98.81, 72.46, 105.0, 72.46)
s2.add_pwr("+3V3", 105.0, 72.46)

# SDA Pin 4 at (61.11, 69.92) -> Pico GP0 (137.14, 104.76)
s2.add_wire(61.11, 69.92, 80.0, 69.92)
s2.add_wire(80.0, 69.92, 80.0, 104.76)
s2.add_wire(80.0, 104.76, 137.14, 104.76)
# Pullup R9 for SDA
s2.add_symbol("Device", "R", "R9", "4.7k", "Resistor_SMD:R_0805_2012Metric", 95.0, 69.92, rot=90)
s2.add_wire(80.0, 69.92, 91.19, 69.92)
s2.add_wire(98.81, 69.92, 105.0, 69.92)
s2.add_pwr("+3V3", 105.0, 69.92)

# Rotary Encoder SW1 at (60.0, 115.0)
s2.add_symbol("Device", "RotaryEncoder_Switch", "SW1", "Rotary_Encoder", 
    "Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm", 60.0, 115.0)
# Connect Rotary Pins A, B, C, S1, S2
# EC11 Pin C at (60.0, 115.0-2.54) -> GND
s2.add_wire(60.0, 117.54, 60.0, 122.0)
s2.add_pwr("GND", 60.0, 122.0)
# Pin S2 -> GND
s2.add_wire(62.54, 118.81, 62.54, 122.0)

# Wire GP2 (ENC_A at 137.14, 109.84) -> SW1 Pin A
s2.add_wire(137.14, 109.84, 125.0, 109.84)
s2.add_label("ENC_A", 125.0, 109.84, rot=180)
s2.add_label("ENC_A", 68.0, 110.0, rot=0)
s2.add_wire(68.0, 110.0, 62.54, 110.0)
# Pullup R11
s2.add_symbol("Device", "R", "R11", "10k", "Resistor_SMD:R_0805_2012Metric", 80.0, 110.0, rot=90)
s2.add_wire(68.0, 110.0, 76.19, 110.0)
s2.add_wire(83.81, 110.0, 90.0, 110.0)
s2.add_pwr("+3V3", 90.0, 110.0)

# Wire GP3 (ENC_B at 137.14, 112.38) -> SW1 Pin B
s2.add_wire(137.14, 112.38, 125.0, 112.38)
s2.add_label("ENC_B", 125.0, 112.38, rot=180)
s2.add_label("ENC_B", 68.0, 113.0, rot=0)
s2.add_wire(68.0, 113.0, 62.54, 113.0)
# Pullup R12
s2.add_symbol("Device", "R", "R12", "10k", "Resistor_SMD:R_0805_2012Metric", 80.0, 113.0, rot=90)
s2.add_wire(68.0, 113.0, 76.19, 113.0)
s2.add_wire(83.81, 113.0, 90.0, 113.0)
s2.add_pwr("+3V3", 90.0, 113.0)

# Wire GP4 (ENC_SW at 137.14, 114.92) -> SW1 Pin S1
s2.add_wire(137.14, 114.92, 125.0, 114.92)
s2.add_label("ENC_SW", 125.0, 114.92, rot=180)
s2.add_label("ENC_SW", 68.0, 116.0, rot=0)
s2.add_wire(68.0, 116.0, 62.54, 116.0)
# Pullup R13
s2.add_symbol("Device", "R", "R13", "10k", "Resistor_SMD:R_0805_2012Metric", 80.0, 116.0, rot=90)
s2.add_wire(68.0, 116.0, 76.19, 116.0)
s2.add_wire(83.81, 116.0, 90.0, 116.0)
s2.add_pwr("+3V3", 90.0, 116.0)

# Tactile Pushbuttons SW2..SW5 at (50, 140..170)
btn_defs = [
    ("SW2", "PLAY_STOP", "GP5", 137.14, 117.46, "R14", 140.0),
    ("SW3", "REC_DUMP",  "GP6", 137.14, 120.0,  "R15", 150.0),
    ("SW4", "REW_PREV",  "GP7", 137.14, 122.54, "R16", 160.0),
    ("SW5", "FFWD_NEXT", "GP8", 137.14, 125.08, "R17", 170.0)
]
for ref, name, gp, px, py, rref, by in btn_defs:
    s2.add_symbol("Switch", "SW_Push", ref, name, "Button_Switch_THT:SW_PUSH_6mm", 50.0, by)
    s2.add_wire(55.08, by, 70.0, by)
    s2.add_label(name, 70.0, by, rot=0)
    s2.add_wire(44.92, by, 38.0, by)
    s2.add_pwr("GND", 38.0, by)
    # Pullup
    s2.add_symbol("Device", "R", rref, "10k", "Resistor_SMD:R_0805_2012Metric", 60.0, by-4.0, rot=90)
    s2.add_wire(55.08, by, 55.08, by-4.0)
    s2.add_wire(55.08, by-4.0, 56.19, by-4.0)
    s2.add_wire(63.81, by-4.0, 70.0, by-4.0)
    s2.add_pwr("+3V3", 70.0, by-4.0)
    # Pico pin connection
    s2.add_wire(px, py, px-10.0, py)
    s2.add_label(name, px-10.0, py, rot=180)

# Status LEDs D2..D5 driven from GP9..GP12
led_defs = [
    ("D2", "LED_READ",   137.14, 127.62, "R19", 190.0, "Green"),
    ("D3", "LED_WRITE",  137.14, 130.16, "R20", 200.0, "Red"),
    ("D4", "LED_MOTOR",  137.14, 132.70, "R21", 210.0, "Yellow"),
    ("D5", "LED_SIGNAL", 137.14, 135.24, "R22", 220.0, "Blue")
]
for ref, name, px, py, rref, ly, col in led_defs:
    s2.add_wire(px, py, px-10.0, py)
    s2.add_label(name, px-10.0, py, rot=180)
    # Resistor + LED
    s2.add_label(name, 70.0, ly, rot=0)
    s2.add_symbol("Device", "R", rref, "330", "Resistor_SMD:R_0805_2012Metric", 80.0, ly, rot=90)
    s2.add_wire(70.0, ly, 76.19, ly)
    s2.add_wire(83.81, ly, 90.0, ly)
    s2.add_symbol("Device", "LED", ref, col, "LED_SMD:LED_0805_2012Metric", 95.0, ly, rot=180)
    s2.add_wire(90.0, ly, 91.19, ly)
    s2.add_wire(98.81, ly, 105.0, ly)
    s2.add_pwr("GND", 105.0, ly)

# Power indicator LED D6 at (50.0, 230.0)
s2.add_symbol("Device", "R", "R23", "1k", "Resistor_SMD:R_0805_2012Metric", 50.0, 230.0, rot=90)
s2.add_wire(40.0, 230.0, 46.19, 230.0)
s2.add_pwr("+3V3", 40.0, 230.0)
s2.add_wire(53.81, 230.0, 60.0, 230.0)
s2.add_symbol("Device", "LED", "D6", "PWR 3.3V", "LED_SMD:LED_0805_2012Metric", 65.0, 230.0, rot=180)
s2.add_wire(60.0, 230.0, 61.19, 230.0)
s2.add_wire(68.81, 230.0, 75.0, 230.0)
s2.add_pwr("GND", 75.0, 230.0)

# Connect Inter-Sheet Signals on Pico:
# GP13: TAPE_DIGITIZED (input from Sheet 3) at (137.14, 137.78)
s2.add_wire(137.14, 137.78, 125.0, 137.78)
s2.add_global_label("TAPE_DIGITIZED", 125.0, 137.78, rot=180, shape="input")

# GP14: C64_MOTOR_SENSE (input from Sheet 4) at (137.14, 140.32)
s2.add_wire(137.14, 140.32, 125.0, 140.32)
s2.add_global_label("C64_MOTOR_SENSE", 125.0, 140.32, rot=180, shape="input")

# GP15: C64_READ (output to Sheet 4) at (137.14, 142.86)
s2.add_wire(137.14, 142.86, 125.0, 142.86)
s2.add_global_label("C64_READ", 125.0, 142.86, rot=180, shape="output")

# Right side pins on Pico:
# GP16: SPI0_MISO (MicroSD DAT0) at (182.86, 107.3)
s2.add_wire(182.86, 107.3, 195.0, 107.3)
s2.add_label("SD_MISO", 195.0, 107.3, rot=0)

# GP17: SPI0_CS (MicroSD CS/DAT3) at (182.86, 109.84)
s2.add_wire(182.86, 109.84, 195.0, 109.84)
s2.add_label("SD_CS", 195.0, 109.84, rot=0)

# GP18: SPI0_SCK (MicroSD CLK) at (182.86, 112.38)
s2.add_wire(182.86, 112.38, 195.0, 112.38)
s2.add_label("SD_SCK", 195.0, 112.38, rot=0)

# GP19: SPI0_MOSI (MicroSD CMD) at (182.86, 114.92)
s2.add_wire(182.86, 114.92, 195.0, 114.92)
s2.add_label("SD_MOSI", 195.0, 114.92, rot=0)

# GP20: C64_WRITE (input from Sheet 4) at (182.86, 117.46)
s2.add_wire(182.86, 117.46, 195.0, 117.46)
s2.add_global_label("C64_WRITE", 195.0, 117.46, rot=0, shape="input")

# GP21: C64_SENSE_DRIVE (output to Sheet 4) at (182.86, 120.0)
s2.add_wire(182.86, 120.0, 195.0, 120.0)
s2.add_global_label("C64_SENSE_DRIVE", 195.0, 120.0, rot=0, shape="output")

# GP22: AUDIO_OUT_PWM (output to Sheet 4) at (182.86, 122.54)
s2.add_wire(182.86, 122.54, 195.0, 122.54)
s2.add_global_label("AUDIO_OUT_PWM", 195.0, 122.54, rot=0, shape="output")

# GP26_ADC0: AZIMUTH_PEAK_ADC (input from Sheet 3) at (182.86, 132.70)
s2.add_wire(182.86, 132.70, 195.0, 132.70)
s2.add_global_label("AZIMUTH_PEAK_ADC", 195.0, 132.70, rot=0, shape="input")

# GP27_ADC1: REMOTE_DRIVE (output to Sheet 4) at (182.86, 135.24)
s2.add_wire(182.86, 135.24, 195.0, 135.24)
s2.add_global_label("REMOTE_DRIVE", 195.0, 135.24, rot=0, shape="output")

# AGND Pin 33 at (182.86, 142.86) -> GND
s2.add_wire(182.86, 142.86, 195.0, 142.86)
s2.add_pwr("GND", 195.0, 142.86)

# J2 MicroSD Card Socket at (240.0, 110.0)
s2.add_symbol("Connector", "Micro_SD_Card_Det1", "J2", "MicroSD", 
    "Connector_Card:microSD_HC_Hirose_DM3D-SF", 240.0, 110.0)
# Connect SD Card pins:
# Pin 2 (DAT3/CS) at (217.14, 117.62) <- SD_CS
s2.add_wire(217.14, 117.62, 210.0, 117.62)
s2.add_label("SD_CS", 210.0, 117.62, rot=180)
# Pullup R5 (10k)
s2.add_symbol("Device", "R", "R5", "10k", "Resistor_SMD:R_0805_2012Metric", 225.0, 95.0, rot=90)
s2.add_wire(210.0, 117.62, 210.0, 95.0)
s2.add_wire(210.0, 95.0, 221.19, 95.0)
s2.add_wire(228.81, 95.0, 235.0, 95.0)
s2.add_pwr("+3V3", 235.0, 95.0)

# Pin 3 (CMD/MOSI) at (217.14, 115.08) <- SD_MOSI
s2.add_wire(217.14, 115.08, 210.0, 115.08)
s2.add_label("SD_MOSI", 210.0, 115.08, rot=180)
s2.add_symbol("Device", "R", "R6", "10k", "Resistor_SMD:R_0805_2012Metric", 225.0, 90.0, rot=90)
s2.add_wire(210.0, 115.08, 210.0, 90.0)
s2.add_wire(210.0, 90.0, 221.19, 90.0)
s2.add_wire(228.81, 90.0, 235.0, 90.0)
s2.add_pwr("+3V3", 235.0, 90.0)

# Pin 4 (VDD) at (217.14, 112.54) -> +3V3
s2.add_wire(217.14, 112.54, 210.0, 112.54)
s2.add_pwr("+3V3", 210.0, 112.54)
# Decoupling C12 (100nF)
s2.add_symbol("Device", "C", "C12", "100nF", "Capacitor_SMD:C_0805_2012Metric", 210.0, 125.0)
s2.add_wire(210.0, 121.19, 210.0, 112.54)
s2.add_wire(210.0, 128.81, 210.0, 135.0)
s2.add_pwr("GND", 210.0, 135.0)

# Pin 5 (CLK) at (217.14, 110.0) <- SD_SCK
s2.add_wire(217.14, 110.0, 205.0, 110.0)
s2.add_label("SD_SCK", 205.0, 110.0, rot=180)
s2.add_symbol("Device", "R", "R8", "10k", "Resistor_SMD:R_0805_2012Metric", 225.0, 85.0, rot=90)
s2.add_wire(205.0, 110.0, 205.0, 85.0)
s2.add_wire(205.0, 85.0, 221.19, 85.0)
s2.add_wire(228.81, 85.0, 235.0, 85.0)
s2.add_pwr("+3V3", 235.0, 85.0)

# Pin 6 (VSS) at (217.14, 107.46) -> GND
s2.add_wire(217.14, 107.46, 210.0, 107.46)
s2.add_pwr("GND", 210.0, 107.46)

# Pin 7 (DAT0/MISO) at (217.14, 104.92) <- SD_MISO
s2.add_wire(217.14, 104.92, 205.0, 104.92)
s2.add_label("SD_MISO", 205.0, 104.92, rot=180)
s2.add_symbol("Device", "R", "R7", "10k", "Resistor_SMD:R_0805_2012Metric", 225.0, 80.0, rot=90)
s2.add_wire(205.0, 104.92, 205.0, 80.0)
s2.add_wire(205.0, 80.0, 221.19, 80.0)
s2.add_wire(228.81, 80.0, 235.0, 80.0)
s2.add_pwr("+3V3", 235.0, 80.0)

# Shield at (260.32, 97.3) -> GND
s2.add_wire(260.32, 97.3, 260.32, 90.0)
s2.add_pwr("GND", 260.32, 90.0)

with open(os.path.join(kicad_dir, "02_MCU_Core.kicad_sch"), "w", encoding="utf-8") as f:
    f.write(s2.render(resolve_symbol))

# ==============================================================================
# 3. SHEET 3: 03_Analog_Ingest.kicad_sch
# ==============================================================================
s3 = SchematicBuilder(s3_uuid, root_uuid,
    "Analog Ingest, Active Sallen-Key Filter, Peak Detector & Digitizer",
    "OPA2134/NE5532 Low Noise Preamp, 300Hz-12kHz Active Bandpass, LM3914 Azimuth Bargraph & LM393 Digitizer")

# Input Jack J3 at (40.0, 70.0)
s3.add_symbol("Connector_Audio", "AudioJack3", "J3", "HEAD_IN / LINE_IN", 
    "Connector_Audio:Jack_3.5mm_PJ320D_Horizontal", 40.0, 70.0)
s3.add_wire(45.08, 72.54, 55.0, 72.54) # Pin S (Sleeve) -> GND
s3.add_pwr("GND", 55.0, 72.54)

# Tip (45.08, 67.46) -> JP2 selector at (60.0, 70.0)
s3.add_wire(45.08, 67.46, 54.92, 67.46)
s3.add_symbol("Connector_Generic", "Conn_01x02", "JP2", "HEAD_BOOST", 
    "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", 60.0, 70.0)
s3.add_wire(54.92, 70.0, 68.0, 70.0)
s3.add_wire(54.92, 67.46, 68.0, 67.46)
s3.add_wire(68.0, 70.0, 68.0, 67.46)

# Input protection D7 BAT54S
s3.add_symbol("Device", "D_Schottky_Dual_Series_ACK", "D7", "BAT54S", 
    "Package_TO_SOT_SMD:SOT-23", 75.0, 67.46)
s3.add_wire(68.0, 67.46, 75.0, 67.46)

# Input AC coupling C15 (1uF) at (90.0, 67.46, rot=90)
s3.add_symbol("Device", "C", "C15", "1uF", "Capacitor_SMD:C_0805_2012Metric", 90.0, 67.46, rot=90)
s3.add_wire(75.0, 67.46, 86.19, 67.46)
s3.add_wire(93.81, 67.46, 105.0, 67.46)

# Input bias R24 (100k) to VBIAS at (105.0, 80.0)
s3.add_symbol("Device", "R", "R24", "100k", "Resistor_SMD:R_0805_2012Metric", 105.0, 80.0)
s3.add_wire(105.0, 67.46, 105.0, 76.19)
s3.add_wire(105.0, 83.81, 105.0, 90.0)
s3.add_global_label("VBIAS", 105.0, 90.0, rot=270, shape="input")

# Stage 1 Pre-Amp U4 Unit 1 (NE5532) at (125.0, 65.0)
s3.add_symbol("Amplifier_Operational", "NE5532", "U4", "NE5532", 
    "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 125.0, 65.0, unit=1)
# Pin 3 (+) at (117.38, 62.46) <- wire from C15/R24
s3.add_wire(105.0, 67.46, 117.38, 67.46)
s3.add_wire(117.38, 67.46, 117.38, 62.46)

# Feedback: Pin 2 (-) at (117.38, 67.54)
# R25 (1k) to VBIAS
s3.add_symbol("Device", "R", "R25", "1k", "Resistor_SMD:R_0805_2012Metric", 117.38, 80.0)
s3.add_wire(117.38, 67.54, 117.38, 76.19)
s3.add_wire(117.38, 83.81, 117.38, 90.0)
s3.add_global_label("VBIAS", 117.38, 90.0, rot=270, shape="input")

# R26 (9.1k) + RV1 (100k trimmer) from Pin 2 (-) to Pin 1 output at (132.62, 65.0)
s3.add_symbol("Device", "R", "R26", "9.1k", "Resistor_SMD:R_0805_2012Metric", 125.0, 52.0, rot=90)
s3.add_symbol("Device", "R_Potentiometer", "RV1", "100k TRIM", 
    "Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical", 137.0, 52.0, rot=90)
s3.add_wire(117.38, 67.54, 112.0, 67.54)
s3.add_wire(112.0, 67.54, 112.0, 52.0)
s3.add_wire(112.0, 52.0, 121.19, 52.0)
s3.add_wire(128.81, 52.0, 133.19, 52.0)
s3.add_wire(140.81, 52.0, 145.0, 52.0)
s3.add_wire(145.0, 52.0, 145.0, 65.0)
s3.add_wire(132.62, 65.0, 145.0, 65.0)

# C16 (47pF) in parallel with feedback
s3.add_symbol("Device", "C", "C16", "47pF", "Capacitor_SMD:C_0805_2012Metric", 125.0, 44.0, rot=90)
s3.add_wire(112.0, 52.0, 112.0, 44.0)
s3.add_wire(112.0, 44.0, 121.19, 44.0)
s3.add_wire(128.81, 44.0, 145.0, 44.0)
s3.add_wire(145.0, 44.0, 145.0, 52.0)

# Preamp output net PREAMP_OUT at (145.0, 65.0)
s3.add_wire(145.0, 65.0, 155.0, 65.0)
s3.add_label("PREAMP_OUT", 155.0, 65.0, rot=0)

# Stage 2: Sallen-Key High-Pass Filter (300 Hz) U5 Unit 1 at (195.0, 65.0)
# C17 (47nF), C18 (47nF), R27 (8.2k), R28 (16k)
s3.add_label("PREAMP_OUT", 160.0, 65.0, rot=180)
s3.add_symbol("Device", "C", "C17", "47nF", "Capacitor_SMD:C_0805_2012Metric", 170.0, 65.0, rot=90)
s3.add_wire(160.0, 65.0, 166.19, 65.0)
s3.add_wire(173.81, 65.0, 178.0, 65.0)

s3.add_symbol("Device", "C", "C18", "47nF", "Capacitor_SMD:C_0805_2012Metric", 184.0, 65.0, rot=90)
s3.add_wire(178.0, 65.0, 180.19, 65.0)
s3.add_wire(187.81, 65.0, 192.0, 65.0)

# U5 Unit 1 at (200.0, 65.0)
s3.add_symbol("Amplifier_Operational", "NE5532", "U5", "NE5532", 
    "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 200.0, 65.0, unit=1)
# Pin 3 (+) at (192.38, 62.46)
s3.add_wire(192.0, 65.0, 192.38, 65.0)
s3.add_wire(192.38, 65.0, 192.38, 62.46)

# R28 (16k) from Pin 3 to VBIAS
s3.add_symbol("Device", "R", "R28", "16k 1%", "Resistor_SMD:R_0805_2012Metric", 192.38, 75.0)
s3.add_wire(192.38, 65.0, 192.38, 71.19)
s3.add_wire(192.38, 78.81, 192.38, 85.0)
s3.add_global_label("VBIAS", 192.38, 85.0, rot=270, shape="input")

# R27 (8.2k) from junction between C17/C18 (178.0, 65.0) to output Pin 1 (207.62, 65.0)
s3.add_symbol("Device", "R", "R27", "8.2k 1%", "Resistor_SMD:R_0805_2012Metric", 190.0, 52.0, rot=90)
s3.add_wire(178.0, 65.0, 178.0, 52.0)
s3.add_wire(178.0, 52.0, 186.19, 52.0)
s3.add_wire(193.81, 52.0, 212.0, 52.0)
s3.add_wire(212.0, 52.0, 212.0, 65.0)
s3.add_wire(207.62, 65.0, 212.0, 65.0)

# Pin 2 (-) of U5 is follower: wire Pin 2 at (192.38, 67.54) to Pin 1 output
s3.add_wire(192.38, 67.54, 188.0, 67.54)
s3.add_wire(188.0, 67.54, 188.0, 58.0)
s3.add_wire(188.0, 58.0, 207.62, 58.0)
s3.add_wire(207.62, 58.0, 207.62, 65.0)

# HPF Output net at (212.0, 65.0)
s3.add_wire(212.0, 65.0, 222.0, 65.0)
s3.add_label("HPF_OUT", 222.0, 65.0, rot=0)

# Stage 3: Sallen-Key Low-Pass Filter (12 kHz) U5 Unit 2 at (60.0, 130.0)
# R29 (12k), R30 (12k), C19 (1.5nF), C20 (680pF)
s3.add_label("HPF_OUT", 35.0, 130.0, rot=180)
s3.add_symbol("Device", "R", "R29", "12k 1%", "Resistor_SMD:R_0805_2012Metric", 45.0, 130.0, rot=90)
s3.add_wire(35.0, 130.0, 41.19, 130.0)
s3.add_wire(48.81, 130.0, 55.0, 130.0)

s3.add_symbol("Device", "R", "R30", "12k 1%", "Resistor_SMD:R_0805_2012Metric", 62.0, 130.0, rot=90)
s3.add_wire(55.0, 130.0, 58.19, 130.0)
s3.add_wire(65.81, 130.0, 72.0, 130.0)

# U5 Unit 2 at (80.0, 130.0)
s3.add_symbol("Amplifier_Operational", "NE5532", "U5", "NE5532", 
    "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 80.0, 130.0, unit=2)
# Pin 5 (+) at (72.38, 127.46)
s3.add_wire(72.0, 130.0, 72.38, 130.0)
s3.add_wire(72.38, 130.0, 72.38, 127.46)

# C20 (680pF) from Pin 5 to VBIAS
s3.add_symbol("Device", "C", "C20", "680pF", "Capacitor_SMD:C_0805_2012Metric", 72.38, 140.0)
s3.add_wire(72.38, 130.0, 72.38, 136.19)
s3.add_wire(72.38, 143.81, 72.38, 150.0)
s3.add_global_label("VBIAS", 72.38, 150.0, rot=270, shape="input")

# C19 (1.5nF) from junction R29/R30 (55.0, 130.0) to output Pin 7 (87.62, 130.0)
s3.add_symbol("Device", "C", "C19", "1.5nF", "Capacitor_SMD:C_0805_2012Metric", 70.0, 118.0, rot=90)
s3.add_wire(55.0, 130.0, 55.0, 118.0)
s3.add_wire(55.0, 118.0, 66.19, 118.0)
s3.add_wire(73.81, 118.0, 92.0, 118.0)
s3.add_wire(92.0, 118.0, 92.0, 130.0)
s3.add_wire(87.62, 130.0, 92.0, 130.0)

# Pin 6 (-) at (72.38, 132.54) -> follower to Pin 7 out
s3.add_wire(72.38, 132.54, 68.0, 132.54)
s3.add_wire(68.0, 132.54, 68.0, 124.0)
s3.add_wire(68.0, 124.0, 87.62, 124.0)
s3.add_wire(87.62, 124.0, 87.62, 130.0)

# LPF Output net is TAPE_FILTERED
s3.add_wire(92.0, 130.0, 105.0, 130.0)
s3.add_label("TAPE_FILTERED", 105.0, 130.0, rot=0)

# Stage 4: Precision Peak Detector U6 Unit 1 at (130.0, 130.0)
s3.add_label("TAPE_FILTERED", 115.0, 130.0, rot=180)
s3.add_symbol("Amplifier_Operational", "NE5532", "U6", "NE5532", 
    "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 130.0, 130.0, unit=1)
s3.add_wire(115.0, 130.0, 122.38, 130.0)
s3.add_wire(122.38, 130.0, 122.38, 127.46) # Pin 3 (+)

# D8 BAT54 diode from Pin 1 out (137.62, 130.0)
s3.add_symbol("Device", "D_Schottky", "D8", "BAT54", "Package_TO_SOT_SMD:SOT-23", 145.0, 130.0, rot=180)
s3.add_wire(137.62, 130.0, 141.19, 130.0)
s3.add_wire(148.81, 130.0, 155.0, 130.0)

# Peak hold capacitor C21 (1uF) + Bleed resistor R31 (100k) to VBIAS
s3.add_symbol("Device", "C", "C21", "1uF", "Capacitor_SMD:C_0805_2012Metric", 155.0, 142.0)
s3.add_wire(155.0, 130.0, 155.0, 138.19)
s3.add_wire(155.0, 145.81, 155.0, 152.0)
s3.add_global_label("VBIAS", 155.0, 152.0, rot=270, shape="input")

s3.add_symbol("Device", "R", "R31", "100k", "Resistor_SMD:R_0805_2012Metric", 165.0, 142.0)
s3.add_wire(155.0, 130.0, 165.0, 130.0)
s3.add_wire(165.0, 130.0, 165.0, 138.19)
s3.add_wire(165.0, 145.81, 165.0, 152.0)
s3.add_global_label("VBIAS", 165.0, 152.0, rot=270, shape="input")

# Pin 2 (-) feedback from peak node
s3.add_wire(155.0, 130.0, 155.0, 122.0)
s3.add_wire(155.0, 122.0, 122.38, 122.0)
s3.add_wire(122.38, 122.0, 122.38, 132.54) # Pin 2 (-)

# Buffer U6 Unit 2 for ADC and LM3914 at (185.0, 130.0)
s3.add_symbol("Amplifier_Operational", "NE5532", "U6", "NE5532", 
    "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 185.0, 130.0, unit=2)
# Pin 5 (+) at (177.38, 127.46) <- Peak node
s3.add_wire(165.0, 130.0, 177.38, 130.0)
s3.add_wire(177.38, 130.0, 177.38, 127.46)
# Pin 6 (-) at (177.38, 132.54) -> Pin 7 out at (192.62, 130.0)
s3.add_wire(177.38, 132.54, 173.0, 132.54)
s3.add_wire(173.0, 132.54, 173.0, 124.0)
s3.add_wire(173.0, 124.0, 192.62, 124.0)
s3.add_wire(192.62, 124.0, 192.62, 130.0)

# Output of U6 Unit 2 is PEAK_SIGNAL
s3.add_wire(192.62, 130.0, 205.0, 130.0)
s3.add_label("PEAK_SIGNAL", 205.0, 130.0, rot=0)

# Feed ADC via R32 (1k)
s3.add_symbol("Device", "R", "R32", "1k", "Resistor_SMD:R_0805_2012Metric", 215.0, 130.0, rot=90)
s3.add_wire(205.0, 130.0, 211.19, 130.0)
s3.add_wire(218.81, 130.0, 228.0, 130.0)
s3.add_global_label("AZIMUTH_PEAK_ADC", 228.0, 130.0, rot=0, shape="output")

# Stage 5: Digitizer Schmitt Trigger U8 LM393 at (60.0, 190.0)
s3.add_symbol("Comparator", "LM393", "U8", "LM393", 
    "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 60.0, 190.0, unit=1)
# Pin 2 (-) at (52.38, 192.54) -> VBIAS (2.5V threshold)
s3.add_wire(52.38, 192.54, 45.0, 192.54)
s3.add_global_label("VBIAS", 45.0, 192.54, rot=180, shape="input")

# Pin 3 (+) at (52.38, 187.46) <- TAPE_FILTERED via R34 (10k)
s3.add_symbol("Device", "R", "R34", "10k", "Resistor_SMD:R_0805_2012Metric", 40.0, 187.46, rot=90)
s3.add_wire(52.38, 187.46, 43.81, 187.46)
s3.add_wire(36.19, 187.46, 28.0, 187.46)
s3.add_label("TAPE_FILTERED", 28.0, 187.46, rot=180)

# Hysteresis positive feedback from Pin 1 out (67.62, 190.0) via R35 (470k) + RV3 (50k)
s3.add_symbol("Device", "R", "R35", "470k", "Resistor_SMD:R_0805_2012Metric", 60.0, 178.0, rot=90)
s3.add_symbol("Device", "R_Potentiometer", "RV3", "50k HYST", 
    "Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical", 72.0, 178.0, rot=90)
s3.add_wire(52.38, 187.46, 48.0, 187.46)
s3.add_wire(48.0, 187.46, 48.0, 178.0)
s3.add_wire(48.0, 178.0, 56.19, 178.0)
s3.add_wire(63.81, 178.0, 68.19, 178.0)
s3.add_wire(75.81, 178.0, 80.0, 178.0)
s3.add_wire(80.0, 178.0, 80.0, 190.0)
s3.add_wire(67.62, 190.0, 80.0, 190.0)

# Pullup R36 (2.2k) to +3V3 on open collector output
s3.add_symbol("Device", "R", "R36", "2.2k", "Resistor_SMD:R_0805_2012Metric", 80.0, 202.0)
s3.add_wire(80.0, 190.0, 80.0, 198.19)
s3.add_wire(80.0, 205.81, 80.0, 212.0)
s3.add_pwr("+3V3", 80.0, 212.0)

# Output is TAPE_DIGITIZED
s3.add_wire(80.0, 190.0, 95.0, 190.0)
s3.add_global_label("TAPE_DIGITIZED", 95.0, 190.0, rot=0, shape="output")

# Stage 6: LM3914 10-LED Azimuth Bargraph U7 at (150.0, 190.0)
s3.add_symbol("Driver_LED", "LM3914N", "U7", "LM3914N", 
    "Package_DIP:DIP-18_W7.62mm", 150.0, 190.0)
# Pin 5 (SIG) at (139.84, 197.62) <- PEAK_SIGNAL
s3.add_wire(139.84, 197.62, 130.0, 197.62)
s3.add_label("PEAK_SIGNAL", 130.0, 197.62, rot=180)

# Pin 4 (RLO) at (139.84, 190.0) -> VBIAS
s3.add_wire(139.84, 190.0, 130.0, 190.0)
s3.add_global_label("VBIAS", 130.0, 190.0, rot=180, shape="input")

# Pin 6 (RHI) at (139.84, 192.54) <- Sensitivity trimmer RV2 (10k)
s3.add_symbol("Device", "R_Potentiometer", "RV2", "10k SENS", 
    "Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical", 125.0, 185.0, rot=90)
s3.add_wire(139.84, 192.54, 128.81, 192.54)
s3.add_wire(128.81, 192.54, 128.81, 185.0)

# Pin 7 (REFOUT at 139.84, 184.92) & Pin 8 (REFADJ at 139.84, 182.38) via R33 (1.2k)
s3.add_symbol("Device", "R", "R33", "1.2k", "Resistor_SMD:R_0805_2012Metric", 125.0, 175.0)
s3.add_wire(139.84, 184.92, 125.0, 184.92)
s3.add_wire(125.0, 184.92, 125.0, 178.81)
s3.add_wire(139.84, 182.38, 125.0, 182.38)
s3.add_wire(125.0, 182.38, 125.0, 171.19)
s3.add_pwr("GND", 125.0, 170.0)

# Pin 3 (V+) at (150.0, 205.24) -> +5V
s3.add_wire(150.0, 205.24, 150.0, 212.0)
s3.add_pwr("+5V", 150.0, 212.0)
# Pin 2 (V-) at (150.0, 172.22) -> GND
s3.add_wire(150.0, 172.22, 150.0, 165.0)
s3.add_pwr("GND", 150.0, 165.0)

# LM3914 10 LED outputs D10..D19 (6 Green, 2 Yellow, 2 Red)
led_outputs = [
    ("D10", "Green",  160.16, 200.16, 215.0),
    ("D11", "Green",  160.16, 197.62, 212.0),
    ("D12", "Green",  160.16, 195.08, 209.0),
    ("D13", "Green",  160.16, 192.54, 206.0),
    ("D14", "Green",  160.16, 190.0,  203.0),
    ("D15", "Green",  160.16, 187.46, 200.0),
    ("D16", "Yellow", 160.16, 184.92, 197.0),
    ("D17", "Yellow", 160.16, 182.38, 194.0),
    ("D18", "Red",    160.16, 179.84, 191.0),
    ("D19", "Red",    160.16, 177.30, 188.0)
]
for ref, col, px, py, ly in led_outputs:
    s3.add_wire(px, py, px+10.0, py)
    s3.add_symbol("Device", "LED", ref, f"VU_{col}", "LED_SMD:LED_0805_2012Metric", px+15.0, py, rot=0)
    s3.add_wire(px+15.0+3.81, py, px+25.0, py)
    s3.add_pwr("+5V", px+25.0, py)

# Power decoupling for U4, U5, U6, U8
for i, (uref, ux) in enumerate([("U4", 50.0), ("U5", 70.0), ("U6", 90.0), ("U8", 110.0)]):
    s3.add_symbol("Device", "C", f"C{22+i}", "100nF", "Capacitor_SMD:C_0805_2012Metric", ux, 230.0)
    s3.add_wire(ux, 226.19, ux, 220.0)
    s3.add_pwr("+5V", ux, 220.0)
    s3.add_wire(ux, 233.81, ux, 240.0)
    s3.add_pwr("GND", ux, 240.0)

with open(os.path.join(kicad_dir, "03_Analog_Ingest.kicad_sch"), "w", encoding="utf-8") as f:
    f.write(s3.render(resolve_symbol))

# ==============================================================================
# 4. SHEET 4: 04_Tape_Interfaces.kicad_sch
# ==============================================================================
s4 = SchematicBuilder(s4_uuid, root_uuid,
    "Vintage Cassette Bus Interfaces & Remote Control",
    "Commodore C2N 6-Pin Datassette Port (74LS06 Driver), Sinclair/Apple Audio PWM & Opto Remote Relay")

# J4 C2N Edge Connector at (50.0, 80.0)
s4.add_symbol("Tape-Master", "C2N_Connector", "J4", "C2N_EDGE", 
    "Tape-Master:C2N_Edge_Connector", 50.0, 80.0)
# J5 C2N 2.54mm Header at (50.0, 130.0) in parallel
s4.add_symbol("Connector_Generic", "Conn_01x06", "J5", "C2N_HEADER", 
    "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical", 50.0, 130.0)

# Pin 1: GND at (39.84, 85.08) and (44.92, 135.08)
s4.add_wire(39.84, 85.08, 30.0, 85.08)
s4.add_pwr("GND", 30.0, 85.08)
s4.add_wire(44.92, 135.08, 30.0, 135.08)
s4.add_pwr("GND", 30.0, 135.08)

# Pin 2: +5V_C64 at (39.84, 82.54) -> global C2N_5V_IN
s4.add_wire(39.84, 82.54, 30.0, 82.54)
s4.add_global_label("C2N_5V_IN", 30.0, 82.54, rot=180, shape="output")
s4.add_wire(44.92, 132.54, 30.0, 132.54)
s4.add_global_label("C2N_5V_IN", 30.0, 132.54, rot=180, shape="output")

# Pin 3: MOTOR at (39.84, 80.0) -> Motor Sense Circuit
s4.add_wire(39.84, 80.0, 30.0, 80.0)
s4.add_label("C64_MOTOR_RAW", 30.0, 80.0, rot=180)
s4.add_wire(44.92, 130.0, 30.0, 130.0)
s4.add_label("C64_MOTOR_RAW", 30.0, 130.0, rot=180)

# Motor sense Q2 2N3904 at (100.0, 80.0)
s4.add_label("C64_MOTOR_RAW", 80.0, 80.0, rot=180)
s4.add_symbol("Device", "R", "R39", "10k", "Resistor_SMD:R_0805_2012Metric", 90.0, 80.0, rot=90)
s4.add_wire(80.0, 80.0, 86.19, 80.0)
s4.add_wire(93.81, 80.0, 100.0, 80.0)
s4.add_symbol("Device", "Q_NPN", "Q2", "2N3904", "Package_TO_SOT_SMD:SOT-23", 105.0, 80.0)
# Base pulldown R40 (10k)
s4.add_symbol("Device", "R", "R40", "10k", "Resistor_SMD:R_0805_2012Metric", 100.0, 92.0)
s4.add_wire(100.0, 80.0, 100.0, 88.19)
s4.add_wire(100.0, 95.81, 100.0, 102.0)
s4.add_pwr("GND", 100.0, 102.0)
# Emitter to GND
s4.add_wire(105.0, 82.54, 105.0, 102.0)
s4.add_pwr("GND", 105.0, 102.0)
# Collector pulled to +3V3 via R41 (10k)
s4.add_symbol("Device", "R", "R41", "10k", "Resistor_SMD:R_0805_2012Metric", 115.0, 68.0)
s4.add_wire(105.0, 77.46, 115.0, 77.46)
s4.add_wire(115.0, 77.46, 115.0, 71.81)
s4.add_wire(115.0, 64.19, 115.0, 58.0)
s4.add_pwr("+3V3", 115.0, 58.0)
# Output to Pico
s4.add_wire(115.0, 77.46, 125.0, 77.46)
s4.add_global_label("C64_MOTOR_SENSE", 125.0, 77.46, rot=0, shape="output")

# Pin 4: READ driven by U9 74LS06 Open-Collector Inverter at (100.0, 120.0)
s4.add_symbol("74xx", "74LS06", "U9", "74LS06", "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm", 100.0, 120.0, unit=1)
# Pin 1 input at (92.38, 120.0) <- C64_READ from RP2040
s4.add_wire(92.38, 120.0, 80.0, 120.0)
s4.add_global_label("C64_READ", 80.0, 120.0, rot=180, shape="input")
# Pin 2 output at (107.62, 120.0) -> connects to C2N READ
s4.add_wire(107.62, 120.0, 120.0, 120.0)
s4.add_label("C64_READ_OUT", 120.0, 120.0, rot=0)
# Wire to J4 and J5 Pin 4
s4.add_wire(60.16, 77.46, 70.0, 77.46)
s4.add_label("C64_READ_OUT", 70.0, 77.46, rot=0)
s4.add_wire(44.92, 127.46, 35.0, 127.46)
s4.add_label("C64_READ_OUT", 35.0, 127.46, rot=180)

# U9 Power Unit 7 at (100.0, 145.0)
s4.add_symbol("74xx", "74LS06", "U9", "74LS06", "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm", 100.0, 145.0, unit=7)
s4.add_wire(100.0, 132.3, 100.0, 125.0) # Pin 14 VCC
s4.add_pwr("+5V", 100.0, 125.0)
s4.add_wire(100.0, 157.7, 100.0, 165.0) # Pin 7 GND
s4.add_pwr("GND", 100.0, 165.0)
s4.add_symbol("Device", "C", "C31", "100nF", "Capacitor_SMD:C_0805_2012Metric", 112.0, 145.0)
s4.add_wire(112.0, 141.19, 112.0, 125.0)
s4.add_pwr("+5V", 112.0, 125.0)
s4.add_wire(112.0, 148.81, 112.0, 165.0)
s4.add_pwr("GND", 112.0, 165.0)

# Pin 5: WRITE (5V -> 3.3V divider R42 1k / R43 2k)
s4.add_wire(39.84, 74.92, 30.0, 74.92)
s4.add_label("C64_WRITE_RAW", 30.0, 74.92, rot=180)
s4.add_wire(44.92, 124.92, 30.0, 124.92)
s4.add_label("C64_WRITE_RAW", 30.0, 124.92, rot=180)

s4.add_label("C64_WRITE_RAW", 140.0, 80.0, rot=180)
s4.add_symbol("Device", "R", "R42", "1k", "Resistor_SMD:R_0805_2012Metric", 150.0, 80.0, rot=90)
s4.add_wire(140.0, 80.0, 146.19, 80.0)
s4.add_wire(153.81, 80.0, 160.0, 80.0)
s4.add_symbol("Device", "R", "R43", "2k", "Resistor_SMD:R_0805_2012Metric", 160.0, 92.0)
s4.add_wire(160.0, 80.0, 160.0, 88.19)
s4.add_wire(160.0, 95.81, 160.0, 102.0)
s4.add_pwr("GND", 160.0, 102.0)
s4.add_wire(160.0, 80.0, 172.0, 80.0)
s4.add_global_label("C64_WRITE", 172.0, 80.0, rot=0, shape="output")

# Pin 6: SENSE driven by Q1 2N7002 at (140.0, 120.0)
s4.add_symbol("Device", "Q_NMOS", "Q1", "2N7002", "Package_TO_SOT_SMD:SOT-23", 140.0, 120.0)
# Gate <- C64_SENSE_DRIVE via R37 (1k)
s4.add_symbol("Device", "R", "R37", "1k", "Resistor_SMD:R_0805_2012Metric", 125.0, 120.0, rot=90)
s4.add_global_label("C64_SENSE_DRIVE", 115.0, 120.0, rot=180, shape="input")
s4.add_wire(115.0, 120.0, 121.19, 120.0)
s4.add_wire(128.81, 120.0, 134.92, 120.0) # Gate
# Gate pulldown R38 (100k)
s4.add_symbol("Device", "R", "R38", "100k", "Resistor_SMD:R_0805_2012Metric", 134.92, 132.0)
s4.add_wire(134.92, 120.0, 134.92, 128.19)
s4.add_wire(134.92, 135.81, 134.92, 142.0)
s4.add_pwr("GND", 134.92, 142.0)
# Source to GND
s4.add_wire(140.0, 122.54, 140.0, 142.0)
s4.add_pwr("GND", 140.0, 142.0)
# Drain to C2N SENSE
s4.add_wire(140.0, 117.46, 140.0, 110.0)
s4.add_label("C64_SENSE_OUT", 140.0, 110.0, rot=0)
s4.add_wire(60.16, 72.38, 70.0, 72.38)
s4.add_label("C64_SENSE_OUT", 70.0, 72.38, rot=0)
s4.add_wire(44.92, 122.38, 35.0, 122.38)
s4.add_label("C64_SENSE_OUT", 35.0, 122.38, rot=180)

# Sinclair ZX & Apple II Audio Output Jack J6 at (210.0, 75.0)
s4.add_symbol("Connector_Audio", "AudioJack3", "J6", "AUDIO_OUT", 
    "Connector_Audio:Jack_3.5mm_PJ320D_Horizontal", 210.0, 75.0)
s4.add_wire(215.08, 77.54, 222.0, 77.54) # Sleeve -> GND
s4.add_pwr("GND", 222.0, 77.54)

# 2nd-order RC filter from AUDIO_OUT_PWM:
# R44 (1k), C28 (10nF), R45 (1k), C29 (10nF), C30 (10uF)
s4.add_global_label("AUDIO_OUT_PWM", 150.0, 60.0, rot=180, shape="input")
s4.add_symbol("Device", "R", "R44", "1k", "Resistor_SMD:R_0805_2012Metric", 160.0, 60.0, rot=90)
s4.add_wire(150.0, 60.0, 156.19, 60.0)
s4.add_wire(163.81, 60.0, 170.0, 60.0)
s4.add_symbol("Device", "C", "C28", "10nF", "Capacitor_SMD:C_0805_2012Metric", 170.0, 70.0)
s4.add_wire(170.0, 60.0, 170.0, 66.19)
s4.add_wire(170.0, 73.81, 170.0, 80.0)
s4.add_pwr("GND", 170.0, 80.0)

s4.add_symbol("Device", "R", "R45", "1k", "Resistor_SMD:R_0805_2012Metric", 180.0, 60.0, rot=90)
s4.add_wire(170.0, 60.0, 176.19, 60.0)
s4.add_wire(183.81, 60.0, 190.0, 60.0)
s4.add_symbol("Device", "C", "C29", "10nF", "Capacitor_SMD:C_0805_2012Metric", 190.0, 70.0)
s4.add_wire(190.0, 60.0, 190.0, 66.19)
s4.add_wire(190.0, 73.81, 190.0, 80.0)
s4.add_pwr("GND", 190.0, 80.0)

# AC coupling C30 (10uF)
s4.add_symbol("Device", "C", "C30", "10uF", "Capacitor_SMD:C_0805_2012Metric", 200.0, 60.0, rot=90)
s4.add_wire(190.0, 60.0, 196.19, 60.0)
s4.add_wire(203.81, 60.0, 215.08, 60.0)
s4.add_wire(215.08, 60.0, 215.08, 72.46) # Tip is EAR_OUT (1 Vpp)

# Attenuator R46 (10k) / R47 (1k) for MIC_OUT (100 mVpp) on Ring
s4.add_symbol("Device", "R", "R46", "10k", "Resistor_SMD:R_0805_2012Metric", 205.0, 75.0)
s4.add_wire(215.08, 60.0, 205.0, 60.0)
s4.add_wire(205.0, 60.0, 205.0, 71.19)
s4.add_wire(205.0, 78.81, 215.08, 75.0) # Ring is MIC_OUT
s4.add_symbol("Device", "R", "R47", "1k", "Resistor_SMD:R_0805_2012Metric", 215.08, 87.0)
s4.add_wire(215.08, 75.0, 215.08, 83.19)
s4.add_wire(215.08, 90.81, 215.08, 97.0)
s4.add_pwr("GND", 215.08, 97.0)

# Opto-isolated Remote Motor Control J7 & U10 PC817 at (200.0, 130.0)
s4.add_symbol("Isolator", "PC817", "U10", "PC817", "Package_DIP:DIP-4_W7.62mm", 190.0, 130.0)
# Pin 1 Anode at (182.38, 132.54) <- REMOTE_DRIVE via R48 (330 ohm)
s4.add_symbol("Device", "R", "R48", "330", "Resistor_SMD:R_0805_2012Metric", 172.0, 132.54, rot=90)
s4.add_global_label("REMOTE_DRIVE", 162.0, 132.54, rot=180, shape="input")
s4.add_wire(162.0, 132.54, 168.19, 132.54)
s4.add_wire(175.81, 132.54, 182.38, 132.54)
# Pin 2 Cathode at (182.38, 127.46) -> GND
s4.add_wire(182.38, 127.46, 175.0, 127.46)
s4.add_pwr("GND", 175.0, 127.46)

# Output phototransistor: Pin 4 Collector at (197.62, 132.54), Pin 3 Emitter at (197.62, 127.46)
s4.add_symbol("Connector_Audio", "AudioJack3", "J7", "REMOTE_2.5mm", 
    "Connector_Audio:Jack_3.5mm_PJ320D_Horizontal", 215.0, 130.0)
s4.add_wire(197.62, 132.54, 220.08, 132.54)
s4.add_wire(220.08, 132.54, 220.08, 127.46) # J7 Tip
s4.add_wire(197.62, 127.46, 220.08, 127.46)
s4.add_wire(220.08, 127.46, 220.08, 132.54) # Connect across J7 contacts

with open(os.path.join(kicad_dir, "04_Tape_Interfaces.kicad_sch"), "w", encoding="utf-8") as f:
    f.write(s4.render(resolve_symbol))

print("All 5 schematics built successfully!")
