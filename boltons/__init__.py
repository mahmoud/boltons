from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("boltons")
except PackageNotFoundError:
    # Package is not installed (e.g. running from source checkout)
    __version__ = "unknown"
