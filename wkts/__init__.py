import duckdb
import importlib.resources
import sys

from . import data


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
        df = duckdb.sql(f"SELECT ST_AsText(geom) AS geom FROM wkls WHERE name = '{fqn}'").df()
        if len(df) != 1:
            raise AttributeError(f"WKT for '{fqn}' does not exist")
        return StaticWKL(fqn, df["geom"][0])


# Seed the database of Well-Known Locations with all available data.
duckdb.load_extension("spatial")
duckdb.sql(f"""CREATE TABLE wkls AS
    SELECT geom_id, name, aliases, geom
    FROM '{importlib.resources.files(data)}/*.parquet'""")

# Rebind ourselves to a top-level dummy WKL that represents the world.
sys.modules["wkts"] = StaticWKL("", "POLYGON()")
