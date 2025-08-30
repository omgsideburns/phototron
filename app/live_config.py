import os
import tomllib
import tomli_w
from app.config import APP_ROOT, USER_CONFIG_PATH

def load_user_config():
    if os.path.exists(USER_CONFIG_PATH):
        with open(USER_CONFIG_PATH, "rb") as f:
            return tomllib.load(f)
    return {}

def save_user_config(data: dict):
    with open(USER_CONFIG_PATH, "wb") as f:
        tomli_w.dump(data, f)
