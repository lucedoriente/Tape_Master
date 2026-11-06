import os, sys
from production_sch_builder import ProductionSheet, snap

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
root = ProductionSheet(root_uuid,
    "Tape Master Exerciser & Signal Digitizer - System Architecture",
    "Modular Vintage Tape Deck Exerciser, Azimuth Tuning & Signal Digitizer")

root.add_subsheet("01_Power_Supply", "01_Power_Supply.kicad_sch", s1_uuid, 40.0, 45.0, 80.0, 45.0, 2)
root.add_subsheet("02_MCU_Core", "02_MCU_Core.kicad_sch", s2_uuid, 145.0, 45.0, 95.0, 65.0, 3)
root.add_subsheet("03_Analog_Ingest", "03_Analog_Ingest.kicad_sch", s3_uuid, 40.0, 115.0, 80.0, 60.0, 4)
root.add_subsheet("04_Tape_Interfaces", "04_Tape_Interfaces.kicad_sch", s4_uuid, 145.0, 130.0, 95.0, 45.0, 5)

with open(os.path.join(kicad_dir, "Tape-Master.kicad_sch"), "w", encoding="utf-8") as f:
    f.write(root.render(page_num="1", is_root=True))

# ==============================================================================
# 1. SHEET 1: 01_Power_Supply.kicad_sch
# ==============================================================================
s1 = ProductionSheet(s1_uuid,
    "Power Supply & Precision Bias Reference Subsystem",
    "USB-C / C2N +5V Dual Input, 3.3V Ultra-Low-Noise LDO & 2.5V Stiff Analog VBIAS")

# J1 USB-C
s1.add_comp("J1", "USB_C_Receptacle_USB2.0_16P", "USB-C",
    "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal", 40.0, 60.0)

# Connect CC pins to 5.1k resistors
s1.add_comp("R1", "R", "5.1k", "Resistor_SMD:R_0805_2012Metric", 70.0, 50.0, rot=90)
s1.connect_pins("J1", "A5", "R1", "1")
s1.connect_pin_stub("R1", "2", "GND", is_pwr=True)

s1.add_comp("R2", "R", "5.1k", "Resistor_SMD:R_0805_2012Metric", 70.0, 56.0, rot=90)
s1.connect_pins("J1", "B5", "R2", "1")
s1.connect_pin_stub("R2", "2", "GND", is_pwr=True)

# Ground connections for USB-C
s1.connect_pin_stub("J1", "A1", "GND", is_pwr=True)
s1.connect_pin_stub("J1", "S1", "GND", is_pwr=True)
s1.connect_pin_stub("J1", "A12", "GND", is_pwr=True)
s1.connect_pin_stub("J1", "B1", "GND", is_pwr=True)
s1.connect_pin_stub("J1", "B12", "GND", is_pwr=True)

# Unused USB pins -> no_connect
for p in ["A6", "A7", "A8", "B6", "B7", "B8"]:
    s1.add_no_connect("J1", p)

# F1 Polyfuse in series with VBUS
s1.add_comp("F1", "Polyfuse", "PTC 1A", "Fuse:Fuse_1206_3216Metric", 70.0, 44.76, rot=90)
s1.connect_pins("J1", "A4", "F1", "1")
s1.connect_pins("J1", "B4", "F1", "1")
s1.connect_pins("J1", "A9", "F1", "1")
s1.connect_pins("J1", "B9", "F1", "1")

# C2N Power selection JP1
s1.add_comp("JP1", "Conn_01x02", "C2N_PWR_SEL",
    "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", 70.0, 75.0)
s1.connect_pin_stub("JP1", "1", "C2N_5V_IN", is_global=True, shape="input")

# D1 Dual Schottky BAT54C (Cathode Pin 3 is +5V)
s1.add_comp("D1", "D_Schottky_Dual_CommonCathode_AAK", "BAT54C",
    "Package_TO_SOT_SMD:SOT-23", 95.0, 60.0)
s1.connect_pins("F1", "2", "D1", "1")
s1.connect_pins("JP1", "2", "D1", "2")
p3_x, p3_y = s1.connect_pin_stub("D1", "3", "+5V", is_pwr=True)
s1.add_pwr_flag(p3_x, p3_y) # +5V PWR_FLAG

# Bulk caps C1 (100uF tantalum), C2 (10uF ceramic), C3 (100nF ceramic)
s1.add_comp("C1", "C_Polarized", "100uF", "Capacitor_Tantalum_SMD:CP_EIA-3528-21_Kemet-B", 115.0, 60.0)
s1.connect_pin_stub("C1", "1", "+5V", is_pwr=True)
s1.connect_pin_stub("C1", "2", "GND", is_pwr=True)

s1.add_comp("C2", "C", "10uF", "Capacitor_SMD:C_0805_2012Metric", 127.0, 60.0)
s1.connect_pin_stub("C2", "1", "+5V", is_pwr=True)
s1.connect_pin_stub("C2", "2", "GND", is_pwr=True)

s1.add_comp("C3", "C", "100nF", "Capacitor_SMD:C_0805_2012Metric", 139.0, 60.0)
s1.connect_pin_stub("C3", "1", "+5V", is_pwr=True)
s1.connect_pin_stub("C3", "2", "GND", is_pwr=True)

# U1 AP2112K-3.3 LDO
s1.add_comp("U1", "AP2112K-3.3", "AP2112K-3.3",
    "Package_TO_SOT_SMD:SOT-23-5", 160.0, 60.0)
s1.connect_pin_stub("U1", "1", "+5V", is_pwr=True)
s1.connect_pin_stub("U1", "3", "+5V", is_pwr=True)
s1.connect_pin_stub("U1", "2", "GND", is_pwr=True)
s1.connect_pin_stub("U1", "5", "+3V3", is_pwr=True)
s1.add_no_connect("U1", "4")

# LDO caps
s1.add_comp("C4", "C", "1uF", "Capacitor_SMD:C_0805_2012Metric", 150.0, 75.0)
s1.connect_pin_stub("C4", "1", "+5V", is_pwr=True)
s1.connect_pin_stub("C4", "2", "GND", is_pwr=True)

for i, (val, ref) in enumerate([("2.2uF", "C5"), ("100nF", "C6")]):
    cx = 175.0 + i * 12.0
    s1.add_comp(ref, "C", val, "Capacitor_SMD:C_0805_2012Metric", cx, 75.0)
    s1.connect_pin_stub(ref, "1", "+3V3", is_pwr=True)
    s1.connect_pin_stub(ref, "2", "GND", is_pwr=True)

