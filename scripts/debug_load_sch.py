import subprocess

with open('kicad/01_Power_Supply.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

idx_lib_symbols = text.find('(lib_symbols')
nest = 0
idx_lib_end = -1
for i in range(idx_lib_symbols, len(text)):
    if text[i] == '(': nest += 1
    elif text[i] == ')':
        nest -= 1
        if nest == 0:
            idx_lib_end = i + 1
            break

print(f"lib_symbols byte range: {idx_lib_symbols} to {idx_lib_end}")

def test_snippet(snippet):
    content = snippet
    if not content.strip().endswith(')'):
        content += "\n)"
    with open('kicad/test_min.kicad_sch', 'w', encoding='utf-8') as tf:
        tf.write(content)
    res = subprocess.run([r'C:\Program Files\KiCad\9.0\bin\kicad-cli.exe', 'sch', 'erc', 'kicad/test_min.kicad_sch'], capture_output=True, text=True)
    return res.returncode == 0, res.stdout, res.stderr

# What if we test with Tape-Master.kicad_sch?
res = subprocess.run([r'C:\Program Files\KiCad\9.0\bin\kicad-cli.exe', 'sch', 'erc', 'kicad/Tape-Master.kicad_sch'], capture_output=True, text=True)
print("Tape-Master.kicad_sch ERC exit code:", res.returncode)


