"""
Tape Master Studio - Application Configuration Manager
Handles persistent JSON configuration for AI settings, window geometry, and hardware preferences.
Author: Alessio Iodice <alessio67@gmail.com>
License: CC BY-NC-SA 4.0
"""

import os
import sys
import json

DEFAULT_CONFIG = {
    "version": "2.0",
    "ai": {
        "backend": "gemini",
        "gemini_model": "gemini-2.0-flash",
        "gemini_api_key": "",
        "ollama_model": "qwen2.5-coder:14b",
    },
    "window": {
        "width": 1280,
        "height": 840,
        "active_tab": 3,
    },
    "serial": {
        "last_port": "",
    },
}

def get_config_dir() -> str:
    """Returns directory where configuration file is stored: strictly in the executable's folder."""
    if getattr(sys, 'frozen', False):
        # PyInstaller standalone executable: strictly in the same directory as .exe
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        # Script execution: tools/Tape_Master_Studio/
        core_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(core_dir)

def get_config_file_path() -> str:
    """Returns absolute path to tape_master_config.json."""
    return os.path.join(get_config_dir(), "tape_master_config.json")

def load_config() -> dict:
    """Loads configuration from JSON file or returns defaults."""
    path = get_config_file_path()
    config = dict(DEFAULT_CONFIG)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Deep merge with defaults
                for section, vals in data.items():
                    if isinstance(vals, dict) and section in config:
                        config[section].update(vals)
                    else:
                        config[section] = vals
        except Exception as e:
            print(f"[CONFIG] Warning: could not parse {path}: {e}")
    else:
        # Check if GEMINI_API_KEY is available in environment
        env_key = os.environ.get("GEMINI_API_KEY", "")
        if env_key:
            config["ai"]["gemini_api_key"] = env_key
        # Save default configuration immediately so the user can inspect/edit it
        save_config(config)
    return config

def save_config(config: dict) -> bool:
    """Saves configuration dict to JSON file."""
    path = get_config_file_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[CONFIG] Error saving {path}: {e}")
        return False