# VBIAS precision divider R3, R4
s1.add_comp("R3", "R", "10k 0.1%", "Resistor_SMD:R_0805_2012Metric", 50.0, 110.0)
s1.connect_pin_stub("R3", "1", "+5V", is_pwr=True)

s1.add_comp("R4", "R", "10k 0.1%", "Resistor_SMD:R_0805_2012Metric", 50.0, 125.0)
s1.connect_pin_stub("R4", "2", "GND", is_pwr=True)
s1.connect_pins("R3", "2", "R4", "1")

# VBIAS filter caps C7, C8
s1.add_comp("C7", "C_Polarized", "47uF", "Capacitor_Tantalum_SMD:CP_EIA-3528-21_Kemet-B", 65.0, 120.0)
s1.connect_pins("R4", "1", "C7", "1")
s1.connect_pin_stub("C7", "2", "GND", is_pwr=True)

s1.add_comp("C8", "C", "100nF", "Capacitor_SMD:C_0805_2012Metric", 77.0, 120.0)
s1.connect_pins("C7", "1", "C8", "1")
s1.connect_pin_stub("C8", "2", "GND", is_pwr=True)

# U2 TLV2372 RRIO Op-Amp Unit 1 follower (pin 1 is Output)
s1.add_comp("U2", "TLV2372", "TLV2372", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 100.0, 120.0, unit=1)
s1.connect_pins("C8", "1", "U2", "3", u2=1)
s1.connect_pins("U2", "2", "U2", "1", u1=1, u2=1)
s1.connect_pin_stub("U2", "1", "VBIAS", is_global=True, shape="output", unit=1)

# Decoupling for VBIAS output
s1.add_comp("C9", "C", "10uF", "Capacitor_SMD:C_0805_2012Metric", 125.0, 120.0)
s1.connect_pin_stub("C9", "1", "VBIAS", is_global=True, shape="input")
s1.connect_pin_stub("C9", "2", "GND", is_pwr=True)

s1.add_comp("C10", "C", "100nF", "Capacitor_SMD:C_0805_2012Metric", 137.0, 120.0)
s1.connect_pin_stub("C10", "1", "VBIAS", is_global=True, shape="input")
s1.connect_pin_stub("C10", "2", "GND", is_pwr=True)

# U2 Unit 2 follower to VBIAS
s1.add_comp("U2", "TLV2372", "TLV2372", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 100.0, 140.0, unit=2)
s1.connect_pin_stub("U2", "5", "VBIAS", is_global=True, shape="input", unit=2)
s1.connect_pins("U2", "6", "U2", "7", u1=2, u2=2)

# U2 Unit 3 power
s1.add_comp("U2", "TLV2372", "TLV2372", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 100.0, 160.0, unit=3)
s1.connect_pin_stub("U2", "8", "+5V", is_pwr=True, unit=3)
s1.connect_pin_stub("U2", "4", "GND", is_pwr=True, unit=3)

s1.add_comp("C11", "C", "100nF", "Capacitor_SMD:C_0805_2012Metric", 115.0, 160.0)
s1.connect_pin_stub("C11", "1", "+5V", is_pwr=True)
s1.connect_pin_stub("C11", "2", "GND", is_pwr=True)

# 4 Mounting Holes H1..H4
for idx, (hx, hy) in enumerate([(20.0, 190.0), (35.0, 190.0), (50.0, 190.0), (65.0, 190.0)]):
    s1.add_comp(f"H{idx+1}", "MountingHole", "MountingHole", "MountingHole:MountingHole_3.2mm_M3", hx, hy)

with open(os.path.join(kicad_dir, "01_Power_Supply.kicad_sch"), "w", encoding="utf-8") as f:
    f.write(s1.render(page_num="2"))

# ==============================================================================
# 2. SHEET 2: 02_MCU_Core.kicad_sch
# ==============================================================================
s2 = ProductionSheet(s2_uuid,
    "Microcontroller Core & User Interface",
    "Raspberry Pi Pico (RP2040), MicroSD SPI, I2C OLED 128x64, Rotary Encoder & Shift Register Interface")

# U3 Raspberry Pi Pico at (160.0, 120.0)
s2.add_comp("U3", "RaspberryPi_Pico", "RaspberryPi_Pico", 
    "Module:RaspberryPi_Pico_Common_THT", 160.0, 120.0)

# Power & GND to Pico
s2.connect_pin_stub("U3", "39", "+5V", is_pwr=True) # VSYS (power_in)
s2.connect_pin_stub("U3", "3", "GND", is_pwr=True)
s2.connect_pin_stub("U3", "8", "GND", is_pwr=True)
s2.connect_pin_stub("U3", "13", "GND", is_pwr=True)
s2.connect_pin_stub("U3", "18", "GND", is_pwr=True)
s2.connect_pin_stub("U3", "23", "GND", is_pwr=True)
s2.connect_pin_stub("U3", "28", "GND", is_pwr=True)
s2.connect_pin_stub("U3", "38", "GND", is_pwr=True)
s2.connect_pin_stub("U3", "33", "GND", is_pwr=True) # AGND

# Pico power outputs / spares -> no_connect
s2.add_no_connect("U3", "36")
s2.add_no_connect("U3", "40")
s2.add_no_connect("U3", "37")
s2.add_no_connect("U3", "12") # GP9 (Spare)
s2.add_no_connect("U3", "34") # GP28 (Spare)

# ADC_VREF Pin 35 connected to +3V3 with C13 (100nF) to GND
s2.connect_pin_stub("U3", "35", "+3V3", is_pwr=True)
s2.add_comp("C13", "C", "100nF", "Capacitor_SMD:C_0805_2012Metric", 195.0, 115.0)
s2.connect_pin_stub("C13", "1", "+3V3", is_pwr=True)
s2.connect_pin_stub("C13", "2", "GND", is_pwr=True)

# Reset Button SW6 on Pin 30 (RUN)
s2.add_comp("SW6", "SW_Push", "RESET", "Button_Switch_THT:SW_PUSH_6mm", 115.0, 97.14)
s2.connect_pins("U3", "30", "SW6", "2")
s2.connect_pin_stub("SW6", "1", "GND", is_pwr=True)

# I2C OLED Display DISP1 at (70.0, 75.0)
s2.add_comp("DISP1", "OLED_0.96_I2C", "OLED_0.96_I2C", 
    "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", 70.0, 75.0)
s2.connect_pin_stub("DISP1", "1", "GND", is_pwr=True)
s2.connect_pin_stub("DISP1", "2", "+3V3", is_pwr=True)

# SCL Pin 3 & SDA Pin 4
s2.connect_pin_stub("DISP1", "3", "I2C_SCL")
s2.connect_pin_stub("DISP1", "4", "I2C_SDA")
s2.connect_pin_stub("U3", "2", "I2C_SCL") # GP1
s2.connect_pin_stub("U3", "1", "I2C_SDA") # GP0

