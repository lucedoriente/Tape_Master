import shutil, os, subprocess, re

src_dir = r'C:\Program Files\KiCad\9.0\share\kicad\demos\flat_hierarchy'
if os.path.exists('kicad/test_flat_dir'):
    shutil.rmtree('kicad/test_flat_dir')
shutil.copytree(src_dir, 'kicad/test_flat_dir')

cmd = [r'C:\Program Files\KiCad\9.0\bin\kicad-cli.exe', 'sch', 'export', 'netlist', 'kicad/test_flat_dir/flat_hierarchy.kicad_sch', '-o', 'kicad/test_flat_dir/out.net']
res = subprocess.run(cmd, capture_output=True, text=True)
print('flat_hierarchy copy netlist export exit code:', res.returncode)

with open('kicad/test_flat_dir/out.net') as f:
    text = f.read()

comps = re.findall(r'\(comp\s+\(ref "([^"]+)"\)', text)
print('Components count in copy:', len(comps))
