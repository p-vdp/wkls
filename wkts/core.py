import duckdb
import importlib.resources
from . import data
import time

S3_PARQUET_PATH = "s3://overturemaps-us-west-2/release/2025-05-21.0/theme=divisions/type=division_area/*"

class Wkl:
    def __init__(self, chain=None):
        start = time.time()
        self.chain = chain or []

        duckdb.load_extension("spatial")
        if not duckdb.sql("SHOW TABLES").df().query("name == 'wkls'").any().any():
            # print("🧱 Creating 'wkls' table now...")
            duckdb.sql(f"""
                CREATE TABLE wkls AS
                SELECT id, country, region, subtype, name, division_id
                FROM '{importlib.resources.files(data)}/overture_zstd22.parquet'
            """)

        end = time.time()
        # print(f"\nInitialized Wkls for chain in \"{'.'.join(self.chain)}\" in {end - start:.7f} seconds")

    def __getattr__(self, attr):
        return Wkl(self.chain + [attr.lower()])

    def __getitem__(self, key):
        return Wkl(self.chain + [key.lower()])

    def __repr__(self):
        return repr(self.resolve())

    def resolve(self):
        start = time.time()
        if not self.chain:
            raise ValueError("No attributes in the chain. Use Wkls().country or Wkls().country.region, etc.")
        elif len(self.chain) == 1:
            country_iso = self.chain[0].upper()
            query = f"""
                SELECT * FROM wkls
                WHERE country = '{country_iso}'
                  AND subtype = 'country'
            """
            # print("QUERY 1:", query)
        elif len(self.chain) == 2:
            country_iso = self.chain[0].upper()
            region_iso = country_iso + "-" + self.chain[1].upper()
            query = f"""
                SELECT * FROM wkls
                WHERE country = '{country_iso}'
                  AND region = '{region_iso}'
                  AND subtype = 'region'
            """
            # print("QUERY 2:", query)
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
            # print("QUERY 3:", query)
        else:
            raise ValueError("Too many chained attributes (max = 3)")
        end = time.time()
        # print(f"\nResolved {'.'.join(self.chain)} in {end - start:.7f} seconds")
        return duckdb.sql(query).df()

    def _get_geom_expr(self, expr: str):
        start = time.time()
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
        end = time.time()
        # print(f"\nExecuted geometry query in {end - start:.7f} seconds")
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
        start = time.time()

        if self.chain:
            raise ValueError("The 'countries' method does not support chaining. Use Wkls().country or Wkls().country.region, etc.")
        
        query = """
            SELECT DISTINCT id, country, subtype, name, division_id
            FROM wkls
            WHERE subtype = 'country'
        """
        df = duckdb.sql(query).df()
        end = time.time()
        # print(f"\nFetched countries in {end - start:.7f} seconds")
        return df

    def regions(self):
        start = time.time()
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
            end = time.time()
            # print(f"\nFetched regions in {end - start:.7f} seconds")
            return df
    
    def counties(self):
        start = time.time()
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
            end = time.time()
            # print(f"\nFetched counties in {end - start:.7f} seconds")
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
            end = time.time()
            # print(f"\nFetched cities in {end - start:.7f} seconds")
            return df
        
    def subtypes(self):
        start = time.time()
        if self.chain:
            raise ValueError("The 'subtypes' method does not support chaining. Use Wkls().country or Wkls().country.region, etc.")
            
        query = f"""
            SELECT DISTINCT subtype FROM wkls
        """
        df = duckdb.sql(query).df()
        end = time.time()
        # print(f"\nFetched subtypes in {end - start:.7f} seconds")
        return df