# I2C Pullups R9, R10
s2.add_comp("R9", "R", "4.7k", "Resistor_SMD:R_0805_2012Metric", 95.0, 70.0, rot=90)
s2.connect_pin_stub("R9", "1", "I2C_SDA")
s2.connect_pin_stub("R9", "2", "+3V3", is_pwr=True)

s2.add_comp("R10", "R", "4.7k", "Resistor_SMD:R_0805_2012Metric", 95.0, 76.0, rot=90)
s2.connect_pin_stub("R10", "1", "I2C_SCL")
s2.connect_pin_stub("R10", "2", "+3V3", is_pwr=True)

# Rotary Encoder SW1 at (60.0, 115.0)
s2.add_comp("SW1", "RotaryEncoder_Switch", "Rotary_Encoder", 
    "Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm", 60.0, 115.0)
s2.connect_pin_stub("SW1", "C", "GND", is_pwr=True)
s2.connect_pin_stub("SW1", "S2", "GND", is_pwr=True)

s2.connect_pin_stub("SW1", "A", "ENC_A")
s2.connect_pin_stub("SW1", "B", "ENC_B")
s2.connect_pin_stub("SW1", "S1", "ENC_SW")
s2.connect_pin_stub("U3", "4", "ENC_A") # GP2
s2.connect_pin_stub("U3", "5", "ENC_B") # GP3
s2.connect_pin_stub("U3", "6", "ENC_SW") # GP4

# Encoder Pullups R11, R12, R13
for i, (pname, rref) in enumerate([("ENC_A", "R11"), ("ENC_B", "R12"), ("ENC_SW", "R13")]):
    ry = 105.0 + i * 8.0
    s2.add_comp(rref, "R", "10k", "Resistor_SMD:R_0805_2012Metric", 85.0, ry, rot=90)
    s2.connect_pin_stub(rref, "1", pname)
    s2.connect_pin_stub(rref, "2", "+3V3", is_pwr=True)

# Buttons SW2..SW5
btn_defs = [
    ("SW2", "BTN_PLAY_STOP", "7", "R14", 140.0),
    ("SW3", "BTN_REC_DUMP",  "9", "R15", 150.0),
    ("SW4", "BTN_REW_PREV",  "10", "R16", 160.0),
    ("SW5", "BTN_FFWD_NEXT", "11", "R17", 170.0)
]
for ref, name, pnum, rref, by in btn_defs:
    s2.add_comp(ref, "SW_Push", name, "Button_Switch_THT:SW_PUSH_6mm", 50.0, by)
    s2.connect_pin_stub(ref, "1", "GND", is_pwr=True)
    s2.connect_pin_stub(ref, "2", name)
    s2.connect_pin_stub("U3", pnum, name)
    s2.add_comp(rref, "R", "10k", "Resistor_SMD:R_0805_2012Metric", 70.0, by-3.0, rot=90)
    s2.connect_pin_stub(rref, "1", name)
    s2.connect_pin_stub(rref, "2", "+3V3", is_pwr=True)

# TLC5916 LED Shift Register Bus from RP2040:
# GP10 (Pin 14) -> LEDBAR_CLK
# GP11 (Pin 15) -> LEDBAR_DATA
# GP12 (Pin 16) -> LEDBAR_LE
s2.connect_pin_stub("U3", "14", "LEDBAR_CLK", is_global=True, shape="output")
s2.connect_pin_stub("U3", "15", "LEDBAR_DATA", is_global=True, shape="output")
s2.connect_pin_stub("U3", "16", "LEDBAR_LE", is_global=True, shape="output")

# Power indicator LED D6 at (50.0, 200.0)
s2.add_comp("R23", "R", "1k", "Resistor_SMD:R_0805_2012Metric", 50.0, 200.0, rot=90)
s2.connect_pin_stub("R23", "1", "+3V3", is_pwr=True)
s2.add_comp("D6", "LED", "PWR 3.3V", "LED_SMD:LED_0805_2012Metric", 65.0, 200.0, rot=180)
s2.connect_pins("R23", "2", "D6", "2")
s2.connect_pin_stub("D6", "1", "GND", is_pwr=True)

# Inter-Sheet Signals on Pico:
s2.connect_pin_stub("U3", "17", "TAPE_DIGITIZED", is_global=True, shape="input")
s2.connect_pin_stub("U3", "19", "C64_MOTOR_SENSE", is_global=True, shape="input")
s2.connect_pin_stub("U3", "20", "C64_READ", is_global=True, shape="output")

s2.connect_pin_stub("U3", "21", "SD_MISO") # GP16
s2.connect_pin_stub("U3", "22", "SD_CS")   # GP17
s2.connect_pin_stub("U3", "24", "SD_SCK")  # GP18
s2.connect_pin_stub("U3", "25", "SD_MOSI") # GP19

s2.connect_pin_stub("U3", "26", "C64_WRITE", is_global=True, shape="input")
s2.connect_pin_stub("U3", "27", "C64_SENSE_DRIVE", is_global=True, shape="output")
s2.connect_pin_stub("U3", "29", "AUDIO_OUT_PWM", is_global=True, shape="output")
s2.connect_pin_stub("U3", "31", "AZIMUTH_PEAK_ADC", is_global=True, shape="input")
s2.connect_pin_stub("U3", "32", "REMOTE_DRIVE", is_global=True, shape="output")

# J2 MicroSD Card Socket at (240.0, 110.0)
s2.add_comp("J2", "Micro_SD_Card_Det1", "MicroSD", 
    "Connector_Card:microSD_HC_Hirose_DM3D-SF", 240.0, 110.0)
s2.connect_pin_stub("J2", "2", "SD_CS")
s2.connect_pin_stub("J2", "3", "SD_MOSI")
s2.connect_pin_stub("J2", "4", "+3V3", is_pwr=True)
s2.connect_pin_stub("J2", "5", "SD_SCK")
s2.connect_pin_stub("J2", "6", "GND", is_pwr=True)
s2.connect_pin_stub("J2", "7", "SD_MISO")
s2.connect_pin_stub("J2", "10", "GND", is_pwr=True) # Shield
s2.add_no_connect("J2", "1") # DAT2
s2.add_no_connect("J2", "8") # DAT1
s2.add_no_connect("J2", "9") # DET

