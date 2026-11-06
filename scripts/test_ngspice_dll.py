import os, ctypes

ngspice_dll = r"C:\Program Files\KiCad\9.0\bin\ngspice.dll"
try:
    lib = ctypes.CDLL(ngspice_dll)
    print("ngspice.dll loaded successfully:", lib)
    # Check ngspice exported functions
    for func in ["ngSpice_Init", "ngSpice_Command", "ngSpice_Circ"]:
        if hasattr(lib, func):
            print(f"Found {func}")
except Exception as e:
    print("Failed to load ngspice.dll:", e)
