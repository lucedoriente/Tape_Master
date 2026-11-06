import os

kicad_dir = os.path.join(os.path.dirname(__file__), "..", "kicad")
os.makedirs(kicad_dir, exist_ok=True)
sym_path = os.path.join(kicad_dir, "Tape-Master.kicad_sym")

sym_content = """(kicad_symbol_lib
	(version 20241209)
	(generator "kicad_symbol_editor")
	(generator_version "9.0")
	(symbol "C2N_Connector"
		(pin_names
			(offset 1.016)
		)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(property "Reference" "J"
			(at -7.62 10.16 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left)
			)
		)
		(property "Value" "C2N_Connector"
			(at -7.62 7.62 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left)
			)
		)
		(property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Datasheet" "datasheets/C2N_Datassette_Port_Pinout.md"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Description" "Commodore C2N 6-pin Cassette Port Interface (GND, +5V, MOTOR, READ, WRITE, SENSE)"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(symbol "C2N_Connector_0_1"
			(rectangle
				(start -7.62 6.35)
				(end 7.62 -11.43)
				(stroke
					(width 0.254)
					(type solid)
				)
				(fill
					(type background)
				)
			)
		)
		(symbol "C2N_Connector_1_1"
			(pin power_out line
				(at -10.16 5.08 0)
				(length 2.54)
				(name "GND"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin power_out line
				(at -10.16 2.54 0)
				(length 2.54)
				(name "+5V"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "2"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin input line
				(at -10.16 0 0)
				(length 2.54)
				(name "MOTOR"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "3"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin open_collector line
				(at 10.16 -2.54 180)
				(length 2.54)
				(name "READ"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "4"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin input line
				(at -10.16 -5.08 0)
				(length 2.54)
				(name "WRITE"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "5"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin open_collector line
				(at 10.16 -7.62 180)
				(length 2.54)
				(name "SENSE"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "6"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
		)
	)
	(symbol "OLED_0.96_I2C"
		(pin_names
			(offset 1.016)
		)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(property "Reference" "DISP"
			(at -6.35 7.62 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left)
			)
		)
		(property "Value" "OLED_0.96_I2C"
			(at -6.35 5.08 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left)
			)
		)
		(property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Datasheet" "https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf"
			(at 0 0 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(symbol "OLED_0.96_I2C_0_1"
			(rectangle
				(start -6.35 3.81)
				(end 6.35 -8.89)
				(stroke
					(width 0.254)
					(type solid)
				)
				(fill
					(type background)
				)
			)
		)
		(symbol "OLED_0.96_I2C_1_1"
			(pin power_in line
				(at -8.89 2.54 0)
				(length 2.54)
				(name "GND"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin power_in line
				(at -8.89 0 0)
				(length 2.54)
				(name "VCC"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "2"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin input line
				(at -8.89 -2.54 0)
				(length 2.54)
				(name "SCL"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "3"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin bidirectional line
				(at -8.89 -5.08 0)
				(length 2.54)
				(name "SDA"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "4"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
		)
	)
)
"""

with open(sym_path, "w", encoding="utf-8") as f:
    f.write(sym_content)

print(f"Created {sym_path}")
