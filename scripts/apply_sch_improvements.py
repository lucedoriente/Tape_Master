import re

# 1. Update 01_Power_Supply.kicad_sch
psu_path = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\01_Power_Supply.kicad_sch"
with open(psu_path, "r", encoding="utf-8") as f:
    psu = f.read()

psu = psu.replace('(property "Value" "BAT54C" (at 95.25 64.77 0)', '(property "Value" "PMEG3010AET" (at 95.25 64.77 0)')
psu = psu.replace('(property "Value" "100uF" (at 115.57 64.77 0)', '(property "Value" "100uF_Polymer" (at 115.57 64.77 0)')

with open(psu_path, "w", encoding="utf-8") as f:
    f.write(psu)
print("Updated 01_Power_Supply.kicad_sch")

# 2. Update 03_Analog_Ingest.kicad_sch
analog_path = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\03_Analog_Ingest.kicad_sch"
with open(analog_path, "r", encoding="utf-8") as f:
    analog = f.read()

# Replace local label at 87.63 139.70 with global_label
target_label = '(label "TAPE_FILTERED" (at 87.63 139.70 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "401c5cf6-d333-43de-a7a5-552c1bb0d0cb"))'
replacement = '(global_label "TAPE_FILTERED" (shape output) (at 87.63 139.70 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "401c5cf6-d333-43de-a7a5-552c1bb0d0cb"))'

if target_label in analog:
    analog = analog.replace(target_label, replacement)
    print("Replaced TAPE_FILTERED label with global_label in 03_Analog_Ingest")
else:
    print("Target label not found exactly, searching via regex...")
    analog = re.sub(r'\(label\s+"TAPE_FILTERED"\s+\(at\s+87\.63\s+139\.70\s+0\)\s+\(effects\s+\(font\s+\(size\s+1\.27\s+1\.27\)\)\s+\(justify\s+left\)\)\s+\(uuid\s+"[^"]+"\)\)',
                    replacement, analog)

with open(analog_path, "w", encoding="utf-8") as f:
    f.write(analog)

# 3. Update 02_MCU_Core.kicad_sch
mcu_path = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\02_MCU_Core.kicad_sch"
with open(mcu_path, "r", encoding="utf-8") as f:
    mcu = f.read()

# Remove no_connect at 182.88 137.16
nc_target = '(no_connect (at 182.88 137.16) (uuid "58e48222-7ba4-47d6-bd84-36ace4b549b1"))'
if nc_target in mcu:
    mcu = mcu.replace(nc_target, "")
    print("Removed no_connect at (182.88, 137.16)")
else:
    mcu = re.sub(r'\(no_connect\s+\(at\s+182\.88\s+137\.16\)\s+\(uuid\s+"[^"]+"\)\)', '', mcu)
    print("Removed no_connect via regex")

# Add wire and global_label for TAPE_FILTERED
wire_str = '  (wire (pts (xy 182.88 137.16) (xy 187.96 137.16)) (stroke (width 0) (type default)))\n'
glabel_str = '  (global_label "TAPE_FILTERED" (shape input) (at 187.96 137.16 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "d8f1025a-4e2b-4231-97b0-7ba4d1b82028"))\n'

# Insert before closing paren of the schematic
idx_end = mcu.rfind(')')
mcu = mcu[:idx_end] + wire_str + glabel_str + mcu[idx_end:]

with open(mcu_path, "w", encoding="utf-8") as f:
    f.write(mcu)
print("Updated 02_MCU_Core.kicad_sch")
