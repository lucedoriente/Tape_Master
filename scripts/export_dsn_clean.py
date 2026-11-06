import os
import pcbnew

kicad_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kicad"))
pcb_file = os.path.join(kicad_dir, "Tape-Master.kicad_pcb")

def strip_sexpr_tag(s, tag):
    out = []
    i = 0
    n = len(s)
    tag_str = '(' + tag
    while i < n:
        if s[i:i+len(tag_str)] == tag_str and (i == 0 or s[i-1] in ' \t\r\n'):
            depth = 1
            j = i + len(tag_str)
            while j < n and depth > 0:
                if s[j] == '"':
                    j += 1
                    while j < n and s[j] != '"':
                        if s[j] == '\\':
                            j += 2
                        else:
                            j += 1
                    j += 1
                    continue
                elif s[j] == '(':
                    depth += 1
                elif s[j] == ')':
                    depth -= 1
                j += 1
            while j < n and s[j] in ' \t':
                j += 1
            if j < n and s[j] == '\n':
                j += 1
            i = j
        else:
            out.append(s[i])
            i += 1
    return ''.join(out)

with open(pcb_file, 'r', encoding='utf-8') as f:
    text = f.read()

cleaned = strip_sexpr_tag(text, 'fp_arc')
cleaned = strip_sexpr_tag(cleaned, 'group')
temp_pcb = os.path.join(kicad_dir, 'temp_no_arcs.kicad_pcb')
with open(temp_pcb, 'w', encoding='utf-8') as f:
    f.write(cleaned)

b = pcbnew.LoadBoard(temp_pcb)
print('Board loaded, footprints count:', len(b.Footprints()))

dsn_path = os.path.join(kicad_dir, 'Tape-Master.dsn')
res = pcbnew.ExportSpecctraDSN(b, dsn_path)
print('DSN Export result:', res, 'Size:', os.path.getsize(dsn_path))
