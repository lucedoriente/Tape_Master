mod_path = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.pretty\C2N_Edge_Connector.kicad_mod"
with open(mod_path, "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find("(model ")
if idx != -1:
    new_model = """(model "${KIPRJMOD}/3dmodels/C2N_Edge_Connector.wrl"
		(offset (xyz 0 0 0))
		(scale (xyz 1 1 1))
		(rotate (xyz 0 0 0))
	)
	(model "${KIPRJMOD}/3dmodels/C2N_Edge_Connector.step"
		(offset (xyz 0 0 0))
		(scale (xyz 1 1 1))
		(rotate (xyz 0 0 0))
	)
)"""
    text = text[:idx] + new_model
    with open(mod_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("Updated C2N_Edge_Connector.kicad_mod")
