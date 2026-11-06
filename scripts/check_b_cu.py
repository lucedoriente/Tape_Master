import pcbnew

pcb_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb"
board = pcbnew.LoadBoard(pcb_file)

b_tracks = [t for t in board.GetTracks() if t.GetLayerName() == "B.Cu"]
print(f"Total tracks on B.Cu: {len(b_tracks)}")
nets = set(t.GetNetname() for t in b_tracks)
print("Nets on B.Cu:", sorted(nets))
