import subprocess
from app.config import PRINTER_CONFIG

def send_to_printer(image_path):
    if not PRINTER_CONFIG.get("enabled", False):
        print("🖨️ Printing is disabled in config.")
        return False

    printer = PRINTER_CONFIG.get("printer_name")
    copies = str(PRINTER_CONFIG.get("copies", 1))
    paper_size = PRINTER_CONFIG.get("paper_size", None)

    if not printer:
        print("⚠️ No printer specified.")
        return False

    cmd = ["lp", "-d", printer, "-n", copies]

    # Optional: set media/paper size
    if paper_size:
        cmd += ["-o", f"media={paper_size}"]

    cmd.append(image_path)

    try:
        subprocess.run(cmd, check=True)
        print("✅ Print job submitted.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Printing failed: {e}")
        return False