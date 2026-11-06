import os, sys, re, pcbnew
from pathlib import Path

ses_file = Path('kicad/Tape-Master.ses')
content = ses_file.read_text(encoding="utf-8")

# Sanitize SES
if "(lock_type position)" in content:
    content = content.replace("(lock_type position)", "")

# Strip component placements
content = re.sub(
    r"(\(placement\b[\s\S]*?)(?:\s*\(\s*component[\s\S]*?\n\s*\)\s*)+(?=\))",
    r"\1",
    content,
)

clean_ses = Path('kicad/Tape-Master-clean.ses')
clean_ses.write_text(content, encoding="utf-8")
print("Sanitized SES written.")

board = pcbnew.LoadBoard('kicad/Tape-Master.kicad_pcb')
print("Loaded board, tracks before import:", len(board.GetTracks()))

ok = pcbnew.ImportSpecctraSES(board, str(clean_ses.resolve()))
print("ImportSpecctraSES result:", ok)
print("Tracks after import:", len(board.GetTracks()))

# Save routed board
board.Save('kicad/Tape-Master.kicad_pcb')
print("Board saved successfully.")