# SD Pullups R5..R8
for i, (snet, rref) in enumerate([("SD_CS", "R5"), ("SD_MOSI", "R6"), ("SD_MISO", "R7"), ("SD_SCK", "R8")]):
    ry = 65.0 + i * 8.0
    s2.add_comp(rref, "R", "10k", "Resistor_SMD:R_0805_2012Metric", 220.0, ry, rot=90)
    s2.connect_pin_stub(rref, "1", snet)
    s2.connect_pin_stub(rref, "2", "+3V3", is_pwr=True)

# SD bypass cap C12 (100nF)
s2.add_comp("C12", "C", "100nF", "Capacitor_SMD:C_0805_2012Metric", 215.0, 125.0)
s2.connect_pin_stub("C12", "1", "+3V3", is_pwr=True)
s2.connect_pin_stub("C12", "2", "GND", is_pwr=True)

with open(os.path.join(kicad_dir, "02_MCU_Core.kicad_sch"), "w", encoding="utf-8") as f:
    f.write(s2.render(page_num="3"))

# ==============================================================================
# 3. SHEET 3: 03_Analog_Ingest.kicad_sch
# ==============================================================================
s3 = ProductionSheet(s3_uuid,
    "Analog Ingest, Active Sallen-Key Filter, Peak Detector & Digitizer",
    "TLV2372 RRIO Low-Noise Preamp, 300Hz-12kHz Active Bandpass, Dual TLC5916 LED Drivers & LM393 Digitizer")

# Input Jack J3 at (40.0, 70.0)
s3.add_comp("J3", "AudioJack3", "HEAD_IN / LINE_IN", 
    "Connector_Audio:Jack_3.5mm_CUI_SJ-3523-SMT_Horizontal", 40.0, 70.0)
s3.connect_pin_stub("J3", "S", "GND", is_pwr=True)

# Input selector JP2 at (60.0, 70.0)
s3.add_comp("JP2", "Conn_01x02", "HEAD_BOOST", 
    "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", 60.0, 70.0)
s3.connect_pins("J3", "T", "JP2", "1")
s3.connect_pins("J3", "R", "JP2", "2")

# Protection D7 BAT54S
s3.add_comp("D7", "D_Schottky_Dual_Series_ACK", "BAT54S", 
    "Package_TO_SOT_SMD:SOT-23", 75.0, 67.46)
s3.connect_pins("JP2", "1", "D7", "3") # node
s3.connect_pin_stub("D7", "1", "GND", is_pwr=True) # Anode to GND
s3.connect_pin_stub("D7", "2", "+3V3", is_pwr=True) # Cathode to 3.3V

# AC coupling C15 (1uF)
s3.add_comp("C15", "C", "1uF", "Capacitor_SMD:C_0805_2012Metric", 90.0, 67.46, rot=90)
s3.connect_pins("D7", "3", "C15", "1")

# Input bias R24 (100k) to VBIAS
s3.add_comp("R24", "R", "100k", "Resistor_SMD:R_0805_2012Metric", 105.0, 80.0)
s3.connect_pins("C15", "2", "R24", "1")
s3.connect_pin_stub("R24", "2", "VBIAS", is_global=True, shape="input")

# Stage 1 Pre-Amp U4 Unit 1 (TLV2372) at (125.0, 65.0)
s3.add_comp("U4", "TLV2372", "TLV2372", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 125.0, 65.0, unit=1)
s3.connect_pins("C15", "2", "U4", "3", u2=1) # Pin 3 (+)

# Feedback: Pin 2 (-)
s3.add_comp("R25", "R", "1k", "Resistor_SMD:R_0805_2012Metric", 115.0, 80.0)
s3.connect_pins("U4", "2", "R25", "1", u1=1)
s3.connect_pin_stub("R25", "2", "VBIAS", is_global=True, shape="input")

s3.add_comp("R26", "R", "9.1k", "Resistor_SMD:R_0805_2012Metric", 125.0, 52.0, rot=90)
s3.connect_pins("U4", "2", "R26", "1", u1=1)

s3.add_comp("RV1", "R_Potentiometer", "100k TRIM", 
    "Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical", 137.0, 52.0, rot=90)
s3.connect_pins("R26", "2", "RV1", "1")
s3.connect_pins("RV1", "2", "U4", "1", u2=1) # Wiper to Out
s3.connect_pins("RV1", "3", "RV1", "2") # Tie unused pin to wiper

# C16 (47pF) in parallel
s3.add_comp("C16", "C", "47pF", "Capacitor_SMD:C_0805_2012Metric", 125.0, 44.0, rot=90)
s3.connect_pins("U4", "2", "C16", "1", u1=1)
s3.connect_pins("C16", "2", "U4", "1", u2=1)

# Preamp output net
s3.connect_pin_stub("U4", "1", "PREAMP_OUT", unit=1)

# U4 Unit 2 (Follower to VBIAS to avoid unused opamp warning)
s3.add_comp("U4", "TLV2372", "TLV2372", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 125.0, 100.0, unit=2)
s3.connect_pin_stub("U4", "5", "VBIAS", is_global=True, shape="input", unit=2)
s3.connect_pins("U4", "6", "U4", "7", u1=2, u2=2)

# U4 Unit 3 (Power)
s3.add_comp("U4", "TLV2372", "TLV2372", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 125.0, 120.0, unit=3)
s3.connect_pin_stub("U4", "8", "+5V", is_pwr=True, unit=3)
s3.connect_pin_stub("U4", "4", "GND", is_pwr=True, unit=3)
s3.add_comp("C22", "C", "100nF", "Capacitor_SMD:C_0805_2012Metric", 135.0, 120.0)
s3.connect_pin_stub("C22", "1", "+5V", is_pwr=True)
s3.connect_pin_stub("C22", "2", "GND", is_pwr=True)

# Stage 2: Sallen-Key HPF (300 Hz) U5 Unit 1 at (195.0, 65.0)
s3.add_comp("C17", "C", "47nF", "Capacitor_SMD:C_0805_2012Metric", 165.0, 65.0, rot=90)
s3.connect_pin_stub("C17", "1", "PREAMP_OUT")

s3.add_comp("C18", "C", "47nF", "Capacitor_SMD:C_0805_2012Metric", 180.0, 65.0, rot=90)
s3.connect_pins("C17", "2", "C18", "1")

s3.add_comp("U5", "TLV2372", "TLV2372", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 200.0, 65.0, unit=1)
s3.connect_pins("C18", "2", "U5", "3", u2=1) # Pin 3 (+)

# R28 (16k) from Pin 3 to VBIAS
s3.add_comp("R28", "R", "16k 1%", "Resistor_SMD:R_0805_2012Metric", 190.0, 80.0)
s3.connect_pins("C18", "2", "R28", "1")
s3.connect_pin_stub("R28", "2", "VBIAS", is_global=True, shape="input")

