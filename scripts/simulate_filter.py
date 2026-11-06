import numpy as np

# Component values:
# HPF Sallen-Key 2nd-order:
# C1 = C2 = 47 nF
# R1 = 8.2k, R2 = 16k
# fc_hpf = 1 / (2*pi * sqrt(R1*R2) * C)
C_h = 47e-9
R1_h = 8.2e3
R2_h = 16e3

fc_hpf = 1.0 / (2 * np.pi * np.sqrt(R1_h * R2_h) * C_h)
Q_hpf = 0.5 * np.sqrt(R2_h / R1_h)

# LPF Sallen-Key 2nd-order:
# R1 = R2 = 12k
# C1 = 1.5 nF, C2 = 680 pF
R_l = 12e3
C1_l = 1.5e-9
C2_l = 680e-12

fc_lpf = 1.0 / (2 * np.pi * R_l * np.sqrt(C1_l * C2_l))
Q_lpf = 0.5 * np.sqrt(C1_l / C2_l)

print(f"HPF: fc = {fc_hpf:.1f} Hz, Q = {Q_hpf:.3f}")
print(f"LPF: fc = {fc_lpf:.1f} Hz, Q = {Q_lpf:.3f}")

# Frequency response evaluation:
freqs = [20, 50, 100, 300, 400, 1000, 3000, 5000, 8000, 10000, 12000, 20000, 50000]

def hpf_resp(f):
    w = 2 * np.pi * f
    s = 1j * w
    # H_hpf(s) = s^2 / (s^2 + s*(1/(R2*C1) + 1/(R2*C2)) + 1/(R1*R2*C1*C2))
    # with C1=C2=C: denominator = s^2 + s*(2/(R2*C)) + 1/(R1*R2*C^2)
    den = s**2 + s * (2.0 / (R2_h * C_h)) + 1.0 / (R1_h * R2_h * C_h**2)
    num = s**2
    return num / den

def lpf_resp(f):
    w = 2 * np.pi * f
    s = 1j * w
    # H_lpf(s) = (1/(R1*R2*C1*C2)) / (s^2 + s*(1/(R1*C1) + 1/(R2*C1)) + 1/(R1*R2*C1*C2))
    # with R1=R2=R:
    w0_sq = 1.0 / (R_l**2 * C1_l * C2_l)
    den = s**2 + s * (2.0 / (R_l * C1_l)) + w0_sq
    return w0_sq / den

print("\nFrequency Response of Cascaded Bandpass Filter:")
print(f"{'Freq (Hz)':<10} | {'HPF (dB)':<10} | {'LPF (dB)':<10} | {'Total (dB)':<10}")
print("-" * 46)
for f in freqs:
    H_h = hpf_resp(f)
    H_l = lpf_resp(f)
    H_tot = H_h * H_l
    db_h = 20 * np.log10(np.abs(H_h))
    db_l = 20 * np.log10(np.abs(H_l))
    db_tot = 20 * np.log10(np.abs(H_tot))
    print(f"{f:<10} | {db_h:>8.2f} dB | {db_l:>8.2f} dB | {db_tot:>8.2f} dB")

print(f"\nHum Attenuation at 50 Hz: {-20 * np.log10(np.abs(hpf_resp(50) * lpf_resp(50))):.2f} dB")
