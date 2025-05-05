# Creating wkts

Use Overture Maps Foundation Divisions dataset to generate wkts.

```python
divisions_df = sedona.table("wherobots_open_data.overture_maps_foundation.divisions_division_area")
divisions_df.createOrReplaceTempView("division_area")
```

To generate a wkt of a country use subtype, 'country':

```python
country_iso = "US" # ISO code of the country

query = f"""
SELECT ST_AsEWKT(geometry) AS wkt
FROM division_area
WHERE subtype = 'country'
AND country = '{country_iso}'
"""

wkt = sedona.sql(query).collect()[0][0]
```

To generate a wkt of a state/region in a country use subtype, 'region':

```python
country_iso = "US" # ISO code of the country
state_iso = "US-AZ" # ISO code of the state

query = f"""
SELECT ST_AsEWKT(geometry) AS wkt
FROM division_area
WHERE subtype = 'region'
AND country = '{country_iso}'
AND region = '{state_iso}'
"""

wkt = sedona.sql(query).collect()[0][0]
```

To generate a wkt of a city use subtype, 'locality':

Make sure to use the country and state filter when filtering by `city_name`.  There may be more than one city with the same name. 

```python
country_iso = "US" # ISO code of the country
state_iso = "US-AZ" # ISO code of the state
city_name = 'Phoenix'

query = f"""
SELECT ST_AsEWKT(geometry) AS wkt
FROM division_area
WHERE subtype = 'locality'
AND country = '{country_iso}'
AND region = '{state_iso}'
AND names.primary = '{city_name}'
"""

wkt = sedona.sql(query).collect()[0][0]
```
