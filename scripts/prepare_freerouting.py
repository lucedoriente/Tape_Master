import os, json

paths = [
    os.path.expandvars(r"%LOCALAPPDATA%\Temp\freerouting\freerouting.json"),
    os.path.expandvars(r"%APPDATA%\freerouting\freerouting.json"),
    os.path.expandvars(r"%LOCALAPPDATA%\freerouting\freerouting.json")
]

for p in paths:
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "gui" not in data:
                data["gui"] = {}
            data["gui"]["enabled"] = False
            with open(p, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"Set gui.enabled = false in {p}")
        except Exception as e:
            print(f"Error updating {p}: {e}")
    else:
        # Create directory and file if it does not exist
        os.makedirs(os.path.dirname(p), exist_ok=True)
        data = {"gui": {"enabled": False}}
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Created {p} with gui.enabled = false")
