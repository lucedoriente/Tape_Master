with open(r'C:\Program Files\KiCad\9.0\share\kicad\demos\flat_hierarchy\pic_programmer.kicad_sch') as f:
    demo = f.read()

with open('kicad/01_Power_Supply.kicad_sch') as f:
    ours = f.read()

import re

# Compare a symbol instance
m_demo = re.search(r'\(symbol\s+.*?\(instances.*?\n\t+\)\n\t+\)', demo, re.DOTALL)
m_ours = re.search(r'\(symbol\s+.*?\(instances.*?\n\s+\)\n\s+\)', ours, re.DOTALL)

print("=== Demo symbol instance ===")
if m_demo:
    print(m_demo.group(0))

print("\n=== Our symbol instance ===")
if m_ours:
    print(m_ours.group(0))
