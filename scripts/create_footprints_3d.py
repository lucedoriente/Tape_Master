import os

fp_dir = os.path.join(os.path.dirname(__file__), "..", "kicad", "Tape-Master.pretty")
models_dir = os.path.join(os.path.dirname(__file__), "..", "kicad", "3dmodels")
os.makedirs(fp_dir, exist_ok=True)
os.makedirs(models_dir, exist_ok=True)

# 1. C2N Edge Connector Footprint (6-pin 3.96mm pitch edge connector + standard pads)
# IMPORTANT RULE: NO lines on Edge.Cuts inside footprints!
# All silkscreen on F.SilkS, courtyard on F.CrtYd, fab on F.Fab
fp_c2n = """(footprint "C2N_Edge_Connector"
	(version 20241223)
	(generator "pcbnew")
	(generator_version "9.0")
	(layer "F.Cu")
	(property "Reference" "REF**"
		(at 9.9 5.5 0)
		(layer "F.SilkS")
		(uuid "5a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d")
		(effects
			(font
				(size 1 1)
				(thickness 0.15)
			)
		)
	)
	(property "Value" "C2N_Edge_Connector"
		(at 9.9 -5.5 0)
		(layer "F.Fab")
		(uuid "6a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d")
		(effects
			(font
				(size 1 1)
				(thickness 0.15)
			)
		)
	)
	(property "Footprint" ""
		(at 0 0 0)
		(layer "F.Cu")
		(hide yes)
		(uuid "7a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d")
		(effects
			(font
				(size 1 1)
				(thickness 0.15)
			)
		)
	)
	(property "Datasheet" "datasheets/C2N_Datassette_Port_Pinout.md"
		(at 0 0 0)
		(layer "F.Cu")
		(hide yes)
		(uuid "8a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d")
		(effects
			(font
				(size 1 1)
				(thickness 0.15)
			)
		)
	)
	(property "Description" "Commodore C2N 6-pin Cassette Edge Connector (3.96mm pitch)"
		(at 0 0 0)
		(layer "F.Cu")
		(hide yes)
		(uuid "9a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d")
		(effects
			(font
				(size 1 1)
				(thickness 0.15)
			)
		)
	)
	(fp_line
		(start -2.5 -4.5)
		(end 22.3 -4.5)
		(stroke
			(width 0.12)
			(type solid)
		)
		(layer "F.SilkS")
		(uuid "11111111-2222-3333-4444-555555555501")
	)
	(fp_line
		(start 22.3 -4.5)
		(end 22.3 4.5)
		(stroke
			(width 0.12)
			(type solid)
		)
		(layer "F.SilkS")
		(uuid "11111111-2222-3333-4444-555555555502")
	)
	(fp_line
		(start 22.3 4.5)
		(end -2.5 4.5)
		(stroke
			(width 0.12)
			(type solid)
		)
		(layer "F.SilkS")
		(uuid "11111111-2222-3333-4444-555555555503")
	)
	(fp_line
		(start -2.5 4.5)
		(end -2.5 -4.5)
		(stroke
			(width 0.12)
			(type solid)
		)
		(layer "F.SilkS")
		(uuid "11111111-2222-3333-4444-555555555504")
	)
	(fp_rect
		(start -3.0 -5.0)
		(end 22.8 5.0)
		(stroke
			(width 0.05)
			(type solid)
		)
		(fill none)
		(layer "F.CrtYd")
		(uuid "11111111-2222-3333-4444-555555555505")
	)
	(pad "1" thru_hole rect
		(at 0 0)
		(size 2.4 3.6)
		(drill 1.2)
		(layers "*.Cu" "*.Mask")
		(uuid "22222222-3333-4444-5555-666666666601")
	)
	(pad "2" thru_hole oval
		(at 3.96 0)
		(size 2.4 3.6)
		(drill 1.2)
		(layers "*.Cu" "*.Mask")
		(uuid "22222222-3333-4444-5555-666666666602")
	)
	(pad "3" thru_hole oval
		(at 7.92 0)
		(size 2.4 3.6)
		(drill 1.2)
		(layers "*.Cu" "*.Mask")
		(uuid "22222222-3333-4444-5555-666666666603")
	)
	(pad "4" thru_hole oval
		(at 11.88 0)
		(size 2.4 3.6)
		(drill 1.2)
		(layers "*.Cu" "*.Mask")
		(uuid "22222222-3333-4444-5555-666666666604")
	)
	(pad "5" thru_hole oval
		(at 15.84 0)
		(size 2.4 3.6)
		(drill 1.2)
		(layers "*.Cu" "*.Mask")
		(uuid "22222222-3333-4444-5555-666666666605")
	)
	(pad "6" thru_hole oval
		(at 19.8 0)
		(size 2.4 3.6)
		(drill 1.2)
		(layers "*.Cu" "*.Mask")
		(uuid "22222222-3333-4444-5555-666666666606")
	)
	(model "${KIPRJMOD}/3dmodels/C2N_Edge_Connector.wrl"
		(offset
			(xyz 0 0 0)
		)
		(scale
			(xyz 1 1 1)
		)
		(rotate
			(xyz 0 0 0)
		)
	)
)
"""

with open(os.path.join(fp_dir, "C2N_Edge_Connector.kicad_mod"), "w", encoding="utf-8") as f:
    f.write(fp_c2n)

# 2. VRML .wrl 3D model for C2N connector
wrl_content = """#VRML V2.0 utf8
# C2N_Edge_Connector VRML Model - Alessio Iodice
Group {
  children [
    Transform {
      translation 9.9 0 4.0
      children [
        Shape {
          appearance Appearance {
            material Material {
              diffuseColor 0.15 0.35 0.55
              specularColor 0.8 0.8 0.8
              shininess 0.5
            }
          }
          geometry Box {
            size 25.0 9.0 8.0
          }
        }
      ]
    }
  ]
}
"""
with open(os.path.join(models_dir, "C2N_Edge_Connector.wrl"), "w", encoding="utf-8") as f:
    f.write(wrl_content)

# 3. STEP .step 3D model for C2N connector
step_content = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('C2N Edge Connector STEP Model'),'2;1');
FILE_NAME('C2N_Edge_Connector.step','2026-11-04T23:00:00',('Alessio Iodice'),('MuDIsTInf'),'KiCad 9.0','KiCad 9.0','');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));
ENDSEC;
DATA;
#1 = APPLICATION_CONTEXT('core data for automotive mechanical design processes');
#2 = APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#1);
#3 = PRODUCT_CONTEXT('part definition',#1,'mechanical');
#4 = PRODUCT('C2N_Edge_Connector','C2N Edge Connector','',(#3));
#5 = PRODUCT_DEFINITION_FORMATION('1','',#4);
#6 = PRODUCT_DEFINITION('design','',#5,#3);
ENDSEC;
END-ISO-10303-21;
"""
with open(os.path.join(models_dir, "C2N_Edge_Connector.step"), "w", encoding="utf-8") as f:
    f.write(step_content)

with open(os.path.join(models_dir, "OLED_0.96_I2C.step"), "w", encoding="utf-8") as f:
    f.write(step_content.replace("C2N_Edge_Connector", "OLED_0.96_I2C"))

print("Custom footprints and 3D models created successfully.")
