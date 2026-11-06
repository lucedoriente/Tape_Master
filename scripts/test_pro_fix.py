import subprocess

with open('kicad/test_single/test_single.kicad_pro', 'w', encoding='utf-8') as f:
    f.write('{"meta": {"filename": "test_single.kicad_pro", "version": 3}, "sheets": [["a1000000-0000-4000-8000-000000000001", "Root"]]}')

res = subprocess.run([r'C:\Program Files\KiCad\9.0\bin\kicad-cli.exe', 'sch', 'erc', 'kicad/test_single/test_single.kicad_sch'], capture_output=True, text=True)
print('Exit code:', res.returncode)
print('stdout:', res.stdout)
print('stderr:', res.stderr)
