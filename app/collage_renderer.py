# app/collage_renderer.py
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Mapping

import tomllib
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

PCT = re.compile(r"^(\d+(?:\.\d+)?)%$")


def to_px(v, total: int) -> int:
    if isinstance(v, str):
        m = PCT.match(v)
        if m:
            return int(float(m.group(1)) * 0.01 * total)
    return int(v)


def anchor_offset(w: int, h: int, anchor: str | None):
    a = anchor or "top_left"
    dx = {"left": 0, "center": -w // 2, "right": -w}[
        ("left" if "left" in a else "center" if "center" in a else "right")
    ]
    dy = {"top": 0, "center": -h // 2, "bottom": -h}[
        ("top" if "top" in a else "center" if "center" in a else "bottom")
    ]
    return dx, dy


def rounded_mask(w: int, h: int, r: int) -> Image.Image:
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, w, h], radius=r, fill=255)
    return mask


def apply_filters(img: Image.Image, specs: list[str] | None) -> Image.Image:
    if not specs:
        return img
    out = img
    for spec in specs:
        if ":" in spec:
            name, arg = spec.split(":", 1)
            val = float(arg)
        else:
            name, val = spec, None
        if name == "auto_contrast":
            out = ImageOps.autocontrast(out)
        elif name == "equalize":
            out = ImageOps.equalize(out)
        elif name == "sharpen":
            out = out.filter(
                ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)
            )
        elif name == "blur":
            out = out.filter(ImageFilter.GaussianBlur(2))
        elif name == "bw":
            out = ImageOps.grayscale(out).convert("RGB")
        elif name == "sepia":
            g = ImageOps.grayscale(out)
            out = ImageOps.colorize(g, "#704214", "#F5DEB3")
        elif name == "exposure":  # simple gamma
            gamma = 1.0 / (1.0 + (val if val is not None else 0.0))
            out = ImageOps.gamma(out, gamma)
        elif name == "saturation":
            out = ImageEnhance.Color(out).enhance(val if val is not None else 1.0)
        elif name == "brightness":
            out = ImageEnhance.Brightness(out).enhance(val if val is not None else 1.0)
        elif name == "contrast":
            out = ImageEnhance.Contrast(out).enhance(val if val is not None else 1.0)
    return out


def _load_font(font_spec: dict, template_dir: Path):
    """Return a PIL ImageFont from either a file path or a system family lookup."""
    size = int(font_spec.get("size", 24))

    # 1) Explicit path (relative to template)
    p = font_spec.get("path")
    if p:
        fp = Path(p)
        if not fp.is_absolute():
            fp = (template_dir / fp).resolve()
        try:
            return ImageFont.truetype(str(fp), size)
        except Exception as e:
            print(f"⚠️ Could not load font at {fp}: {e}")

    # 2) System font by family/weight/style (best on Linux via fontconfig)
    family = font_spec.get("family")
    if family:
        style_bits = []
        if font_spec.get("weight"):  # e.g., "Bold", "Medium"
            style_bits.append(str(font_spec["weight"]))
        if font_spec.get("style"):  # e.g., "Italic"
            style_bits.append(str(font_spec["style"]))
        style_str = " ".join(style_bits) if style_bits else None

        # Try fc-match (Linux/RPi typically has it)
        try:
            query = family + (f":style={style_str}" if style_str else "")
            path = subprocess.check_output(
                ["fc-match", "-f", "%{file}\n", query], text=True
            ).strip()
            if path and Path(path).exists():
                return ImageFont.truetype(path, size)
        except Exception:
            pass

        # Fallback: search common font dirs (macOS/Windows/Linux)
        candidates = [
            Path("/usr/share/fonts"),
            Path("/usr/local/share/fonts"),
            Path.home() / ".local/share/fonts",
            Path("/System/Library/Fonts"),
            Path("/Library/Fonts"),
            Path("C:/Windows/Fonts"),
        ]
        stem = family.replace(" ", "").lower()
        for base in candidates:
            if not base.exists():
                continue
            try:
                for fp in base.rglob("*.ttf"):
                    if stem in fp.stem.replace(" ", "").lower():
                        try:
                            return ImageFont.truetype(str(fp), size)
                        except Exception:
                            continue
            except Exception:
                continue

    # 3) Final fallbacks
    for fp in [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]:
        if fp.exists():
            try:
                return ImageFont.truetype(str(fp), size)
            except Exception:
                pass

    print("⚠️ Falling back to PIL default bitmap font.")
    return ImageFont.load_default()


