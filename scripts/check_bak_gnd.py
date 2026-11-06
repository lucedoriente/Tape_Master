import pcbnew

pcb_bak = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\temp_bak.kicad_pcb"
board = pcbnew.LoadBoard(pcb_bak)

gnd_tracks = [t for t in board.GetTracks() if t.GetNetname() == "GND"]
gnd_vias = [t for t in gnd_tracks if isinstance(t, pcbnew.PCB_VIA)]
print(f"Original board GND tracks: {len(gnd_tracks)}, GND vias: {len(gnd_vias)}")
print(f"Total tracks in bak: {len(board.GetTracks())}")
