import os, subprocess, sys, shutil
from pathlib import Path

kicad_cli = r"C:\Program Files\KiCad\9.0\bin\kicad-cli.exe"
prj_dir = Path(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad")
sch_file = prj_dir / "Tape-Master.kicad_sch"
pcb_file = prj_dir / "Tape-Master.kicad_pcb"
gerber_dir = prj_dir / "gerbers"
render_dir = prj_dir / "renders"
art_dir = Path(r"C:\Users\aless\.gemini\antigravity\brain\e4725c83-ea1a-4d3e-98e3-4ebaff3f7cb6")

gerber_dir.mkdir(exist_ok=True)
render_dir.mkdir(exist_ok=True)

print("1. Exporting schematic PDF...")
subprocess.run([kicad_cli, "sch", "export", "pdf", "-o", str(prj_dir / "Tape-Master-Schematic.pdf"), str(sch_file)], check=True)

print("2. Exporting netlist...")
subprocess.run([kicad_cli, "sch", "export", "netlist", "-o", str(prj_dir / "Tape-Master.net"), str(sch_file)], check=True)

print("3. Exporting BOM...")
subprocess.run([kicad_cli, "sch", "export", "bom", "-o", str(prj_dir / "bom.csv"), str(sch_file)], check=True)

print("4. Exporting Gerbers...")
subprocess.run([
    kicad_cli, "pcb", "export", "gerbers",
    "-o", str(gerber_dir) + os.sep,
    "--layers", "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts",
    str(pcb_file)
], check=True)

print("5. Exporting Excellon drill files...")
subprocess.run([
    kicad_cli, "pcb", "export", "drill",
    "-o", str(gerber_dir) + os.sep,
    "--format", "excellon",
    "--drill-origin", "absolute",
    str(pcb_file)
], check=True)

print("6. Rendering 3D Top View PNG...")
top_png = render_dir / "Tape-Master-3D-top.png"
subprocess.run([
    kicad_cli, "pcb", "render",
    "--width", "1920", "--height", "1080",
    "--side", "top",
    "--quality", "high",
    "-o", str(top_png),
    str(pcb_file)
], check=True)
if art_dir.exists():
    shutil.copyfile(top_png, art_dir / "Tape-Master-3D-top.png")

print("7. Rendering 3D Isometric View PNG...")
iso_png = render_dir / "Tape-Master-3D-iso.png"
subprocess.run([
    kicad_cli, "pcb", "render",
    "--width", "1920", "--height", "1080",
    "--rotate", "45,0,45",
    "--perspective",
    "--quality", "high",
    "-o", str(iso_png),
    str(pcb_file)
], check=True)
if art_dir.exists():
    shutil.copyfile(iso_png, art_dir / "Tape-Master-3D-iso.png")

print("8. Exporting 3D STEP mechanical model...")
subprocess.run([
    kicad_cli, "pcb", "export", "step",
    "-o", str(prj_dir / "Tape-Master.step"),
    str(pcb_file)
], check=True)

print("All production deliverables exported successfully!")
