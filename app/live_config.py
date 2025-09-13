import tomllib
import tomli_w
from app.config import USER_CONFIG_PATH  # already a Path

def load_user_config() -> dict:
    if USER_CONFIG_PATH.exists():
        with USER_CONFIG_PATH.open("rb") as f:
            return tomllib.load(f)
    return {}

def save_user_config(data: dict) -> None:
    USER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with USER_CONFIG_PATH.open("wb") as f:
        tomli_w.dump(data, f)
