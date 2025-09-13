# test.py
import tomllib

from app.config import (
    APP_ROOT,  
    CONFIG,
    STYLE_PATH,
    STYLE_ROOT,
    EVENT_BASE_PATH,
)

print("🛠 CONFIG PATHS")
print(f"APP_ROOT:        {APP_ROOT}")
print(f"STYLE_ROOT:      {STYLE_ROOT}")
print(f"STYLE_PATH:      {STYLE_PATH}")
print(f"EVENT_BASE_PATH: {EVENT_BASE_PATH}")
print()

print("📂 CONFIG CONTENTS")
for section, settings in CONFIG.items():
    print(f"[{section}]")
    if isinstance(settings, dict):
        for key, value in settings.items():
            print(f"{key} = {value}")
    else:
        print(f"{section} = {settings}")
    print()

print("📘 EDITABLE KEYS")
editable_keys_path = APP_ROOT / "app" / "editable_keys.cfg"

if not editable_keys_path.exists():
    print("❌ editable_keys.cfg not found.")
else:
    with editable_keys_path.open("rb") as f:
        editable = tomllib.load(f)

    for section, keys in editable.items():
        print(f"[{section}]")
        for key, setting_type in keys.items():
            current_value = CONFIG.get(section, {}).get(key, None)
            print(f"{key} ({setting_type}) = {current_value}")
