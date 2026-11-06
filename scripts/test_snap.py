def snap(val, grid=1.27):
    return round(round(val / grid) * grid, 2)

for v in [40.0, 60.0, 70.0, 95.0, 115.0, 160.0]:
    print(f"{v} -> snapped: {snap(v)} (diff: {snap(v)-v:.2f})")
