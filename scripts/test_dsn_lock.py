import pcbnew, os

board = pcbnew.LoadBoard(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb")

# Lock all existing tracks
for tr in board.GetTracks():
    tr.SetLocked(True)

temp_dsn = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\test_lock.dsn"
pcbnew.ExportSpecctraDSN(board, temp_dsn)

with open(temp_dsn, "r", encoding="utf-8") as f:
    text = f.read()

import re
print("Has (type protect):", "(type protect" in text or "(protect" in text or "fix" in text)
matches = re.findall(r'\(wire\s+[\s\S]*?\)', text)
if matches:
    print("Sample wire:", matches[0])