# R27 (8.2k) from junction C17/C18 to Pin 1 output
s3.add_comp("R27", "R", "8.2k 1%", "Resistor_SMD:R_0805_2012Metric", 180.0, 52.0, rot=90)
s3.connect_pins("C17", "2", "R27", "1")
s3.connect_pins("R27", "2", "U5", "1", u2=1)

# Follower: Pin 2 (-) to Pin 1 out
s3.connect_pins("U5", "2", "U5", "1", u1=1, u2=1)
s3.connect_pin_stub("U5", "1", "HPF_OUT", unit=1)

# Stage 3: Sallen-Key LPF (12 kHz) U5 Unit 2 at (60.0, 140.0)
s3.add_comp("R29", "R", "12k 1%", "Resistor_SMD:R_0805_2012Metric", 40.0, 140.0, rot=90)
s3.connect_pin_stub("R29", "1", "HPF_OUT")

s3.add_comp("R30", "R", "12k 1%", "Resistor_SMD:R_0805_2012Metric", 55.0, 140.0, rot=90)
s3.connect_pins("R29", "2", "R30", "1")

s3.add_comp("U5", "TLV2372", "TLV2372", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 75.0, 140.0, unit=2)
s3.connect_pins("R30", "2", "U5", "5", u2=2) # Pin 5 (+)

# C20 (680pF) from Pin 5 to VBIAS
s3.add_comp("C20", "C", "680pF", "Capacitor_SMD:C_0805_2012Metric", 65.0, 155.0)
s3.connect_pins("R30", "2", "C20", "1")
s3.connect_pin_stub("C20", "2", "VBIAS", is_global=True, shape="input")

# C19 (1.5nF) from junction R29/R30 to Pin 7 out
s3.add_comp("C19", "C", "1.5nF", "Capacitor_SMD:C_0805_2012Metric", 60.0, 128.0, rot=90)
s3.connect_pins("R29", "2", "C19", "1")
s3.connect_pins("C19", "2", "U5", "7", u2=2)

# Follower: Pin 6 (-) to Pin 7 out
s3.connect_pins("U5", "6", "U5", "7", u1=2, u2=2)
s3.connect_pin_stub("U5", "7", "TAPE_FILTERED", unit=2)

# U5 Unit 3 (Power)
s3.add_comp("U5", "TLV2372", "TLV2372", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 105.0, 180.0, unit=3)
s3.connect_pin_stub("U5", "8", "+5V", is_pwr=True, unit=3)
s3.connect_pin_stub("U5", "4", "GND", is_pwr=True, unit=3)
s3.add_comp("C23", "C", "100nF", "Capacitor_SMD:C_0805_2012Metric", 115.0, 180.0)
s3.connect_pin_stub("C23", "1", "+5V", is_pwr=True)
s3.connect_pin_stub("C23", "2", "GND", is_pwr=True)

# Stage 4: Peak Detector U6 Unit 1 at (130.0, 140.0)
s3.add_comp("U6", "TLV2372", "TLV2372", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 130.0, 140.0, unit=1)
s3.connect_pin_stub("U6", "3", "TAPE_FILTERED", unit=1) # Pin 3 (+)

# D8 BAT54 diode from Pin 1 out
s3.add_comp("D8", "D_Schottky", "BAT54", "Package_TO_SOT_SMD:SOT-23", 145.0, 140.0, rot=180)
s3.connect_pins("U6", "1", "D8", "2", u1=1) # Pin 2 Anode

# C21 (1uF) + R31 (100k) from Cathode Pin 1 to VBIAS
s3.add_comp("C21", "C", "1uF", "Capacitor_SMD:C_0805_2012Metric", 155.0, 155.0)
s3.connect_pins("D8", "1", "C21", "1")
s3.connect_pin_stub("C21", "2", "VBIAS", is_global=True, shape="input")

s3.add_comp("R31", "R", "100k", "Resistor_SMD:R_0805_2012Metric", 165.0, 155.0)
s3.connect_pins("D8", "1", "R31", "1")
s3.connect_pin_stub("R31", "2", "VBIAS", is_global=True, shape="input")

# Feedback: Pin 2 (-) to peak node
s3.connect_pins("U6", "2", "D8", "1", u1=1)

# Buffer U6 Unit 2 at (185.0, 140.0)
s3.add_comp("U6", "TLV2372", "TLV2372", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 185.0, 140.0, unit=2)
s3.connect_pins("D8", "1", "U6", "5", u2=2) # Pin 5 (+)
s3.connect_pins("U6", "6", "U6", "7", u1=2, u2=2) # Follower
s3.connect_pin_stub("U6", "7", "PEAK_SIGNAL", unit=2)

# Peak Detector ADC Divider & Protection:
# R32 (10k 1%) from PEAK_SIGNAL to AZIMUTH_PEAK_ADC
# R33 (18k 1%) from AZIMUTH_PEAK_ADC to GND
# D9 (BAT54) clamp from AZIMUTH_PEAK_ADC to +3.3V
# C32 (100nF) filter cap to GND
s3.add_comp("R32", "R", "10k 1%", "Resistor_SMD:R_0805_2012Metric", 210.0, 140.0, rot=90)
s3.connect_pin_stub("R32", "1", "PEAK_SIGNAL")

s3.add_comp("R33", "R", "18k 1%", "Resistor_SMD:R_0805_2012Metric", 225.0, 140.0, rot=90)
s3.connect_pins("R32", "2", "R33", "1")
s3.connect_pin_stub("R33", "2", "GND", is_pwr=True)

# D9 BAT54 Schottky Clamp: Pin 2 (Anode) at ADC node, Pin 1 (Cathode) to +3V3
s3.add_comp("D9", "D_Schottky", "BAT54", "Package_TO_SOT_SMD:SOT-23", 240.0, 135.0, rot=180)
s3.connect_pins("R32", "2", "D9", "2")
s3.connect_pin_stub("D9", "1", "+3V3", is_pwr=True)

# C32 ADC filter cap
s3.add_comp("C32", "C", "100nF", "Capacitor_SMD:C_0805_2012Metric", 240.0, 150.0)
s3.connect_pins("R32", "2", "C32", "1")
s3.connect_pin_stub("C32", "2", "GND", is_pwr=True)

s3.connect_pin_stub("R32", "2", "AZIMUTH_PEAK_ADC", is_global=True, shape="output")

# U6 Unit 3 (Power)
s3.add_comp("U6", "TLV2372", "TLV2372", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 185.0, 170.0, unit=3)
s3.connect_pin_stub("U6", "8", "+5V", is_pwr=True, unit=3)
s3.connect_pin_stub("U6", "4", "GND", is_pwr=True, unit=3)
s3.add_comp("C24", "C", "100nF", "Capacitor_SMD:C_0805_2012Metric", 195.0, 170.0)
s3.connect_pin_stub("C24", "1", "+5V", is_pwr=True)
s3.connect_pin_stub("C24", "2", "GND", is_pwr=True)

