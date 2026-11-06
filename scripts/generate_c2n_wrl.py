# Script to generate realistic C2N_Edge_Connector VRML model
import os

vrml_content = """#VRML V2.0 utf8
# Commodore C2N 6-pin (12-contact) 3.96mm Pitch Edge Connector Model
# Author: Alessio Iodice for MuDIsTInf / Tape Master Exerciser
# Scale 0.39370079 (1mm = 0.39370079 units)

Transform {
  scale 0.39370079 0.39370079 0.39370079
  children [

    # --- Main Connector Housing (Commodore Blue Nylon) ---
    # Bottom Base
    Transform {
      translation 9.9 0.0 2.25
      children [
        Shape {
          appearance Appearance {
            material DEF C2N_HOUSING Material {
              diffuseColor 0.12 0.30 0.52
              specularColor 0.35 0.45 0.55
              shininess 0.35
            }
          }
          geometry Box { size 24.8 9.0 4.5 }
        }
      ]
    }

    # Left Wall of Card Slot
    Transform {
      translation 9.9 -2.85 8.0
      children [
        Shape {
          appearance Appearance { material USE C2N_HOUSING }
          geometry Box { size 24.8 3.3 7.0 }
        }
      ]
    }

    # Right Wall of Card Slot
    Transform {
      translation 9.9 2.85 8.0
      children [
        Shape {
          appearance Appearance { material USE C2N_HOUSING }
          geometry Box { size 24.8 3.3 7.0 }
        }
      ]
    }

    # Left End Wall
    Transform {
      translation -1.4 0.0 8.0
      children [
        Shape {
          appearance Appearance { material USE C2N_HOUSING }
          geometry Box { size 2.2 2.4 7.0 }
        }
      ]
    }

    # Right End Wall
    Transform {
      translation 21.2 0.0 8.0
      children [
        Shape {
          appearance Appearance { material USE C2N_HOUSING }
          geometry Box { size 2.2 2.4 7.0 }
        }
      ]
    }

    # Polarizing Key Notch Tab (Between Pin 2 at 3.96 and Pin 3 at 7.92 -> X = 5.94)
    Transform {
      translation 5.94 0.0 7.5
      children [
        Shape {
          appearance Appearance { material USE C2N_HOUSING }
          geometry Box { size 1.6 2.4 6.0 }
        }
      ]
    }

    # --- 6 Solder Tail Contact Pins (Through Board, Phosphor Bronze/Gold) ---
"""

# Add the 6 contact pins and leaf springs
pins_x = [0.0, 3.96, 7.92, 11.88, 15.84, 19.80]
for i, px in enumerate(pins_x, 1):
    vrml_content += f"""
    # Pin {i} Solder Tail (under PCB)
    Transform {{
      translation {px:.2f} 0.0 -1.0
      children [
        Shape {{
          appearance Appearance {{
            material DEF GOLD_PIN Material {{
              diffuseColor 0.85 0.72 0.30
              specularColor 0.95 0.90 0.60
              shininess 0.85
            }}
          }}
          geometry Box {{ size 0.8 0.8 4.0 }}
        }}
      ]
    }}

    # Pin {i} Internal Leaf Contact - Side A
    Transform {{
      translation {px:.2f} -1.0 6.5
      children [
        Shape {{
          appearance Appearance {{ material USE GOLD_PIN }}
          geometry Box {{ size 0.6 0.3 5.0 }}
        }}
      ]
    }}

    # Pin {i} Internal Leaf Contact - Side B
    Transform {{
      translation {px:.2f} 1.0 6.5
      children [
        Shape {{
          appearance Appearance {{ material USE GOLD_PIN }}
          geometry Box {{ size 0.6 0.3 5.0 }}
        }}
      ]
    }}
"""

vrml_content += """
  ]
}
"""

out_path = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\3dmodels\C2N_Edge_Connector.wrl"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(vrml_content)
print(f"Wrote {out_path}, size={os.path.getsize(out_path)} bytes")
