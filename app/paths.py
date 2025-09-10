from pathlib import Path

# This is a set of path functions I put together 
# while swapping everything from os.path to pathlib.
# There are more notes at the bottom of this file.

# Root of the project (adjust depth if needed)
APP_ROOT = Path(__file__).resolve().parents[1]

def read_text(p: Path | str, encoding="utf-8") -> str:
    """Read file as text."""
    return Path(p).read_text(encoding=encoding)

def write_text(p: Path | str, data: str, encoding="utf-8") -> None:
    """Write text to file, creating parent dirs if missing."""
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(data, encoding=encoding)

def read_bytes(p: Path | str) -> bytes:
    return Path(p).read_bytes()

def write_bytes(p: Path | str, data: bytes) -> None:
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)

def ensure_dir(p: Path | str) -> Path:
    """Ensure a directory exists and return it as Path."""
    p = Path(p)
    p.mkdir(parents=True, exist_ok=True)
    return p

def list_dirs(p: Path | str) -> list[Path]:
    """List immediate subdirectories of a path."""
    return [d for d in Path(p).iterdir() if d.is_dir()]

def list_files(p: Path | str, pattern="*") -> list[Path]:
    """List files matching a glob pattern in a directory."""
    return sorted(Path(p).glob(pattern))

def posix(p: Path | str) -> str:
    """Return forward-slash path (safe for QSS, JSON, URLs)."""
    return Path(p).as_posix()


# Notes on moving from os.path to pathlib...
'''
Old (os.path etc.)	            New (pathlib)
os.path.join(a, b, c)	        Path(a) / b / c
os.path.exists(p)	            Path(p).exists()
os.makedirs(p, exist_ok=True)   Path(p).mkdir(parents=True, exist_ok=True)
open(p).read()	                Path(p).read_text()
open(p, "rb").read()	        Path(p).read_bytes()
open(p, "w").write(data)        Path(p).write_text(data)
os.listdir(p)	                [x.name for x in Path(p).iterdir()]
glob.glob("*.jpg")	            Path(".").glob("*.jpg")
os.path.basename(p)	            Path(p).name
os.path.dirname(p)	            Path(p).parent
os.path.splitext(p)	            (Path(p).stem, Path(p).suffix)
os.remove(p)	                Path(p).unlink()
os.rename(a, b)	                Path(a).rename(b)

When injecting paths into QSS or JSON, always do:
STYLE_PATH.as_posix()
That guarantees forward slashes (C:/Users/...) even on Windows.

'''