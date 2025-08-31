import os
import shutil
import tomllib

# Get absolute project root
APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Config paths
DEFAULT_CONFIG_PATH = os.path.join(APP_ROOT, "app/config.cfg")
USER_CONFIG_PATH = os.path.join(APP_ROOT, "user_config.cfg")

# Use user config if it exists; otherwise, copy default to create it
if not os.path.exists(USER_CONFIG_PATH):
    shutil.copy(DEFAULT_CONFIG_PATH, USER_CONFIG_PATH)

# Load config (always from user_config.cfg)
with open(USER_CONFIG_PATH, "rb") as f:
    CONFIG = tomllib.load(f)

# Core paths
LAST_SESSION_FILE = os.path.join(APP_ROOT, "last_session.txt")

# Section references
SETTINGS_CONFIG   = CONFIG.get("settings", {})
CAMERA_CONFIG     = CONFIG.get("camera", {})
CAMERAS_CONFIG    = CONFIG.get("cameras", {})
CAMERA1_CONFIG    = CONFIG.get("camera1", {})
CAMERA2_CONFIG    = CONFIG.get("camera2", {})
IDLE_CONFIG       = CONFIG.get("idle_screen", {})
PHOTO_CONFIG      = CONFIG.get("photo", {})
COLLAGE_CONFIG    = CONFIG.get("collage", {})
STYLE_CONFIG      = CONFIG.get("style", {})
EMAIL_CONFIG      = CONFIG.get("email", {})
PRINTER_CONFIG    = CONFIG.get("printer", {})
LIGHTS_CONFIG     = CONFIG.get("lights", {})

# Derived paths
EVENT_BASE_PATH = os.path.join(APP_ROOT, SETTINGS_CONFIG.get("base_event_path", "events"))
EVENT_LOADED = os.path.join(APP_ROOT, SETTINGS_CONFIG.get("current_event", "default"))
STYLE_ROOT = os.path.join(APP_ROOT, STYLE_CONFIG.get("style_path", "app/styles"))
STYLE_PATH = os.path.join(APP_ROOT, STYLE_CONFIG.get("style_path", "app/styles"), STYLE_CONFIG.get("style_dir", "default"))

print("config.py: APP_ROOT: ", APP_ROOT)
print("config.py: EVENT_BASE_PATH: ", EVENT_BASE_PATH)
print("config.py: EVENT_LOADED: ", EVENT_LOADED)

EVENT_COMPS = os.path.join(APP_ROOT, SETTINGS_CONFIG.get("base_event_path", "events"), SETTINGS_CONFIG.get("event_loaded", "default"), PHOTO_CONFIG.get("composite_path", "comps"))

# DEBUG
#print(EVENT_COMPS)