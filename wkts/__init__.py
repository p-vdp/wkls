import duckdb
import importlib.resources
import sys
import time
from collections import UserDict

from . import data

S3_PARQUET_PATH = "s3://overturemaps-us-west-2/release/2025-05-21.0/theme=divisions/type=division_area/*"

class StaticWKL(UserDict):
    """Powerhouse behind the Well-Known Locations WKT library. Supports both dict-like and attribute-like access."""

    def __init__(self, name, id=None, country_iso=None, region_iso=None, subtype=None):
        super().__init__()
        # Always store as lists for consistency
        self.data["name"] = name if isinstance(name, list) else [name]
        self.data["id"] = id if isinstance(id, list) else [id]
        self.data["country_iso"] = country_iso if isinstance(country_iso, list) else [country_iso]
        self.data["region_iso"] = region_iso if isinstance(region_iso, list) else [region_iso]
        self.data["subtype"] = subtype if isinstance(subtype, list) else [subtype]

    def __getattr__(self, key):
        try:
            return self.data[key]
        except KeyError:
            
            # Country level
            if not self.data["name"][0]:
                startT = time.time()
                country_iso = key.upper()
                df = duckdb.sql(f"""
                    SELECT id, name, subtype
                    FROM wkls
                    WHERE country = '{country_iso}'
                      AND subtype = 'country'
                """).df()
                if len(df) < 1:
                    raise AttributeError(f"Country '{country_iso}' not found")
                endT = time.time()
                print(f"\nResolved ID(s) of country '{country_iso}' in {endT - startT:.4f} seconds")
                return StaticWKL(
                    name=df["name"].tolist(),
                    id=df["id"].tolist(),
                    country_iso=[country_iso]*len(df),
                    subtype=df["subtype"].tolist()
                )
            
            # Region level (State/Province)
            elif self.data["country_iso"][0] and not self.data["region_iso"][0]:
                startT = time.time()
                region_iso = f"{self.data['country_iso'][0]}-{key.upper()}"
                df = duckdb.sql(f"""
                    SELECT id, name, subtype
                    FROM wkls
                    WHERE country = '{self.data['country_iso'][0]}'
                      AND region = '{region_iso}'
                      AND subtype = 'region'
                """).df()
                if len(df) < 1:
                    raise AttributeError(f"Region '{region_iso}' not found")
                endT = time.time()
                print(f"Resolved ID(s) of region '{region_iso}' in {endT - startT:.4f} seconds")
                return StaticWKL(
                    name=df["name"].tolist(),
                    id=df["id"].tolist(),
                    country_iso=[self.data["country_iso"][0]]*len(df),
                    region_iso=[region_iso]*len(df),
                    subtype=df["subtype"].tolist()
                )
            
            # County, locality and localadmin levels (County and City)
            elif self.data["country_iso"][0] and self.data["region_iso"][0]:
                startT = time.time()
                df = duckdb.sql(f"""
                    SELECT id, name, subtype
                    FROM wkls
                    WHERE country = '{self.data['country_iso'][0]}'
                      AND region = '{self.data['region_iso'][0]}'
                      AND REPLACE(name, ' ', '') ILIKE '{key}'
                """).df()
                if len(df) < 1:
                    raise AttributeError(f"City '{key}' not found.")
                endT = time.time()
                print(f"Resolved ID(s) of City/County '{key}' in {endT - startT:.4f} seconds")
                return StaticWKL(
                    name=df["name"].tolist(),
                    id=df["id"].tolist(),
                    country_iso=[self.data["country_iso"][0]]*len(df),
                    region_iso=[self.data["region_iso"][0]]*len(df),
                    subtype=df["subtype"].tolist()
                )
            else:
                raise AttributeError("Only country, region and locality levels are supported in this implementation.")

    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            return self.__getattr__(key)
        
    def __setattr__(self, key, value):
        if key == "data":
            super().__setattr__(key, value)
        else:
            self.data[key] = value

    def __iter__(self):
        return iter(self.data)

    def items(self):
        return self.data.items()
    
    def keys(self):
        return self.data.keys()

    def __len__(self):
        return len(self.data)

    def _load_geom(self, transform):
        # Always use the first id in the list for geometry
        id_to_use = self.data["id"][0]
        if id_to_use and id_to_use != "POLYGON()":
            startT = time.time()
            geom_df = duckdb.sql(f"""
                SELECT {transform}(geometry) AS geom
                FROM parquet_scan('{S3_PARQUET_PATH}')
                WHERE id = '{id_to_use}'
            """).df()
            if len(geom_df) != 1:
                raise AttributeError(f"Geometry for id '{id_to_use}' not found")
            endT = time.time()
            print(f"Looked up '{self.data['name'][0]}' by ID {id_to_use} in {endT - startT:.4f} seconds")
            return geom_df["geom"][0]
        return None

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