def draw_text(
    canvas,
    text,
    x,
    y,
    font_spec,
    fill,
    stroke=None,
    tracking=0,
    anchor="top_left",
    template_dir: Path | None = None,
):
    # Load font from spec (path or system family)
    fnt = _load_font(font_spec, template_dir or Path("."))

    # Measure
    draw = ImageDraw.Draw(canvas)
    sw = int(stroke["width"]) if stroke and "width" in stroke else 0
    bbox = draw.textbbox((0, 0), text, font=fnt, stroke_width=sw)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    dx, dy = anchor_offset(w, h, anchor)
    cx, cy = x + dx, y + dy

    # Tracking (very light): draw char-by-char with extra spacing if requested
    if tracking:
        advance = 0
        for ch in text:
            cb = draw.textbbox((0, 0), ch, font=fnt, stroke_width=sw)
            cw = cb[2] - cb[0]
            if stroke:
                draw.text(
                    (cx + advance, cy),
                    ch,
                    font=fnt,
                    fill=fill,
                    stroke_width=sw,
                    stroke_fill=stroke["color"],
                )
            else:
                draw.text((cx + advance, cy), ch, font=fnt, fill=fill)
            advance += cw + tracking
    else:
        if stroke:
            draw.text(
                (cx, cy),
                text,
                font=fnt,
                fill=fill,
                stroke_width=sw,
                stroke_fill=stroke["color"],
            )
        else:
            draw.text((cx, cy), text, font=fnt, fill=fill)


