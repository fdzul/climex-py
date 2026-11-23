"""climex: climate data of Mexico from the NASA POWER API."""
from importlib.metadata import PackageNotFoundError, version

from .climex import build_url, download_nasa_power_data, parse_response
from .load_data import centroids, load_centroid_data
from .municipalities import municipalities

try:
    __version__ = version("climex-py")
except PackageNotFoundError:          # running from the source tree
    __version__ = "0.0.0"

__all__ = ["download_nasa_power_data", "municipalities", "centroids", "build_url", "parse_response",
           "load_centroid_data"]
