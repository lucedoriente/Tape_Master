import pcbnew, os, sys

board = pcbnew.LoadBoard("kicad/Tape-Master.kicad_pcb")

# Check all footprints and their courtyards / bounding boxes
fps = list(board.Footprints())
print(f"Total footprints: {len(fps)}")

# Print Pico info
pico = board.FindFootprintByReference("U3")
if pico:
    bb = pico.GetBoundingBox()
    print(f"Pico pos: ({pico.GetPosition().x/1e6:.2f}, {pico.GetPosition().y/1e6:.2f})")
    print(f"Pico bbox: ({bb.GetX()/1e6:.2f}, {bb.GetY()/1e6:.2f}) to ({bb.GetRight()/1e6:.2f}, {bb.GetBottom()/1e6:.2f})")

# Check which footprints overlap
overlaps = []
for i in range(len(fps)):
    fp1 = fps[i]
    bb1 = fp1.GetBoundingBox()
    for j in range(i + 1, len(fps)):
        fp2 = fps[j]
        bb2 = fp2.GetBoundingBox()
        if bb1.Intersects(bb2):
            overlaps.append((fp1.GetReference(), fp2.GetReference()))

print(f"Total bounding box intersections: {len(overlaps)}")
print("Sample overlaps:", overlaps[:10])
