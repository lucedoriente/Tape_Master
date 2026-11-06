import os, re

symbols_dir = r"C:\Program Files\KiCad\9.0\share\kicad\symbols"

def get_symbol_raw(lib_name, sym_name):
    path = os.path.join(symbols_dir, f"{lib_name}.kicad_sym")
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    target = f'(symbol "{sym_name}"'
    s = text.find(target)
    if s == -1: return None
    nest = 0
    for i in range(s, len(text)):
        if text[i] == '(': nest += 1
        elif text[i] == ')':
            nest -= 1
            if nest == 0:
                return text[s:i+1]
    return None

def resolve_symbol(lib_name, sym_name):
    raw = get_symbol_raw(lib_name, sym_name)
    if not raw: return None
    m = re.search(r'\(extends "([^"]+)"\)', raw)
    if not m:
        # Not derived, return as is with library prefix
        return raw.replace(f'(symbol "{sym_name}"', f'(symbol "{lib_name}:{sym_name}"', 1)
    
    parent_name = m.group(1)
    parent_raw = get_symbol_raw(lib_name, parent_name)
    if not parent_raw:
        # Check other libs or return parent included
        return raw
    
    # Extract sub-symbols (graphics and pins) from parent
    # Sub-symbols look like: (symbol "LM2904_1_1" ...)
    sub_syms = []
    for sub in re.finditer(rf'\(symbol "{parent_name}_([^"]+)"', parent_raw):
        s_idx = sub.start()
        nest = 0
        for i in range(s_idx, len(parent_raw)):
            if parent_raw[i] == '(': nest += 1
            elif parent_raw[i] == ')':
                nest -= 1
                if nest == 0:
                    sub_body = parent_raw[s_idx:i+1]
                    # Rename parent prefix to derived symbol prefix
                    sub_body_renamed = sub_body.replace(f'(symbol "{parent_name}_', f'(symbol "{sym_name}_')
                    sub_syms.append(sub_body_renamed)
                    break
    
    # Remove (extends "...") from raw
    cleaned = re.sub(r'\s*\(extends "[^"]+"\)', '', raw)
    # Insert sub_syms before the last closing paren
    last_paren = cleaned.rfind(')')
    full = cleaned[:last_paren] + "\n\t\t" + "\n\t\t".join(sub_syms) + "\n\t)"
    return full.replace(f'(symbol "{sym_name}"', f'(symbol "{lib_name}:{sym_name}"', 1)

res = resolve_symbol("Amplifier_Operational", "NE5532")
print("Resolved NE5532:", res[:400], "...\nLength:", len(res))
m_ext = re.search(r'\(extends', res)
print("Has extends?", bool(m_ext))
