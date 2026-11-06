with open('scripts/build_full_production_system.py', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'U3' in l and ('connect_pin_stub' in l or 'connect_pins' in l or 'no_connect' in l):
        print(f'{i+1}: {l.strip()}')
