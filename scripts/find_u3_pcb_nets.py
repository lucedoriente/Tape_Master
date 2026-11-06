sch_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\02_MCU_Core.kicad_sch"
with open(sch_file, "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = re.findall(r'\(symbol\s+"([^"]*Pico[^"]*)"[\s\S]*?\n    \)', text)
print("Matches:", len(matches))
if matches:
    print(matches[0][:500])

# Or let's see what nets are connected to U3 pads in Tape-Master.kicad_pcb!
import pcbnew
board = pcbnew.LoadBoard(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb")
u3 = board.FindFootprintByReference("U3")
print("=== U3 Pads and Nets from PCB ===")
for p in u3.Pads():
    print(f"Pin {p.GetPadName():2s}: Net = {p.GetNetname()}")
