import sys; sys.path.append('scripts')
from production_sch_builder import ProductionSheet
s2 = ProductionSheet('s2', 'MCU', 'test')
s2.add_comp('U3', 'RaspberryPi_Pico', 'Pico', 'Module:RaspberryPi_Pico_Common_THT', 160.0, 110.0)
for p in ['1', '2', '3', '16', '17', '18', '21', '22', '24', '25', '33', '38']:
    print(f"Pin {p:2s}: {s2.get_pin('U3', p)}")







