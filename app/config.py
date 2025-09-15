from pathlib import Path
import shutil
import tomllib

# Note: I'm trying to use this to pull alllllll configs across the board
# so that the global vars are used and making sweeping changes to the config
# structure in the future won't break stray variables but it's getting harder.
# most paths are derived at the bottom but others may
# be created from parts in their respective files..
# I need to add default-directory creation into one file instead of being spread out...

# Get absolute project root
APP_ROOT = Path(__file__).resolve().parent.parent

# Config paths
DEFAULT_CONFIG_PATH = APP_ROOT / "app" / "config.cfg"
USER_CONFIG_PATH = APP_ROOT / "app" / "user_config.cfg"

# Use user config if it exists; otherwise, copy default to create it
if not USER_CONFIG_PATH.exists():
    shutil.copy(DEFAULT_CONFIG_PATH, USER_CONFIG_PATH)

# Load config (always from user_config.cfg)
with USER_CONFIG_PATH.open("rb") as f:
    CONFIG = tomllib.load(f)

# Section references
SETTINGS_CONFIG = CONFIG.get("settings", {})
CAMERA_CONFIG = CONFIG.get("camera", {})
CAMERAS_CONFIG = CONFIG.get("cameras", {})
CAMERA1_CONFIG = CONFIG.get("camera1", {})
CAMERA2_CONFIG = CONFIG.get("camera2", {})
IDLE_CONFIG = CONFIG.get("idle_screen", {})
PHOTO_CONFIG = CONFIG.get("photo", {})
COLLAGE_CONFIG = CONFIG.get("collage", {})  # deprecate or repurpose...
STYLE_CONFIG = CONFIG.get("style", {})
EMAIL_CONFIG = CONFIG.get("email", {})
PRINTER_CONFIG = CONFIG.get("printer", {})
LIGHTS_CONFIG = CONFIG.get("lights", {})

# Derived paths - these are recursive and rely on each other and the order they are declared.. don't be a dumbass.
EVENT_BASE_PATH = APP_ROOT / SETTINGS_CONFIG.get("base_event_path", "events")
# Support both legacy key "current_event" and current key "event_loaded"
_event_name = SETTINGS_CONFIG.get("event_loaded") or SETTINGS_CONFIG.get(
    "current_event", "default"
)
EVENT_LOADED = EVENT_BASE_PATH / _event_name
STYLE_ROOT = APP_ROOT / STYLE_CONFIG.get("style_path", "app/styles")
STYLE_PATH = STYLE_ROOT / STYLE_CONFIG.get("style_dir", "default")
STYLE_FILE = STYLE_PATH / "style.qss"
TEMPLATE_PATH = STYLE_PATH / "template.toml"  # photo layout template

EVENT_RAW = EVENT_LOADED / PHOTO_CONFIG.get("raw_path", "raw")
EVENT_COMPS = EVENT_LOADED / PHOTO_CONFIG.get("composite_path", "comps")

# DEBUG
# print(EVENT_COMPS)
