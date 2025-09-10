from pathlib import Path
import shutil
import tomllib

# Get absolute project root
APP_ROOT = Path(__file__).resolve().parent.parent

# Config paths
DEFAULT_CONFIG_PATH = APP_ROOT / "app" / "config.cfg"
USER_CONFIG_PATH    = APP_ROOT / "app" / "user_config.cfg"

# Use user config if it exists; otherwise, copy default to create it
if not USER_CONFIG_PATH.exists():
    shutil.copy(DEFAULT_CONFIG_PATH, USER_CONFIG_PATH)

# Load config (always from user_config.cfg)
with USER_CONFIG_PATH.open("rb") as f:
    CONFIG = tomllib.load(f)

# LAST_SESSION_FILE deprecated, now using "event_loaded" var in config.
LAST_SESSION_FILE = APP_ROOT / "last_session.txt"

# Section references
SETTINGS_CONFIG = CONFIG.get("settings", {})
CAMERA_CONFIG   = CONFIG.get("camera", {})
CAMERAS_CONFIG  = CONFIG.get("cameras", {})
CAMERA1_CONFIG  = CONFIG.get("camera1", {})
CAMERA2_CONFIG  = CONFIG.get("camera2", {})
IDLE_CONFIG     = CONFIG.get("idle_screen", {})
PHOTO_CONFIG    = CONFIG.get("photo", {})
COLLAGE_CONFIG  = CONFIG.get("collage", {})
STYLE_CONFIG    = CONFIG.get("style", {})
EMAIL_CONFIG    = CONFIG.get("email", {})
PRINTER_CONFIG  = CONFIG.get("printer", {})
LIGHTS_CONFIG   = CONFIG.get("lights", {})

# Derived paths
EVENT_BASE_PATH = APP_ROOT / SETTINGS_CONFIG.get("base_event_path", "events")
EVENT_LOADED    = EVENT_BASE_PATH / SETTINGS_CONFIG.get("current_event", "default")
STYLE_ROOT      = APP_ROOT / STYLE_CONFIG.get("style_path", "app/styles")
STYLE_PATH      = STYLE_ROOT / STYLE_CONFIG.get("style_dir", "default")

EVENT_COMPS = APP_ROOT / EVENT_BASE_PATH / EVENT_LOADED / PHOTO_CONFIG.get("composite_path", "comps")

# DEBUG
# print(EVENT_COMPS)
