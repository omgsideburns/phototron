import os
import tomllib

# Get absolute project root
APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load the config.toml file
CONFIG_PATH = os.path.join(APP_ROOT, "config.cfg")
with open(CONFIG_PATH, "rb") as f:
    CONFIG = tomllib.load(f)

# Extract and resolve core paths
EVENT_BASE_PATH = os.path.join(APP_ROOT, CONFIG.get("base_event_path", "events"))
LAST_SESSION_FILE = os.path.join(APP_ROOT, "last_session.txt")

# Camera and photo settings
CAMERA_CONFIG = CONFIG.get("camera", {})
PHOTO_CONFIG = CONFIG.get("photo", {})
COLLAGE_CONFIG = CONFIG.get("collage", {})

# Style Config
STYLE_CONFIG = CONFIG.get("style", {})
STYLE_PATH = os.path.join(APP_ROOT, CONFIG.get("style_path", "app/styles"))

# Email Config
EMAIL_CONFIG = CONFIG.get("email", {})

# Printer Config
PRINTER_CONFIG = CONFIG.get("printer", {})

# Lights Config
LIGHTS_CONFIG = CONFIG.get("lights", {})
