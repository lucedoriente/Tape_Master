import os

fp_dir = r"C:\Program Files\KiCad\9.0\share\kicad\footprints\Connector_Audio.pretty"
if os.path.exists(fp_dir):
    for f in os.listdir(fp_dir):
        if "3.5" in f or "2.5" in f:
            print(f)