# Stage 5: Digitizer Schmitt Trigger U8 LM393 at (60.0, 205.0)
s3.add_comp("U8", "LM393", "LM393", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 60.0, 205.0, unit=1)
s3.connect_pin_stub("U8", "2", "VBIAS", is_global=True, shape="input", unit=1) # Pin 2 (-)

# Input R34 (10k)
s3.add_comp("R34", "R", "10k", "Resistor_SMD:R_0805_2012Metric", 40.0, 200.0, rot=90)
s3.connect_pin_stub("R34", "1", "TAPE_FILTERED")
s3.connect_pins("R34", "2", "U8", "3", u2=1)

# Hysteresis R35 (470k) + RV3 (50k)
s3.add_comp("R35", "R", "470k", "Resistor_SMD:R_0805_2012Metric", 60.0, 192.0, rot=90)
s3.connect_pins("U8", "3", "R35", "1", u1=1)

s3.add_comp("RV3", "R_Potentiometer", "50k HYST", 
    "Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical", 72.0, 192.0, rot=90)
s3.connect_pins("R35", "2", "RV3", "1")
s3.connect_pins("RV3", "2", "U8", "1", u2=1) # Wiper to Pin 1 out
s3.connect_pins("RV3", "3", "RV3", "2") # Tie unused pin to wiper

# Pullup R36 (2.2k) to +3V3 on open collector output
s3.add_comp("R36", "R", "2.2k", "Resistor_SMD:R_0805_2012Metric", 85.0, 215.0)
s3.connect_pins("U8", "1", "R36", "1", u1=1)
s3.connect_pin_stub("R36", "2", "+3V3", is_pwr=True)
s3.connect_pin_stub("U8", "1", "TAPE_DIGITIZED", is_global=True, shape="output", unit=1)

# U8 Unit 2 (unused unit)
s3.add_comp("U8", "LM393", "LM393", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 60.0, 235.0, unit=2)
s3.connect_pin_stub("U8", "5", "VBIAS", is_global=True, shape="input", unit=2)
s3.connect_pin_stub("U8", "6", "GND", is_pwr=True, unit=2)
s3.add_no_connect("U8", "7", unit=2)

# U8 Unit 3 (Power)
s3.add_comp("U8", "LM393", "LM393", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 60.0, 255.0, unit=3)
s3.connect_pin_stub("U8", "8", "+5V", is_pwr=True, unit=3)
s3.connect_pin_stub("U8", "4", "GND", is_pwr=True, unit=3)
s3.add_comp("C26", "C", "100nF", "Capacitor_SMD:C_0805_2012Metric", 75.0, 255.0)
s3.connect_pin_stub("C26", "1", "+5V", is_pwr=True)
s3.connect_pin_stub("C26", "2", "GND", is_pwr=True)

# Stage 6: Modern Dual Cascaded TLC5916 LED Constant-Current Drivers U7 & U11
# Controls 10 Azimuth Bargraph LEDs (D10..D19) + 4 Status LEDs (D2..D5)
# U7 at (130.0, 220.0), U11 at (195.0, 220.0)

# U7 (TLC5916 #1): Bargraph Low Channels (D10..D17)
s3.add_comp("U7", "TLC5916", "TLC5916", "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm", 130.0, 220.0)
s3.connect_pin_stub("U7", "1", "GND", is_pwr=True)
s3.connect_pin_stub("U7", "2", "LEDBAR_DATA", is_global=True, shape="input")
s3.connect_pin_stub("U7", "3", "LEDBAR_CLK", is_global=True, shape="input")
s3.connect_pin_stub("U7", "4", "LEDBAR_LE", is_global=True, shape="input")
s3.connect_pin_stub("U7", "13", "GND", is_pwr=True) # OE_N tied to GND (always active)
s3.connect_pin_stub("U7", "16", "+3V3", is_pwr=True)

# U7 R-EXT resistor R18 (1.2k) sets constant current to ~15mA
s3.add_comp("R18", "R", "1.2k", "Resistor_SMD:R_0805_2012Metric", 115.0, 240.0, rot=90)
s3.connect_pins("U7", "15", "R18", "1")
s3.connect_pin_stub("R18", "2", "GND", is_pwr=True)

# U7 Decoupling C25 (100nF)
s3.add_comp("C25", "C", "100nF", "Capacitor_SMD:C_0805_2012Metric", 130.0, 245.0)
s3.connect_pin_stub("C25", "1", "+3V3", is_pwr=True)
s3.connect_pin_stub("C25", "2", "GND", is_pwr=True)

# U11 (TLC5916 #2): Bargraph High Channels (D18..D19) + Status LEDs (D2..D5)
s3.add_comp("U11", "TLC5916", "TLC5916", "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm", 195.0, 220.0)
s3.connect_pin_stub("U11", "1", "GND", is_pwr=True)
# Cascade SDO of U7 (pin 14) to SDI of U11 (pin 2)
s3.connect_pins("U7", "14", "U11", "2")
s3.connect_pin_stub("U11", "3", "LEDBAR_CLK", is_global=True, shape="input")
s3.connect_pin_stub("U11", "4", "LEDBAR_LE", is_global=True, shape="input")
s3.connect_pin_stub("U11", "13", "GND", is_pwr=True) # OE_N tied to GND
s3.connect_pin_stub("U11", "16", "+3V3", is_pwr=True)

# U11 R-EXT resistor R20 (1.2k)
s3.add_comp("R20", "R", "1.2k", "Resistor_SMD:R_0805_2012Metric", 180.0, 240.0, rot=90)
s3.connect_pins("U11", "15", "R20", "1")
s3.connect_pin_stub("R20", "2", "GND", is_pwr=True)

# U11 Decoupling C27 (100nF)
s3.add_comp("C27", "C", "100nF", "Capacitor_SMD:C_0805_2012Metric", 195.0, 245.0)
s3.connect_pin_stub("C27", "1", "+3V3", is_pwr=True)
s3.connect_pin_stub("C27", "2", "GND", is_pwr=True)

# U11 unused pins: SDO (pin 14), OUT6 (pin 11), OUT7 (pin 12) -> no_connect
s3.add_no_connect("U11", "14")
s3.add_no_connect("U11", "11")
s3.add_no_connect("U11", "12")

