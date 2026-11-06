analog_path = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\03_Analog_Ingest.kicad_sch"
with open(analog_path, "r", encoding="utf-8") as f:
    text = f.read()

# Replace all remaining local labels "TAPE_FILTERED" with global_label
text = text.replace('(label "TAPE_FILTERED" (at 116.84 137.16 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "e6e36496-4f8b-4412-a251-5b59e4915ca6"))',
                    '(global_label "TAPE_FILTERED" (shape input) (at 116.84 137.16 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "e6e36496-4f8b-4412-a251-5b59e4915ca6"))')

text = text.replace('(label "TAPE_FILTERED" (at 30.48 199.39 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "42237091-7dbd-49bc-a482-d303f2f74127"))',
                    '(global_label "TAPE_FILTERED" (shape input) (at 30.48 199.39 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "42237091-7dbd-49bc-a482-d303f2f74127"))')

with open(analog_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Converted all TAPE_FILTERED labels to global_label in 03_Analog_Ingest")