def render_collage(
    template_path: str | Path,
    shots: dict[str, Image.Image],
    variables: Mapping[str, str],
    out_path: str | Path,
) -> Path:
    template_path = Path(template_path)
    out_path = Path(out_path)
    template_dir = template_path.parent

    with template_path.open("rb") as f:
        tpl = tomllib.load(f)

    W, H = int(tpl["canvas"]["width"]), int(tpl["canvas"]["height"])
    bg_color = tpl["canvas"].get("color", "#ffffff")
    canvas = Image.new("RGBA", (W, H), bg_color)

    # background image
    if "background" in tpl and "image" in tpl["background"]:
        bg_file = template_dir / tpl["background"]["image"]
        bg = Image.open(bg_file).convert("RGBA")
        fit = tpl["background"].get("fit", "cover")
        if fit in ("cover", "contain", "stretch", "center", "tile"):
            if fit == "stretch":
                bg = bg.resize((W, H), Image.LANCZOS)
                canvas.alpha_composite(bg, (0, 0))
            elif fit == "center":
                x = (W - bg.width) // 2
                y = (H - bg.height) // 2
                canvas.alpha_composite(bg, (x, y))
            elif fit == "tile":
                for yy in range(0, H, bg.height):
                    for xx in range(0, W, bg.width):
                        canvas.alpha_composite(bg, (xx, yy))
            else:
                # cover / contain
                ratio = (
                    min(W / bg.width, H / bg.height)
                    if fit == "contain"
                    else max(W / bg.width, H / bg.height)
                )
                rb = bg.resize(
                    (int(bg.width * ratio), int(bg.height * ratio)), Image.LANCZOS
                )
                x = (W - rb.width) // 2
                y = (H - rb.height) // 2
                canvas.alpha_composite(rb, (x, y))

    for layer in tpl.get("layers", []):
        t = layer["type"]
        if t == "image_slot":
            src_name = layer["name"]  # 'shot1' / 'shot2' / 'shot3'
            src_img = shots.get(src_name)
            if src_img is None:
                continue
            img = src_img.convert("RGBA")

            # filters
            img = apply_filters(img, layer.get("filters"))

            # fit image into box (cover)
            w = to_px(layer["w"], W)
            h = to_px(layer["h"], H)
            ir = max(w / img.width, h / img.height)
            ri = img.resize((int(img.width * ir), int(img.height * ir)), Image.LANCZOS)
            ix = (w - ri.width) // 2
            iy = (h - ri.height) // 2
            frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            frame.alpha_composite(ri, (ix, iy))

            # rounded mask
            r = int(layer.get("radius", 0))
            if r > 0:
                mask = rounded_mask(w, h, r)
                frame.putalpha(mask)

            # rotate (about center)
            if "transform" in layer and "rotate" in layer["transform"]:
                frame = frame.rotate(
                    layer["transform"]["rotate"], expand=True, resample=Image.BICUBIC
                )

            # shadow (simple drop shadow)
            if "shadow" in layer:
                sh = layer["shadow"]
                sx, sy = int(sh.get("dx", 0)), int(sh.get("dy", 0))
                blur = int(sh.get("blur", 12))
                scol = sh.get("color", "#00000040")
                alpha = frame.split()[-1]
                sfill = Image.new("RGBA", frame.size, scol)
                shadow = Image.composite(
                    sfill, Image.new("RGBA", frame.size, (0, 0, 0, 0)), alpha
                ).filter(ImageFilter.GaussianBlur(blur))
                canvas.alpha_composite(
                    shadow, (to_px(layer["x"], W) + sx, to_px(layer["y"], H) + sy)
                )

            # border
            if "border" in layer:
                b = layer["border"]
                bw = int(b.get("width", 0))
                if bw > 0:
                    border = Image.new(
                        "RGBA", (frame.width, frame.height), (0, 0, 0, 0)
                    )
                    draw = ImageDraw.Draw(border)
                    draw.rounded_rectangle(
                        [0, 0, frame.width - 1, frame.height - 1],
                        radius=r,
                        outline=b["color"],
                        width=bw,
                    )
                    frame = Image.alpha_composite(frame, border)

            # place
            x = to_px(layer["x"], W)
            y = to_px(layer["y"], H)
            dx, dy = anchor_offset(
                frame.width, frame.height, layer.get("anchor", "top_left")
            )
            canvas.alpha_composite(frame, (x + dx, y + dy))

        elif t == "image_overlay":
            p = template_dir / layer["image"]
            ov = Image.open(p).convert("RGBA")
            if "w" in layer and "h" in layer:
                ov = ov.resize(
                    (to_px(layer["w"], W), to_px(layer["h"], H)), Image.LANCZOS
                )
            if "opacity" in layer:
                a = ov.split()[-1].point(lambda i: int(i * float(layer["opacity"])))
                ov.putalpha(a)
            x = to_px(layer["x"], W)
            y = to_px(layer["y"], H)
            dx, dy = anchor_offset(ov.width, ov.height, layer.get("anchor", "top_left"))
            canvas.alpha_composite(ov, (x + dx, y + dy))

        elif t == "text":
            raw = layer["text"]

            # simple variables, plus strftime support
            # may modify to use settings.py to manage...
            def subst(s: str) -> str:
                # s = s.replace("{EVENT_NAME}", variables.get("EVENT_NAME", "Event"))
                # s = s.replace("{SESSION_ID}", variables.get("SESSION_ID", "0000"))
                # s = s.replace("{APP_VERSION}", variables.get("APP_VERSION", "0.0.0"))
                # {DATE:%b %d, %Y}
                if "{DATE:" in s:
                    fmt = s.split("{DATE:", 1)[1].split("}", 1)[0]
                    s = s.replace("{DATE:" + fmt + "}", datetime.now().strftime(fmt))
                return s

            txt = subst(raw)
            x = to_px(layer["x"], W)
            y = to_px(layer["y"], H)
            draw_text(
                canvas,
                txt,
                x,
                y,
                layer["font"],
                layer.get("fill", "#000000"),
                stroke=layer.get("stroke"),
                tracking=layer.get("tracking", 0),
                anchor=layer.get("anchor", "top_left"),
            )

    # ensure parent exists, save, and return Path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas = canvas.convert("RGB")  # strip alpha for JPEG if needed
    canvas.save(out_path)
    return out_path