# 10 Bargraph LEDs D10..D19 (Anodes to +5V, Cathodes to TLC5916 sinks)
# D10..D17 to U7 OUT0..OUT7 (pins 5..12)
# D18..D19 to U11 OUT0..OUT1 (pins 5..6)
vu_leds = [
    ("D10", "U7", "5",  "VU_Green"),
    ("D11", "U7", "6",  "VU_Green"),
    ("D12", "U7", "7",  "VU_Green"),
    ("D13", "U7", "8",  "VU_Green"),
    ("D14", "U7", "9",  "VU_Green"),
    ("D15", "U7", "10", "VU_Green"),
    ("D16", "U7", "11", "VU_Green"),
    ("D17", "U7", "12", "VU_Green"),
    ("D18", "U11", "5", "VU_Yellow"),
    ("D19", "U11", "6", "VU_Red")
]

for i, (dref, uref, upin, label) in enumerate(vu_leds):
    dy = 190.0 + i * 5.0
    s3.add_comp(dref, "LED", label, "LED_SMD:LED_0805_2012Metric", 160.0, dy, rot=0)
    s3.connect_pins(uref, upin, dref, "1") # Cathode to sink
    s3.connect_pin_stub(dref, "2", "+5V", is_pwr=True) # Anode to +5V

# 4 Status LEDs D2..D5 to U11 OUT2..OUT5 (pins 7..10)
status_leds = [
    ("D2", "7",  "LED_READ",   "Green"),
    ("D3", "8",  "LED_WRITE",  "Red"),
    ("D4", "9",  "LED_MOTOR",  "Yellow"),
    ("D5", "10", "LED_SIGNAL", "Blue")
]
for i, (dref, upin, val, col) in enumerate(status_leds):
    dy = 245.0 + i * 5.0
    s3.add_comp(dref, "LED", f"{val}_{col}", "LED_SMD:LED_0805_2012Metric", 225.0, dy, rot=0)
    s3.connect_pins("U11", upin, dref, "1") # Cathode to sink
    s3.connect_pin_stub(dref, "2", "+5V", is_pwr=True) # Anode to +5V

with open(os.path.join(kicad_dir, "03_Analog_Ingest.kicad_sch"), "w", encoding="utf-8") as f:
    f.write(s3.render(page_num="4"))

# ==============================================================================
# 4. SHEET 4: 04_Tape_Interfaces.kicad_sch
# ==============================================================================
s4 = ProductionSheet(s4_uuid,
    "Vintage Cassette Bus Interfaces & Remote Control",
    "Commodore C2N 6-Pin Datassette Port (74HCT06 Driver), Sinclair/Apple Audio PWM & Opto Remote Relay")

# J4 C2N Edge Connector at (50.0, 80.0)
s4.add_comp("J4", "C2N_Connector", "C2N_EDGE", "Tape-Master:C2N_Edge_Connector", 50.0, 80.0)
# J5 C2N 2.54mm Header at (50.0, 130.0) in parallel
s4.add_comp("J5", "Conn_01x06", "C2N_HEADER", 
    "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical", 50.0, 130.0)

# Pin 1: GND
s4.connect_pin_stub("J4", "1", "GND", is_pwr=True)
s4.connect_pin_stub("J5", "1", "GND", is_pwr=True)

# Pin 2: +5V_C64 -> global C2N_5V_IN
s4.connect_pin_stub("J4", "2", "C2N_5V_IN", is_global=True, shape="output")
s4.connect_pins("J5", "2", "J4", "2")

# Pin 3: MOTOR -> Motor Sense Circuit
s4.connect_pin_stub("J4", "3", "C64_MOTOR_RAW")
s4.connect_pins("J5", "3", "J4", "3")

# Motor sense Q2 2N3904 at (105.0, 80.0)
s4.add_comp("R39", "R", "10k", "Resistor_SMD:R_0805_2012Metric", 90.0, 80.0, rot=90)
s4.connect_pin_stub("R39", "1", "C64_MOTOR_RAW")

s4.add_comp("Q2", "Q_NPN", "2N3904", "Package_TO_SOT_SMD:SOT-23", 105.0, 80.0)
s4.connect_pins("R39", "2", "Q2", "1") # Base Pin 1

s4.add_comp("R40", "R", "10k", "Resistor_SMD:R_0805_2012Metric", 100.0, 95.0)
s4.connect_pins("Q2", "1", "R40", "1")
s4.connect_pin_stub("R40", "2", "GND", is_pwr=True)

# Emitter Pin 2 to GND
s4.connect_pin_stub("Q2", "2", "GND", is_pwr=True)

# Collector Pin 3 pulled up to +3V3 via R41 (10k)
s4.add_comp("R41", "R", "10k", "Resistor_SMD:R_0805_2012Metric", 115.0, 70.0)
s4.connect_pins("Q2", "3", "R41", "2")
s4.connect_pin_stub("R41", "1", "+3V3", is_pwr=True)
s4.connect_pin_stub("Q2", "3", "C64_MOTOR_SENSE", is_global=True, shape="output")

# Pin 4: READ driven by U9 74HCT06 High-Speed CMOS Open-Collector Inverter at (100.0, 120.0)
s4.add_comp("U9", "74HCT06", "74HCT06", "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm", 100.0, 120.0, unit=1)
s4.connect_pin_stub("U9", "1", "C64_READ", is_global=True, shape="input", unit=1)
s4.connect_pin_stub("U9", "2", "C64_READ_OUT", unit=1)
s4.connect_pin_stub("J4", "4", "C64_READ_OUT")
s4.connect_pins("J5", "4", "J4", "4")

# U9 unused units 2..6: inputs grounded, outputs no_connect
s4.add_comp("U9", "74HCT06", "74HCT06", "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm", 100.0, 140.0, unit=2)
s4.connect_pin_stub("U9", "3", "GND", is_pwr=True, unit=2)
s4.add_no_connect("U9", "4", unit=2)

s4.add_comp("U9", "74HCT06", "74HCT06", "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm", 100.0, 155.0, unit=3)
s4.connect_pin_stub("U9", "5", "GND", is_pwr=True, unit=3)
s4.add_no_connect("U9", "6", unit=3)

s4.add_comp("U9", "74HCT06", "74HCT06", "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm", 100.0, 170.0, unit=4)
s4.connect_pin_stub("U9", "9", "GND", is_pwr=True, unit=4)
s4.add_no_connect("U9", "8", unit=4)

s4.add_comp("U9", "74HCT06", "74HCT06", "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm", 100.0, 185.0, unit=5)
s4.connect_pin_stub("U9", "11", "GND", is_pwr=True, unit=5)
s4.add_no_connect("U9", "10", unit=5)

