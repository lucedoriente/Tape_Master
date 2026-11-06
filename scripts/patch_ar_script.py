with open(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\scripts\auto_route_production_board.py", "r", encoding="utf-8") as f:
    text = f.read()

# Fix zone removal to keep keepout zones
text = text.replace("for z in list(board.Zones()):\n    board.Remove(z)",
                    "for z in list(board.Zones()):\n    if not z.GetIsKeepout():\n        board.Remove(z)")

# Add 3D fix call at end
if "apply_3d_fixes" not in text:
    text = text.replace("print(\"Routed board saved to:\", pcb_path)",
"""print(\"Routed board saved to:\", pcb_path)
import apply_3d_fixes
print(\"3D models re-verified.\")""")

with open(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\scripts\auto_route_production_board.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated auto_route_production_board.py")
