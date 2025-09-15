# app/collage.py
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from PIL import Image, ImageDraw

from app.collage_renderer import render_collage
from app.config import EVENT_LOADED, TEMPLATE_PATH


def generate_collage(
    photo_paths: List[Path] | List[str],
    output_path: Path | str,
    logo_path: Optional[Path | str] = None,
    config: Optional[dict] = None,
) -> Path:
    # Prefer template, fallback to standard render otherwise
    photo_paths = [Path(p) for p in photo_paths]
    output_path = Path(output_path)
    logo_path = Path(logo_path) if logo_path else None

    if len(photo_paths) != 3:
        raise ValueError(f"🛑 Expected exactly 3 photo paths, got {len(photo_paths)}")

    tpl = TEMPLATE_PATH

    shots = {
        "shot1": Image.open(photo_paths[0]).convert("RGB"),
        "shot2": Image.open(photo_paths[1]).convert("RGB"),
        "shot3": Image.open(photo_paths[2]).convert("RGB"),
    }

    # EVENT_NAME from EVENT_LOADED folder name if available
    if EVENT_LOADED:
        event_name = Path(EVENT_LOADED).name
    else:
        event_name = (config or {}).get("event_name", "Event")

    # SESSION_ID from photo filename prefix (e.g., "0007-01.jpg" -> "0007")
    m = re.match(r"^(\d{4})-", photo_paths[0].name)
    session_id = m.group(1) if m else (config or {}).get("session_id", "0000")

    variables = {
        "EVENT_NAME": event_name,
        "SESSION_ID": session_id,
        # placeholders for now... may add to settings
    }

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    render_collage(str(tpl), shots, variables, str(output_path))
    print(f"✅ Collage saved (template): {output_path}")
    return output_path

    # Deprecate this... calls up the old way to composite. use 'if tpl'
    # No template.toml next to the style then use legacy layout
    # print("No template.toml alongside style; using legacy collage.")
    # return _legacy_collage(photo_paths, output_path, logo_path, cfg)


# will remove this eventually... this is a fallback in case the template is broken.


def _legacy_collage(
    photo_paths: list[Path],
    output_path: Path,
    logo_path: Optional[Path],
    cfg: dict,
) -> Path:
    """
    Previous behavior: simple 2x2 (3 photos + logo/placeholder).
    Keeps you running if no template is present.
    """
    canvas_size = tuple(cfg.get("canvas_size", (2400, 3600)))  # 4x6 portrait
    grid = tuple(cfg.get("grid", (2, 2)))
    collage = Image.new("RGB", canvas_size, "white")
    cell_w = canvas_size[0] // grid[0]
    cell_h = canvas_size[1] // grid[1]

    positions = [
        (0, 0),  # Top-left
        (cell_w, 0),  # Top-right
        (0, cell_h),  # Bottom-left
        (cell_w, cell_h),  # Bottom-right (logo/placeholder)
    ]

    # First three slots = photos
    for i, p in enumerate(photo_paths[:3]):
        img = Image.open(p).convert("RGB")
        img = img.resize((cell_w, cell_h), Image.LANCZOS)
        collage.paste(img, positions[i])

    # Last slot = logo or placeholder
    if logo_path and Path(logo_path).exists():
        try:
            logo = Image.open(logo_path).convert("RGB")
            logo = logo.resize((cell_w, cell_h), Image.LANCZOS)
            collage.paste(logo, positions[3])
        except Exception as e:
            print(f"⚠️ Failed to load logo: {e}")
    else:
        draw = ImageDraw.Draw(collage)
        x0, y0 = positions[3]
        draw.rectangle([(x0, y0), (x0 + cell_w, y0 + cell_h)], outline="black", width=3)
        draw.text((x0 + 20, y0 + 20), "LOGO HERE", fill="black")

    collage.save(output_path)
    print("✅ Collage saved (legacy):", output_path)
    return output_path