s4.add_comp("U9", "74HCT06", "74HCT06", "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm", 100.0, 200.0, unit=6)
s4.connect_pin_stub("U9", "13", "GND", is_pwr=True, unit=6)
s4.add_no_connect("U9", "12", unit=6)

# U9 Unit 7 Power
s4.add_comp("U9", "74HCT06", "74HCT06", "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm", 100.0, 220.0, unit=7)
s4.connect_pin_stub("U9", "14", "+5V", is_pwr=True, unit=7)
s4.connect_pin_stub("U9", "7", "GND", is_pwr=True, unit=7)
s4.add_comp("C31", "C", "100nF", "Capacitor_SMD:C_0805_2012Metric", 115.0, 220.0)
s4.connect_pin_stub("C31", "1", "+5V", is_pwr=True)
s4.connect_pin_stub("C31", "2", "GND", is_pwr=True)

# Pin 5: WRITE (5V -> 3.3V divider R42 1k / R43 2k)
s4.connect_pin_stub("J4", "5", "C64_WRITE_RAW")
s4.connect_pins("J5", "5", "J4", "5")

s4.add_comp("R42", "R", "1k", "Resistor_SMD:R_0805_2012Metric", 145.0, 80.0, rot=90)
s4.connect_pin_stub("R42", "1", "C64_WRITE_RAW")

s4.add_comp("R43", "R", "2k", "Resistor_SMD:R_0805_2012Metric", 155.0, 95.0)
s4.connect_pins("R42", "2", "R43", "1")
s4.connect_pin_stub("R43", "2", "GND", is_pwr=True)
s4.connect_pin_stub("R42", "2", "C64_WRITE", is_global=True, shape="output")

# Pin 6: SENSE driven by Q1 2N7002 at (145.0, 120.0)
s4.add_comp("Q1", "Q_NMOS", "2N7002", "Package_TO_SOT_SMD:SOT-23", 145.0, 120.0)
# Gate <- C64_SENSE_DRIVE via R37 (1k)
s4.add_comp("R37", "R", "1k", "Resistor_SMD:R_0805_2012Metric", 130.0, 120.0, rot=90)
s4.connect_pin_stub("R37", "1", "C64_SENSE_DRIVE", is_global=True, shape="input")
s4.connect_pins("R37", "2", "Q1", "1") # Gate Pin 1

# Gate pulldown R38 (100k)
s4.add_comp("R38", "R", "100k", "Resistor_SMD:R_0805_2012Metric", 135.0, 135.0)
s4.connect_pins("Q1", "1", "R38", "1")
s4.connect_pin_stub("R38", "2", "GND", is_pwr=True)

# Source Pin 2 to GND
s4.connect_pin_stub("Q1", "2", "GND", is_pwr=True)

# Drain Pin 3 to C2N SENSE
s4.connect_pin_stub("Q1", "3", "C64_SENSE_OUT")
s4.connect_pin_stub("J4", "6", "C64_SENSE_OUT")
s4.connect_pins("J5", "6", "J4", "6")

# Sinclair ZX & Apple II Audio Output Jack J6 at (210.0, 75.0)
s4.add_comp("J6", "AudioJack3", "AUDIO_OUT", 
    "Connector_Audio:Jack_3.5mm_CUI_SJ-3523-SMT_Horizontal", 210.0, 75.0)
s4.connect_pin_stub("J6", "S", "GND", is_pwr=True)

# RC filter from AUDIO_OUT_PWM: R44 (1k), C28 (10nF), R45 (1k), C29 (10nF), C30 (10uF)
s4.add_comp("R44", "R", "1k", "Resistor_SMD:R_0805_2012Metric", 160.0, 60.0, rot=90)
s4.connect_pin_stub("R44", "1", "AUDIO_OUT_PWM", is_global=True, shape="input")

s4.add_comp("C28", "C", "10nF", "Capacitor_SMD:C_0805_2012Metric", 170.0, 72.0)
s4.connect_pins("R44", "2", "C28", "1")
s4.connect_pin_stub("C28", "2", "GND", is_pwr=True)

s4.add_comp("R45", "R", "1k", "Resistor_SMD:R_0805_2012Metric", 180.0, 60.0, rot=90)
s4.connect_pins("R44", "2", "R45", "1")

s4.add_comp("C29", "C", "10nF", "Capacitor_SMD:C_0805_2012Metric", 190.0, 72.0)
s4.connect_pins("R45", "2", "C29", "1")
s4.connect_pin_stub("C29", "2", "GND", is_pwr=True)

s4.add_comp("C30", "C", "10uF", "Capacitor_SMD:C_0805_2012Metric", 200.0, 60.0, rot=90)
s4.connect_pins("R45", "2", "C30", "1")
s4.connect_pins("C30", "2", "J6", "T") # Tip is EAR_OUT

# Attenuator R46 (10k) / R47 (1k) for MIC_OUT on Ring
s4.add_comp("R46", "R", "10k", "Resistor_SMD:R_0805_2012Metric", 205.0, 75.0)
s4.connect_pins("C30", "2", "R46", "1")
s4.connect_pins("R46", "2", "J6", "R") # Ring

s4.add_comp("R47", "R", "1k", "Resistor_SMD:R_0805_2012Metric", 215.0, 88.0)
s4.connect_pins("J6", "R", "R47", "1")
s4.connect_pin_stub("R47", "2", "GND", is_pwr=True)

# Opto-isolated Remote Motor Control J7 & U10 PC817 at (190.0, 130.0)
s4.add_comp("U10", "PC817", "PC817", "Package_DIP:DIP-4_W7.62mm", 190.0, 130.0)
s4.add_comp("R48", "R", "330", "Resistor_SMD:R_0805_2012Metric", 172.0, 132.54, rot=90)
s4.connect_pin_stub("R48", "1", "REMOTE_DRIVE", is_global=True, shape="input")
s4.connect_pins("R48", "2", "U10", "1") # Anode
s4.connect_pin_stub("U10", "2", "GND", is_pwr=True) # Cathode to GND

s4.add_comp("J7", "AudioJack3", "REMOTE_2.5mm", 
    "Connector_Audio:Jack_3.5mm_CUI_SJ-3523-SMT_Horizontal", 215.0, 130.0)
s4.connect_pins("U10", "4", "J7", "T") # Collector to Tip
s4.connect_pins("U10", "3", "J7", "S") # Emitter to Sleeve
s4.add_no_connect("J7", "R") # Ring unused

with open(os.path.join(kicad_dir, "04_Tape_Interfaces.kicad_sch"), "w", encoding="utf-8") as f:
    f.write(s4.render(page_num="5"))

print("Production Schematics rebuilt with TLV2372, 74HCT06, and Dual TLC5916!")
