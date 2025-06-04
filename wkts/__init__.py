import duckdb
import importlib.resources
import sys
import time

from . import data

S3_PARQUET_PATH = "s3://overturemaps-us-west-2/release/2025-05-21.0/theme=divisions/type=division_area/*"

class StaticWKL:
    """Powerhouse behind the Well-Known Locations WKT library. This class
    represents the string WKT geometry of a given Well-Known Location, but
    dynamically intercepts attempts to access sub-attributes to resolve
    locations from the underlying static database."""

    def __init__(self, name, id=None, country=None, region=None, subtype=None):
        self.name = name
        self.id = id
        self.country = country
        self.region = region
        self.subtype = subtype
        self._geom = None

    def __getattr__(self, name):
        # Only resolve id, not geometry

        # Country level
        if not self.name:
            startT = time.time()
            country_iso = name
            df = duckdb.sql(f"""
                SELECT id, country
                FROM wkls
                WHERE country = '{country_iso.upper()}'
                  AND subtype = 'country'
            """).df()
            if len(df) != 1:
                raise AttributeError(f"Country '{country_iso}' not found")
            endT = time.time()
            print(f"\nResolved ID of country '{country_iso}' in {endT - startT:.4f} seconds")
            return StaticWKL(country_iso, id=df["id"][0], country=country_iso.upper(), subtype="country")
        
        # Region level (State/Province)
        elif self.country and not self.region:
            startT = time.time()
            region_code = f"{self.country}-{name.upper()}"
            df = duckdb.sql(f"""
                SELECT id, region
                FROM wkls
                WHERE country = '{self.country}'
                  AND region = '{region_code}'
                  AND subtype = 'region'
            """).df()
            if len(df) != 1:
                raise AttributeError(f"Region '{region_code}' not found")
            endT = time.time()
            print(f"Resolved ID of region '{region_code}' in {endT - startT:.4f} seconds")
            return StaticWKL(name, id=df["id"][0], country=self.country, region=region_code, subtype="region")
        
        # County, locality and localadmin levels (County and City)
        elif self.country and self.region and self.subtype != "city":
            startT = time.time()
            df = duckdb.sql(f"""
                SELECT id, division_id
                FROM wkls
                WHERE country = '{self.country}'
                  AND region = '{self.region}'
                  AND REPLACE(name, ' ', '') ILIKE '{name}'
            """).df()
            if len(df) < 1:
                raise AttributeError(f"City '{name}' not found.")
            endT = time.time()
            print(f"Resolved id of City/County '{self.name}' in {endT - startT:.4f} seconds")
            return StaticWKL(name, id=df["id"][0], country=self.country, region=self.region, subtype="city")
        else:
            raise AttributeError("Only country, region and locality levels are supported in this implementation.")

    def _load_geom(self, transform):
        if self.id and self.id != "POLYGON()" and self._geom is None:
            startT = time.time()
            geom_df = duckdb.sql(f"""
                SELECT {transform}(geometry) AS geom
                FROM parquet_scan('{S3_PARQUET_PATH}')
                WHERE id = '{self.id}'
            """).df()
            if len(geom_df) != 1:
                raise AttributeError(f"Geometry for id '{self.id}' not found")
            self._geom = geom_df["geom"][0]
            endT = time.time()
            print(f"Looked up '{self.name}' by ID {self.id} in {endT - startT:.4f} seconds")
        return self._geom

    def wkt(self):
        return str(self._load_geom("ST_AsText")) or ""

    def wkb(self):
        return self._load_geom("ST_AsWKB")
    
    def hexwkb(self):
        return self._load_geom("ST_AsHexWKB") or ""
    
    def geojson(self):
        return self._load_geom("ST_AsGeoJSON")
    
    def svg(self):
        return self._load_geom("ST_AsSVG") or ""

# Seed the database of Well-Known Locations with geometry-excluded OMF divisions_division_area.
duckdb.load_extension("spatial")
duckdb.sql(f"""CREATE TABLE wkls AS
    SELECT id, country, region, subtype, name, division_id
    FROM '{importlib.resources.files(data)}/overture_zstd22.parquet'""")

# Rebind ourselves to a top-level dummy WKL that represents the world.
sys.modules["wkts"] = StaticWKL("", "POLYGON()")
