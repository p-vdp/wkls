import importlib.resources
import sys
from . import data, util


class StaticWKL(str):
    """Powerhouse behind the Well-Known Locations WKT library. This class
    represents the string WKT geometry of a given Well-Known Location, but
    dynamically intercepts attempts to access sub-attributes to resolve
    locations from the underlying static database."""

    def __new__(cls, name, geom):
        s = super().__new__(cls, geom)
        s.name = name
        return s

    def __getattr__(self, name):
        fqn = f"{self.name}.{name}" if self.name else name
        wkl = _DATABASE.get(fqn)
        if wkl:
            return wkl
        raise AttributeError(f"WKT for '{fqn}' does not exist")


# Seed the database of Well-Known Locations with all available data.
data_files = [
    file for file in importlib.resources.files(data).iterdir()
    if file.is_file() and file.name.endswith('.parquet')
]
_DATABASE = util.read_wkt_data(data_files, StaticWKL)

# Rebind ourselves to a top-level dummy WKL that represents the world.
sys.modules["wkts"] = StaticWKL("", "POLYGON()")
