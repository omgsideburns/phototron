from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("phototron")
except PackageNotFoundError:
    __version__ = "0.0.0+local"
