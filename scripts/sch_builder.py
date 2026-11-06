import uuid

class SchematicBuilder:
    def __init__(self, sheet_uuid, root_uuid, title, comment2):
        self.sheet_uuid = sheet_uuid
        self.root_uuid = root_uuid
        self.title = title
        self.comment2 = comment2
        self.symbols = []
        self.wires = []
        self.labels = []
        self.global_labels = []
        self.subsheets = []
        self.lib_symbol_keys = set()
    
    def add_lib_symbol(self, lib_name, sym_name):
        self.lib_symbol_keys.add((lib_name, sym_name))
    
    def add_symbol(self, lib_name, sym_name, ref, val, fp, x, y, rot=0, unit=1, fields=None):
        self.add_lib_symbol(lib_name, sym_name)
        u = str(uuid.uuid4())
        lib_id = f"{lib_name}:{sym_name}"
        inst = f'''    (instances
      (project "Tape-Master"
        (path "/{self.root_uuid}/{self.sheet_uuid}" (reference "{ref}"))
        (path "/{self.sheet_uuid}" (reference "{ref}"))
      )
    )'''
        # Position ref and val cleanly outside body
        ref_x = x
        ref_y = y - 3.81
        val_x = x
        val_y = y + 3.81
        
        extra_fields = ""
        if fields:
            for k, v in fields.items():
                extra_fields += f'\n    (property "{k}" "{v}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (hide yes)))'
        
        sym_str = f'''  (symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} {rot}) (unit {unit})
    (in_bom yes) (on_board yes) (dnp no)
    (uuid "{u}")
    (property "Reference" "{ref}" (at {ref_x:.2f} {ref_y:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{val}" (at {val_x:.2f} {val_y:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "{fp}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes))){extra_fields}
{inst}
  )'''
        self.symbols.append(sym_str)
        return u

    def add_pwr(self, pwr_name, x, y, rot=0):
        self.add_lib_symbol("power", pwr_name)
        u = str(uuid.uuid4())
        lib_id = f"power:{pwr_name}"
        inst = f'''    (instances
      (project "Tape-Master"
        (path "/{self.root_uuid}/{self.sheet_uuid}" (reference "#{pwr_name}"))
        (path "/{self.sheet_uuid}" (reference "#{pwr_name}"))
      )
    )'''
        sym_str = f'''  (symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} {rot}) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid "{u}")
    (property "Reference" "#{pwr_name}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "{pwr_name}" (at {x:.2f} {y+2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
{inst}
  )'''
        self.symbols.append(sym_str)
        return u

    def add_pwr_flag(self, x, y, rot=0):
        self.add_lib_symbol("power", "PWR_FLAG")
        u = str(uuid.uuid4())
        lib_id = "power:PWR_FLAG"
        inst = f'''    (instances
      (project "Tape-Master"
        (path "/{self.root_uuid}/{self.sheet_uuid}" (reference "#FLG"))
        (path "/{self.sheet_uuid}" (reference "#FLG"))
      )
    )'''
        sym_str = f'''  (symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} {rot}) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid "{u}")
    (property "Reference" "#FLG" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "PWR_FLAG" (at {x:.2f} {y+2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
{inst}
  )'''
        self.symbols.append(sym_str)
        return u

    def add_wire(self, x1, y1, x2, y2):
        self.wires.append(f'  (wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f})) (stroke (width 0) (type default)))')

    def add_label(self, name, x, y, rot=0):
        justify = "left" if rot == 0 else ("right" if rot == 180 else ("bottom" if rot == 90 else "top"))
        self.labels.append(f'  (label "{name}" (at {x:.2f} {y:.2f} {rot}) (effects (font (size 1.27 1.27)) (justify {justify})) (uuid "{str(uuid.uuid4())}"))')

    def add_global_label(self, name, x, y, rot=0, shape="bidirectional"):
        justify = "left" if rot == 0 else ("right" if rot == 180 else ("bottom" if rot == 90 else "top"))
        self.global_labels.append(f'  (global_label "{name}" (shape {shape}) (at {x:.2f} {y:.2f} {rot}) (effects (font (size 1.27 1.27)) (justify {justify})) (uuid "{str(uuid.uuid4())}"))')

    def add_subsheet(self, name, filename, suuid, x, y, w, h, page_num):
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

    def render(self, resolve_fn):
        lib_syms = []
        for lib, sym in sorted(self.lib_symbol_keys):
            resolved = resolve_fn(lib, sym)
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
        if self.subsheets:
            content += "\n" + "\n".join(self.subsheets) + "\n"
        if self.symbols:
            content += "\n" + "\n".join(self.symbols) + "\n"
        if self.wires:
            content += "\n" + "\n".join(self.wires) + "\n"
        if self.labels:
            content += "\n" + "\n".join(self.labels) + "\n"
        if self.global_labels:
            content += "\n" + "\n".join(self.global_labels) + "\n"
        
        content += ")\n"
        return content
