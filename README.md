# wkt

wkt makes it easy to grab Well-Known Text strings for countries, states, and cities around the world.

Here's how you can grab the polygon for New York State for example:

```python
import wkt

wkt.us.states.new_york() # => "POLYGON((-79.7624 42.5142,-79.0672 42.7783..."
```

`wkt` is interoperable with many Pythonic geospatial tools like Shapely, GeoPandas, Sedona, and Dask!

You can also fetch WKTs from the Overture Maps Foundation tables as follows:

```python
table_name = "wherobots_open_data.overture_maps_foundation.divisions_division_area"
wkt.omf(sedona, table_name).state("US", "US-AZ") # => "POLYGON((..."
```

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

## WKTs from Overture data

It's easy to get the WKT for countries, states, and cities from the Overture data:

TODO

## Contributing

Feel free to submit a pull request with additional WKTs!

You can also create an issue to discuss ideas before writing any code.

You can also check issues with the "help wanted" tag for contribution ideas.

## Developing

You can run the test suite with `uv run pytest tests`.
