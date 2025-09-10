from pathlib import Path
from typing import List, Optional

from PIL import Image, ImageDraw

from app.config import COLLAGE_CONFIG


def generate_collage(
    photo_paths: List[Path] | List[str],
    output_path: Path | str,
    logo_path: Optional[Path | str] = None,
    config: Optional[dict] = None,
) -> Path:
    """
    Generate a 4x6 portrait collage with 3 photos and a logo/placeholder.
    """
    photo_paths = [Path(p) for p in photo_paths]
    output_path = Path(output_path)
    logo_path = Path(logo_path) if logo_path else None

    if len(photo_paths) != 3:
        raise ValueError(f"🛑 Expected exactly 3 photo paths, got {len(photo_paths)}")

    config = COLLAGE_CONFIG if config is None else config
    canvas_size = tuple(config.get("canvas_size", (2400, 3600)))  # 4x6 portrait
    grid = tuple(config.get("grid", (2, 2)))  # default 2x2 grid

    collage = Image.new("RGB", canvas_size, "white")
    cell_width = canvas_size[0] // grid[0]
    cell_height = canvas_size[1] // grid[1]

    positions = [
        (0, 0),  # Top left
        (cell_width, 0),  # Top right
        (0, cell_height),  # Bottom left
        (cell_width, cell_height),  # Bottom right (logo)
    ]

    # Paste photos
    for i, photo_path in enumerate(photo_paths):
        try:
            img = Image.open(photo_path).convert("RGB")
            img = img.resize((cell_width, cell_height), Image.LANCZOS)
            collage.paste(img, positions[i])
        except Exception as e:
            print(f"❌ Error loading photo {photo_path}: {e}")

    # Add logo or placeholder
    if logo_path and logo_path.exists():
        try:
            logo = Image.open(logo_path).convert("RGB")
            logo = logo.resize((cell_width, cell_height), Image.LANCZOS)
            collage.paste(logo, positions[3])
        except Exception as e:
            print(f"⚠️ Failed to load logo: {e}")
    else:
        draw = ImageDraw.Draw(collage)
        draw.rectangle(
            [
                positions[3],
                (positions[3][0] + cell_width, positions[3][1] + cell_height),
            ],
            outline="black",
            width=3,
        )
        draw.text(
            (positions[3][0] + 20, positions[3][1] + 20),
            "LOGO HERE",
            fill="black",
        )

    collage.save(output_path)
    print("✅ Collage saved:", output_path)
    return output_path
