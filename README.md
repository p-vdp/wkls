# wkt

wkt makes it easy to grab Well-Known Text strings for countries, states, and cities around the world.

Here's how you can grab the polygon for New York State for example:

```python
import wkt

wkt.us.states.new_york() # => "POLYGON((-79.7624 42.5142,-79.0672 42.7783..."
```

`wkt` is interoperable with many Pythonic geospatial tools like Shapely, GeoPandas, Sedona, and Dask!

## Installation

Just run `pip install wkt`.

This library doesn't have any dependencies, so it's easy to install anywhere.

## Shapely + wkt

Let's create a Shapely polygon with `wkt`:

```python
import wkt
from shapely import from_wkt

alaska = from_wkt(wkt.us.states.alaska())
```

Check to make sure that a Shapely Polygon is created:

```python
type(alaska) # => shapely.geometry.polygon.Polygon
```

Compute the area of the polygon:

```python
alaska.area # => 353.4887780300002
```

## GeoPandas + wkt

Create a GeoPandas DataFrame with `wkt`:

```python
import geopandas as gpd
import pandas as pd

data = {
    "state": ["colorado", "new_mexico"],
    "geometry": [from_wkt(wkt.us.states.colorado()), from_wkt(wkt.us.states.new_mexico())]
}
df = pd.DataFrame(data)
gdf = gpd.GeoDataFrame(df, geometry="geometry")
```

Add a column with centroids:

```python
gdf['centroid'] = gdf.geometry.centroid
```

Look at the results:

```python
        state                     geometry                     centroid
0    colorado  POLYGON ((-109.0448 37.0004,  POINT (-105.54643 38.99855)
1  new_mexico  POLYGON ((-109.0448 36.9971,  POINT (-106.10366 34.42267)
```

## Sedona + wkt

Read the Overture Maps Foundation places dataset:

```python
places = sedona.table("wherobots_open_data.overture_maps_foundation.places_place")
places.createOrReplaceTempView("places")
```

Find all the barbecue restaurants in the state of Florida:

```python
query = f"""
select * from places
where
    categories.primary = 'barbecue_restaurant' and
    ST_Contains(ST_GeomFromWKT('{wkt.us.states.florida()}'), geometry)
"""
res = sedona.sql(query)
res.count() # => 1386
```

## Creating wkts

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

## Contributing

Feel free to submit a pull request with additional WKTs!

You can also create an issue to discuss ideas before writing any code.

You can also check issues with the "help wanted" tag for contribution ideas.

## Developing

You can run the test suite with `uv run pytest tests`.
