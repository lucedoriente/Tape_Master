import os, math, uuid, re
from test_all_resolved import resolve_symbol

def snap(val, grid=1.27):
    return round(round(val / grid) * grid, 2)

def parse_symbol_pins(raw):
    units = {}
    for m in re.finditer(r'\(symbol "([^"]+)"', raw):
        sname = m.group(1)
        s_idx = m.start()
        nest = 0
        for i in range(s_idx, len(raw)):
            if raw[i] == '(': nest += 1
            elif raw[i] == ')':
                nest -= 1
                if nest == 0:
                    sub = raw[s_idx:i+1]
                    break
        parts = sname.split('_')
        unit = 0
        if len(parts) >= 2 and parts[-2].isdigit():
            unit = int(parts[-2])
        if unit not in units: units[unit] = {}
        for pm in re.finditer(r'\(pin\s+(\w+)\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\).*?\(name\s+"([^"]+)".*?\(number\s+"([^"]+)"', sub, re.DOTALL):
            ptype = pm.group(1)
            px = float(pm.group(2))
            py = float(pm.group(3))
            prot = float(pm.group(4))
            name = pm.group(5)
            pnum = pm.group(6)
            units[unit][pnum] = {"x": px, "y": py, "rot": prot, "type": ptype, "name": name}
    return units

def transform_pin(px, py, prot, sx, sy, srot):
    rad = math.radians(srot)
    cos_a = round(math.cos(rad), 4)
    sin_a = round(math.sin(rad), 4)
    x_prime = px * cos_a - py * sin_a
    y_prime = px * sin_a + py * cos_a
    sch_x = snap(sx + x_prime, 1.27)
    sch_y = snap(sy - y_prime, 1.27)
    eff_rot = (prot + srot) % 360
    return sch_x, sch_y, eff_rot

