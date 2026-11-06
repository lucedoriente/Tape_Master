import subprocess

with open('kicad/test_single/test_single.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.splitlines()

# We know minimal header + sheet_instances loads
# Let's find the closing of lib_symbols
idx_lib_symbols = -1
for i, l in enumerate(lines):
    if l.strip() == '(lib_symbols':
        idx_lib_symbols = i
        break

idx_lib_end = -1
nest = 0
for i in range(idx_lib_symbols, len(lines)):
    for char in lines[i]:
        if char == '(': nest += 1
        elif char == ')':
            nest -= 1
            if nest == 0:
                idx_lib_end = i
                break
    if idx_lib_end != -1:
        break

print(f"lib_symbols lines: {idx_lib_symbols} to {idx_lib_end}")

def check_lines(selected_lines):
    content = "\n".join(selected_lines)
    if not content.strip().endswith(')'):
        content += "\n  (sheet_instances\n    (path \"/\" (page \"1\"))\n  )\n)\n"
    with open('kicad/test_single/test_single.kicad_sch', 'w', encoding='utf-8') as f:
        f.write(content)
    res = subprocess.run([r'C:\Program Files\KiCad\9.0\bin\kicad-cli.exe', 'sch', 'erc', 'kicad/test_single/test_single.kicad_sch'], capture_output=True, text=True)
    return res.returncode == 0 or "violations" in res.stdout

# Test without lib_symbols (empty lib_symbols)
header_only = lines[:idx_lib_symbols] + ['  (lib_symbols)', '  )']
print("Header only loads:", check_lines(header_only))

# Test header + lib_symbols
header_with_libs = lines[:idx_lib_end+1]
print("Header + lib_symbols loads:", check_lines(header_with_libs))
