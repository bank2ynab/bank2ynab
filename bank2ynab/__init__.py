from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("bank2ynab")
except PackageNotFoundError:
    __version__ = "unknown"