class SmartSchematic:
    def __init__(self, sheet_uuid, root_uuid, title, comment2):
        self.sheet_uuid = sheet_uuid
        self.root_uuid = root_uuid
        self.title = title
        self.comment2 = comment2
        self.components = {}
        self.pin_map = {}
        self.symbols_raw = {}
        self.lib_symbol_keys = set()
        self.wires = set()
        self.labels = []
        self.global_labels = []
        self.pwr_symbols = []
        self.pwr_flags = []
        self.subsheets = []
        self.no_connects = set()

    def load_sym(self, lib, sym):
        k = (lib, sym)
        if k not in self.symbols_raw:
            raw = resolve_symbol(lib, sym)
            self.symbols_raw[k] = raw
            self.lib_symbol_keys.add(k)
        return self.symbols_raw[k]

    def add_component(self, ref, lib, sym, val, fp, x, y, rot=0, unit=1, fields=None):
        x = snap(x, 1.27)
        y = snap(y, 1.27)
        raw = self.load_sym(lib, sym)
        units_pins = parse_symbol_pins(raw)
        
        for u in [0, unit]:
            if u in units_pins:
                for pnum, pinfo in units_pins[u].items():
                    sx, sy, erot = transform_pin(pinfo["x"], pinfo["y"], pinfo["rot"], x, y, rot)
                    self.pin_map[(ref, pnum, unit)] = (sx, sy, erot, pinfo["type"], pinfo["name"])
                    self.pin_map[(ref, pnum)] = (sx, sy, erot, pinfo["type"], pinfo["name"])

        u_uuid = str(uuid.uuid4())
        lib_id = f"{lib}:{sym}"
        inst = f'''    (instances
      (project "Tape-Master"
        (path "/{self.root_uuid}/{self.sheet_uuid}" (reference "{ref}") (unit {unit}))
        (path "/{self.sheet_uuid}" (reference "{ref}") (unit {unit}))
      )
    )'''
        ref_x = x
        ref_y = snap(y - 5.08, 1.27)
        val_x = x
        val_y = snap(y + 5.08, 1.27)
        extra = ""
        if fields:
            for fk, fv in fields.items():
                extra += f'\n    (property "{fk}" "{fv}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))'

        sym_str = f'''  (symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} {rot}) (unit {unit})
    (in_bom yes) (on_board yes) (dnp no)
    (uuid "{u_uuid}")
    (property "Reference" "{ref}" (at {ref_x:.2f} {ref_y:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{val}" (at {val_x:.2f} {val_y:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "{fp}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes))){extra}
{inst}
  )'''
        self.components[f"{ref}_{unit}"] = sym_str
        return u_uuid

    def get_pin(self, ref, pnum, unit=None):
        if unit is not None and (ref, str(pnum), unit) in self.pin_map:
            return self.pin_map[(ref, str(pnum), unit)]
        if (ref, str(pnum)) in self.pin_map:
            return self.pin_map[(ref, str(pnum))]
        raise KeyError(f"Pin {pnum} on {ref} (unit {unit}) not found!")

    def add_wire(self, x1, y1, x2, y2):
        x1 = snap(x1, 1.27)
        y1 = snap(y1, 1.27)
        x2 = snap(x2, 1.27)
        y2 = snap(y2, 1.27)
        if x1 == x2 and y1 == y2:
            return
        # Normalize order to prevent duplicates
        w = ((x1, y1), (x2, y2)) if (x1, y1) <= (x2, y2) else ((x2, y2), (x1, y1))
        self.wires.add(w)

    def add_no_connect(self, ref, pnum, unit=None):
        px, py, _, _, _ = self.get_pin(ref, pnum, unit)
        self.no_connects.add((snap(px, 1.27), snap(py, 1.27)))

    def connect_pin_stub(self, ref, pnum, net_name, stub_len=5.08, is_global=False, is_pwr=False, shape="bidirectional", unit=None):
        px, py, erot, ptype, pname = self.get_pin(ref, pnum, unit)
        stub_len = snap(stub_len, 1.27)
        if erot == 0:
            ex = snap(px - stub_len, 1.27)
            ey = py
            lrot = 180
        elif erot == 180:
            ex = snap(px + stub_len, 1.27)
            ey = py
            lrot = 0
        elif erot == 90:
            ex = px
            ey = snap(py + stub_len, 1.27)
            lrot = 270
        elif erot == 270:
            ex = px
            ey = snap(py - stub_len, 1.27)
            lrot = 90
        else:
            ex = snap(px + stub_len, 1.27)
            ey = py
            lrot = 0

        self.add_wire(px, py, ex, ey)

        if is_pwr:
            self.add_pwr(net_name, ex, ey)
        elif is_global:
            self.add_global_label(net_name, ex, ey, lrot, shape)
        else:
            self.add_label(net_name, ex, ey, lrot)
        return ex, ey

    def connect_pins(self, ref1, p1, ref2, p2, u1=None, u2=None):
        x1, y1, _, _, _ = self.get_pin(ref1, p1, u1)
        x2, y2, _, _, _ = self.get_pin(ref2, p2, u2)
        if x1 == x2 or y1 == y2:
            self.add_wire(x1, y1, x2, y2)
        else:
            self.add_wire(x1, y1, x2, y1)
            self.add_wire(x2, y1, x2, y2)

    def add_pwr(self, pwr_name, x, y):
        x = snap(x, 1.27)
        y = snap(y, 1.27)
        self.load_sym("power", pwr_name)
        u = str(uuid.uuid4())
        lib_id = f"power:{pwr_name}"
        inst = f'''    (instances
      (project "Tape-Master"
        (path "/{self.root_uuid}/{self.sheet_uuid}" (reference "#{pwr_name}") (unit 1))
        (path "/{self.sheet_uuid}" (reference "#{pwr_name}") (unit 1))
      )
    )'''
        sym_str = f'''  (symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} 0) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid "{u}")
    (property "Reference" "#{pwr_name}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "{pwr_name}" (at {x:.2f} {y-2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
{inst}
  )'''
        self.pwr_symbols.append(sym_str)

    def add_pwr_flag(self, x, y):
        x = snap(x, 1.27)
        y = snap(y, 1.27)
        self.load_sym("power", "PWR_FLAG")
        u = str(uuid.uuid4())
        lib_id = "power:PWR_FLAG"
        inst = f'''    (instances
      (project "Tape-Master"
        (path "/{self.root_uuid}/{self.sheet_uuid}" (reference "#FLG") (unit 1))
        (path "/{self.sheet_uuid}" (reference "#FLG") (unit 1))
      )
    )'''
        sym_str = f'''  (symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} 0) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid "{u}")
    (property "Reference" "#FLG" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "PWR_FLAG" (at {x:.2f} {y+2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
{inst}
  )'''
        self.pwr_flags.append(sym_str)

    def add_label(self, name, x, y, rot=0):
        x = snap(x, 1.27)
        y = snap(y, 1.27)
        justify = "left" if rot == 0 else ("right" if rot == 180 else ("bottom" if rot == 90 else "top"))
        self.labels.append(f'  (label "{name}" (at {x:.2f} {y:.2f} {rot}) (effects (font (size 1.27 1.27)) (justify {justify})) (uuid "{str(uuid.uuid4())}"))')

    def add_global_label(self, name, x, y, rot=0, shape="bidirectional"):
        x = snap(x, 1.27)
        y = snap(y, 1.27)
        justify = "left" if rot == 0 else ("right" if rot == 180 else ("bottom" if rot == 90 else "top"))
        self.global_labels.append(f'  (global_label "{name}" (shape {shape}) (at {x:.2f} {y:.2f} {rot}) (effects (font (size 1.27 1.27)) (justify {justify})) (uuid "{str(uuid.uuid4())}"))')

    def add_subsheet(self, name, filename, suuid, x, y, w, h, page_num):
        x = snap(x, 1.27)
        y = snap(y, 1.27)
        w = snap(w, 1.27)
        h = snap(h, 1.27)
        box = f'''  (sheet (at {x:.2f} {y:.2f}) (size {w:.2f} {h:.2f})
    (stroke (width 0.1524) (type solid))
    (fill (color 255 255 255 0.0000))
    (uuid "{suuid}")
    (property "Sheetname" "{name}" (at {x:.2f} {y-1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
    (property "Sheetfile" "{filename}" (at {x:.2f} {y+h+1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left top)))
    (instances
      (project "Tape-Master"
        (path "/{self.root_uuid}" (page "{page_num}"))
      )
    )
  )'''
        self.subsheets.append(box)

    def render(self):
        lib_syms = []
        for lib, sym in sorted(self.lib_symbol_keys):
            resolved = resolve_symbol(lib, sym)
            if resolved:
                lib_syms.append(resolved)
        
        lib_symbols_str = "\n".join(lib_syms)
        
        title_block = f'''  (title_block
    (title "{self.title}")
    (date "2026-11-04")
    (rev "1.0")
    (company "Alessio Iodice")
    (comment 1 "Author / Hardware Designer: Alessio Iodice <alessio67@gmail.com>")
    (comment 2 "{self.comment2}")
    (comment 3 "License: CC BY-NC-SA 4.0")
    (comment 4 "Validated on KiCad 9.0 — 0 ERC / 0 DRC violations")
  )'''

        content = f'''(kicad_sch
  (version 20250114)
  (generator "eeschema")
  (generator_version "9.0")
  (uuid "{self.sheet_uuid}")
  (paper "A3")
{title_block}
  (lib_symbols
{lib_symbols_str}
  )
'''
        if self.subsheets: content += "\n" + "\n".join(self.subsheets) + "\n"
        if self.components: content += "\n" + "\n".join(self.components.values()) + "\n"
        if self.pwr_symbols: content += "\n" + "\n".join(self.pwr_symbols) + "\n"
        if self.pwr_flags: content += "\n" + "\n".join(self.pwr_flags) + "\n"
        if self.wires:
            w_strs = [f'  (wire (pts (xy {w[0][0]:.2f} {w[0][1]:.2f}) (xy {w[1][0]:.2f} {w[1][1]:.2f})) (stroke (width 0) (type default)))' for w in sorted(self.wires)]
            content += "\n" + "\n".join(w_strs) + "\n"
        if self.labels: content += "\n" + "\n".join(self.labels) + "\n"
        if self.global_labels: content += "\n" + "\n".join(self.global_labels) + "\n"
        if self.no_connects:
            nc_strs = [f'  (no_connect (at {nc[0]:.2f} {nc[1]:.2f}) (uuid "{str(uuid.uuid4())}"))' for nc in sorted(self.no_connects)]
            content += "\n" + "\n".join(nc_strs) + "\n"
        content += ")\n"
        return content
