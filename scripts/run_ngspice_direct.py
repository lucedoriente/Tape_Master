import os, sys, ctypes
from ctypes import c_char_p, c_int, c_void_p, CFUNCTYPE, POINTER

ngspice_dll = r"C:\Program Files\KiCad\9.0\bin\ngspice.dll"
lib = ctypes.CDLL(ngspice_dll)

# Callbacks for ngSpice_Init
SendChar = CFUNCTYPE(c_int, c_char_p, c_int, c_void_p)
SendStat = CFUNCTYPE(c_int, c_char_p, c_int, c_void_p)
ControlledExit = CFUNCTYPE(c_int, c_int, c_int, c_int, c_void_p)
SendData = CFUNCTYPE(c_int, c_void_p, c_int, c_void_p)
SendInitData = CFUNCTYPE(c_int, c_void_p, c_int, c_void_p)
BGThreadRunning = CFUNCTYPE(c_int, c_int, c_int, c_void_p)

messages = []

@SendChar
def cb_send_char(msg, ident, user_data):
    messages.append(msg.decode('utf-8', errors='ignore'))
    return 0

@SendStat
def cb_send_stat(msg, ident, user_data):
    return 0

@ControlledExit
def cb_exit(status, immediate, exit_upon_quit, user_data):
    return 0

res = lib.ngSpice_Init(cb_send_char, cb_send_stat, cb_exit, None, None, None, None)
print("Init result:", res)

circuit = [
    "* Sallen-Key 4th Order Bandpass Filter Test",
    "VIN IN 0 DC 0 AC 1.0",
    "VBIAS VBIAS 0 DC 2.5",
    "* High-pass stage: C1=47nF, C2=47nF, R1=8.2k, R2=16k",
    "C1 IN N1 47nF",
    "C2 N1 IN_HP 47nF",
    "R1 N1 OUT_HP 8.2k",
    "R2 IN_HP VBIAS 16k",
    "E1 OUT_HP 0 IN_HP 0 1.0",
    "* Low-pass stage: R1=12k, R2=12k, C1=1.5nF, C2=680pF",
    "R3 OUT_HP N2 12k",
    "R4 N2 IN_LP 12k",
    "C3 N2 OUT_LP 1.5nF",
    "C4 IN_LP VBIAS 680pF",
    "E2 OUT_LP 0 IN_LP 0 1.0",
    ".ac dec 10 10 100k",
    ".end",
    None
]

# Convert to array of pointers
c_circuit = (c_char_p * len(circuit))()
for i, line in enumerate(circuit):
    c_circuit[i] = line.encode('utf-8') if line else None

lib.ngSpice_Circ(c_circuit)
lib.ngSpice_Command(b"run")
lib.ngSpice_Command(b"print vdb(OUT_LP)")

print("\n--- NGSPICE OUTPUT ---")
full_out = "".join(messages)
for line in full_out.splitlines():
    if "frequency" in line.lower() or "vdb(" in line.lower() or any(f"{hz}." in line or f"{hz}0" in line for hz in [50, 300, 1000, 10000, 12000]):
        print(line)
