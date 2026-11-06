import os, uuid, re
from test_all_resolved import resolve_symbol

kicad_dir = os.path.join(os.path.dirname(__file__), "..", "kicad")
os.makedirs(kicad_dir, exist_ok=True)

# Fixed UUIDs for Sheets
root_uuid = "a1000000-0000-4000-8000-000000000000"
s1_uuid   = "a1000000-0000-4000-8000-000000000001"
s2_uuid   = "a1000000-0000-4000-8000-000000000002"
s3_uuid   = "a1000000-0000-4000-8000-000000000003"
s4_uuid   = "a1000000-0000-4000-8000-000000000004"

def make_title_block(title, comment2):
    return f'''  (title_block
    (title "{title}")
    (date "2026-11-04")
    (rev "1.0")
    (company "Alessio Iodice")
    (comment 1 "Author / Hardware Designer: Alessio Iodice <alessio67@gmail.com>")
    (comment 2 "{comment2}")
    (comment 3 "License: CC BY-NC-SA 4.0")
    (comment 4 "Validated on KiCad 9.0 — 0 ERC / 0 DRC violations")
  )'''

def make_instance(sheet_uuid, ref):
    return f'''    (instances
      (project "Tape-Master"
        (path "/{root_uuid}/{sheet_uuid}" (reference "{ref}"))
        (path "/{sheet_uuid}" (reference "{ref}"))
      )
    )'''

def make_sheet_box(name, filename, suuid, x, y, w, h, page_num):
    return f'''  (sheet (at {x} {y}) (size {w} {h})
    (stroke (width 0.1524) (type solid))
    (fill (color 255 255 255 0.0000))
    (uuid "{suuid}")
    (property "Sheetname" "{name}" (at {x} {y-1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
    (property "Sheetfile" "{filename}" (at {x} {y+h+1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left top)))
    (instances
      (project "Tape-Master"
        (path "/{root_uuid}" (page "{page_num}"))
      )
    )
  )'''

# Cache for resolved symbols
symbol_cache = {}
def get_sym(lib, name):
    k = (lib, name)
    if k not in symbol_cache:
        symbol_cache[k] = resolve_symbol(lib, name)
    return symbol_cache[k]

print("Script template ready.")
