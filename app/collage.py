from PIL import Image, ImageDraw
import os
from typing import List, Optional
from app.config import EVENT_BASE_PATH, CONFIG, COLLAGE_CONFIG

def generate_collage(
    photo_paths: List[str],
    output_path: str,
    logo_path: Optional[str] = None,
    config: Optional[dict] = None
) -> str:
    if len(photo_paths) != 3:
        raise ValueError("🛑 Expected exactly 3 photo paths, got {}".format(len(photo_paths)))

    config = COLLAGE_CONFIG
    canvas_size = tuple(config.get("canvas_size", (2400, 3600)))  # 4x6 portrait
    grid = tuple(config.get("grid", (2, 2)))  # default 2x2 grid

    collage = Image.new("RGB", canvas_size, "white")
    cell_width = canvas_size[0] // grid[0]
    cell_height = canvas_size[1] // grid[1]

    positions = [
        (0, 0),               # Top left
        (cell_width, 0),      # Top right
        (0, cell_height),     # Bottom left
        (cell_width, cell_height)  # Bottom right (logo)
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
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGB")
            logo = logo.resize((cell_width, cell_height), Image.LANCZOS)
            collage.paste(logo, positions[3])
        except Exception as e:
            print(f"⚠️ Failed to load logo: {e}")
    else:
        draw = ImageDraw.Draw(collage)
        draw.rectangle(
            [positions[3],
             (positions[3][0] + cell_width, positions[3][1] + cell_height)],
            outline="black", width=3
        )
        draw.text((positions[3][0] + 20, positions[3][1] + 20),
                  "LOGO HERE", fill="black")

    collage.save(output_path)
    print("✅ Collage saved:", output_path)
    return output_path