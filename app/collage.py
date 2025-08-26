from PIL import Image
import os

def generate_collage(photo_paths, output_path, logo_path=None, config=None):
    if len(photo_paths) != 3:
        print("🛑 Expected exactly 3 photo paths")
        raise ValueError("Expected exactly 3 photo paths")

    config = config or {}
    canvas_size = tuple(config.get("canvas_size", (2400, 3600)))
    grid = tuple(config.get("grid", (2, 2)))

    collage = Image.new("RGB", canvas_size, "white")
    cell_width = canvas_size[0] // grid[0]
    cell_height = canvas_size[1] // grid[1]

    positions = [
        (0, 0),               # Top left
        (cell_width, 0),      # Top right
        (0, cell_height),     # Bottom left
        (cell_width, cell_height)  # Bottom right (logo)
    ]

    for i, photo_path in enumerate(photo_paths):
        img = Image.open(photo_path)
        img = img.resize((cell_width, cell_height), Image.LANCZOS)
        collage.paste(img, positions[i])

    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path)
        logo = logo.resize((cell_width, cell_height), Image.LANCZOS)
        collage.paste(logo, positions[3])
    else:
        from PIL import ImageDraw
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