import os, subprocess, shlex, tempfile
from pathlib import Path
from PIL import Image
from app.config import PRINTER_CONFIG

LP_BIN = "/usr/bin/lp"  # avoid PATH issues from .desktop launchers


def _normalize_for_print(src_path: str) -> str:
    src = Path(src_path)

    # If it's already a baseline RGB JPEG with no alpha, just use it as-is.
    if src.suffix.lower() in (".jpg", ".jpeg"):
        try:
            with Image.open(src) as im:
                if im.mode in ("RGB", "L"):  # SELPHY accepts RGB JPEG best
                    # Pillow sets .info.get("progression") True for progressive JPEGs
                    is_progressive = bool(
                        im.info.get("progressive") or im.info.get("progression")
                    )
                    if not is_progressive:
                        return str(src)
        except Exception:
            pass  # fall through to re-encode

    # Otherwise, write a baseline (non-progressive) sRGB JPEG to /tmp
    tmp = Path(tempfile.gettempdir()) / (src.stem + "_print.jpg")
    with Image.open(src) as im:
        # Flatten alpha if present
        if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im.convert("RGBA"), mask=im.convert("RGBA").split()[-1])
            im = bg
        # Convert CMYK/etc → RGB
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")

        # Save as **baseline JPEG** (progressive=False), strip ICC
        im.save(
            tmp,
            "JPEG",
            quality=92,
            optimize=True,
            progressive=False,  # <-- key change
            icc_profile=None,
        )
    return str(tmp)


def send_to_printer(image_path):
    if not PRINTER_CONFIG.get("enabled", False):
        print("🖨️ Printing is disabled in config.")
        return False

    # 0) verify input exists
    src = Path(image_path)
    if not src.exists():
        print(f"⚠️ File not found: {src}")
        return False

    # 1) normalize to JPEG
    printable = _normalize_for_print(str(src))
    size = Path(printable).stat().st_size
    print(f"[print.py] printable={printable} ({size} bytes)")

    # 2) build command (use default CUPS printer unless explicitly set)
    printer = PRINTER_CONFIG.get("printer_name")
    copies = str(PRINTER_CONFIG.get("copies", 1))
    paper_size = PRINTER_CONFIG.get("paper_size")

    cmd = [LP_BIN, "-n", copies]
    if printer:
        print(f"[print.py] using specified printer: {printer}")
        cmd += ["-d", printer]
    #if paper_size:
    #    print(f"[print.py] using specified paper size: {paper_size}")
    #    cmd += ["-o", f"media={paper_size}"]

    cmd.append(printable)
    print("[print.py]", shlex.join(cmd))

    try:
        # minimal sane PATH even from .desktop
        env = os.environ.copy()
        env["PATH"] = "/usr/bin:/bin:/usr/sbin:/sbin"
        out = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
        msg = out.stdout.strip()
        print("✅ Print job submitted." + (f" {msg}" if msg else ""))
        return True
    except FileNotFoundError:
        print("⚠️ '/usr/bin/lp' not found — is CUPS installed?")
        return False
    except subprocess.CalledProcessError as e:
        err = (e.stderr or e.stdout or "").strip()
        print(f"⚠️ Printing failed (exit {e.returncode}): {err}")
        # quick hints:
        print(
            "   Hints: check default queue `lpstat -p -d`; ensure not a RAW queue; see /var/log/cups/error_log"
        )
        return False
