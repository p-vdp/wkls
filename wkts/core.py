import duckdb
import importlib.resources
from . import data
import time

S3_PARQUET_PATH = "s3://overturemaps-us-west-2/release/2025-05-21.0/theme=divisions/type=division_area/*"

# Module-level initialization flag
_table_initialized = False

def _initialize_table():
    """Initialize the wkls table if it doesn't exist. Called once per module import."""
    global _table_initialized
    if not _table_initialized:
        duckdb.load_extension("spatial")
        if not duckdb.sql("SHOW TABLES").df().query("name == 'wkls'").any().any():
            duckdb.sql(f"""
                CREATE TABLE wkls AS
                SELECT id, country, region, subtype, name, division_id
                FROM '{importlib.resources.files(data)}/overture_zstd22.parquet'
            """)
        _table_initialized = True

# Initialize the table when the module is imported
_initialize_table()

class Wkl:
    def __init__(self, chain=None):
        self.chain = chain or []

    def __getattr__(self, attr):
        return Wkl(self.chain + [attr.lower()])

    def __getitem__(self, key):
        return Wkl(self.chain + [key.lower()])

    def __repr__(self):
        return repr(self.resolve())

    def resolve(self):
        if not self.chain:
            raise ValueError("No attributes in the chain. Use Wkls().country or Wkls().country.region, etc.")
        elif len(self.chain) == 1:
            country_iso = self.chain[0].upper()
            query = f"""
                SELECT * FROM wkls
                WHERE country = '{country_iso}'
                  AND subtype = 'country'
            """
        elif len(self.chain) == 2:
            country_iso = self.chain[0].upper()
            region_iso = country_iso + "-" + self.chain[1].upper()
            query = f"""
                SELECT * FROM wkls
                WHERE country = '{country_iso}'
                  AND region = '{region_iso}'
                  AND subtype = 'region'
            """
        elif len(self.chain) == 3:
            country_iso = self.chain[0].upper()
            region_iso = country_iso + "-" + self.chain[1].upper()
            query = f"""
                SELECT * FROM wkls
                WHERE country = '{country_iso}'
                  AND region = '{region_iso}'
                  AND subtype IN ('county', 'locality', 'localadmin')
                  AND REPLACE(name, ' ', '') ILIKE REPLACE('{self.chain[2]}', ' ', '')
            """
        else:
            raise ValueError("Too many chained attributes (max = 3)")
        return duckdb.sql(query).df()

    def _get_geom_expr(self, expr: str):
        df = self.resolve()
        if df.empty:
            raise ValueError(f"No result found for: {'.'.join(self.chain)}")

        geom_id = df.iloc[0]["id"]
        query = f"""
            SELECT {expr}
            FROM parquet_scan('{S3_PARQUET_PATH}')
            WHERE id = '{geom_id}'
        """
        result_df = duckdb.sql(query).df()
        if result_df.empty:
            raise ValueError(f"No geometry found for ID: {geom_id}")
        return result_df.iloc[0, 0]

    def wkt(self):
        return self._get_geom_expr("ST_AsText(geometry)")

    def wkb(self):
        return self._get_geom_expr("ST_AsWKB(geometry)")

    def hexwkb(self):
        return self._get_geom_expr("ST_AsHEXWKB(geometry)")

    def geojson(self):
        return self._get_geom_expr("ST_AsGeoJSON(geometry)")

    def svg(self):
        return self._get_geom_expr("ST_AsSVG(geometry)")
    
    def countries(self):
        if self.chain:
            raise ValueError("The 'countries' method does not support chaining. Use Wkls().country or Wkls().country.region, etc.")
        
        query = """
            SELECT DISTINCT id, country, subtype, name, division_id
            FROM wkls
            WHERE subtype = 'country'
        """
        df = duckdb.sql(query).df()
        return df

    def regions(self):
        if not self.chain or len(self.chain) > 1:
            raise ValueError("The 'regions' method supports only country or country.region chaining. Use Wkls().country or Wkls().country.region, etc.")
        if len(self.chain) == 1:
            country_iso = self.chain[0].upper()
            query = f"""
                SELECT * FROM wkls
                WHERE country = '{country_iso}'
                    AND subtype = 'region'
            """
            df = duckdb.sql(query).df()
            return df
    
    def counties(self):
        if not self.chain or len(self.chain) > 2:
            raise ValueError("The 'counties' method supports only country or country.region chaining. Use Wkls().country or Wkls().country.region, etc.")
        if len(self.chain) == 2:
            country_iso = self.chain[0].upper()
            region_iso = country_iso + "-" + self.chain[1].upper()
            query = f"""
                SELECT * FROM wkls
                WHERE country = '{country_iso}'
                  AND region = '{region_iso}'
                  AND subtype = 'county'
            """
            df = duckdb.sql(query).df()
            return df
    
    def cities(self):
        start = time.time()
        if not self.chain or len(self.chain) > 3:
            raise ValueError("The 'cities' method supports only country, country.region, or country.region.city chaining. Use Wkls().country or Wkls().country.region, etc.")
        if len(self.chain) == 2:
            country_iso = self.chain[0].upper()
            region_iso = country_iso + "-" + self.chain[1].upper()
            query = f"""
                SELECT * FROM wkls
                WHERE country = '{country_iso}'
                  AND region = '{region_iso}'
                  AND subtype IN ('locality', 'localadmin')
            """
            df = duckdb.sql(query).df()
            return df
        
    def subtypes(self):
        if self.chain:
            raise ValueError("The 'subtypes' method does not support chaining. Use Wkls().country or Wkls().country.region, etc.")
            
        query = f"""
            SELECT DISTINCT subtype FROM wkls
        """
        df = duckdb.sql(query).df()
        return df
