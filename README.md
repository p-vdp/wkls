# WKT (Well-Known Text) geometries for WKLs (Well-Known Locations)

`wkts` makes it easy to grab Well-Known Text geometry strings for
Well-Known Locations such as countries, regions and states, and major
cities around the world.

It's impossible to be comprehensive in this library. If something is
missing, please propose it and we will work to integrate it! There also
may be situations with name conflicts that make it impossible to include
certain locations; as a result, `wkts` is by nature _opinionated_ about
what is available.

`wkts` is interoperable with many Pythonic geospatial tools like
Shapely, GeoPandas, Sedona, and Dask.

## Installation

```
pip install wkts
```

This library doesn't have any dependencies, so it's easy to install anywhere.

## Usage

`wkts` provides two mechanisms for accessing WKT geometries:

1. A hierarchy of Python attributes that you can access and reference
   directly; this provides the most direct and efficient access, but
   isn't exhaustive.
2. Helpers to query Overture Maps Foundation data using a provided
   Apache Sedona context, for flexible queries.

### Simple usage

Here's how you can grab the polygon for New York State for example:

```python
import wkts
print(wkt.us.ny) # => "POLYGON((-79.7624 42.5142,-79.0672 42.7783..."
```

You can also fetch WKTs from the Overture Maps Foundation tables as follows:

```python
table_name = "wherobots_open_data.overture_maps_foundation.divisions_division_area"
wkt.omf(sedona, table_name).state("US", "US-AZ") # => "POLYGON((..."
```

### Shapely + WKTs

To create a Shapely geometry using a WKT value from `wkts`:

```python
import shapely
import wkts

alaska = shapely.from_wkt(wkts.us.ak)
print(type(alaska))   # => shapely.geometry.polygon.Polygon
print(alaska.area)    # => 353.4887780300002
```

## GeoPandas + WKTs

To create a GeoPandas DataFrame using WKT values from `wkts`:

```python
import geopandas as gpd
import pandas as pd
import shapely
import wkts

data = {
    "state": ["colorado", "new_mexico"],
    "geometry": [shapely.from_wkt(wkts.us.colorado), shapely.from_wkt(wkts.us.new_mexico)]
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

## Sedona + WKTs

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

Here's how to get the WKT for a country:

```python
table_name = "wherobots_open_data.overture_maps_foundation.divisions_division_area"
wkt.omf(sedona, table_name).country("US") # => "POLYGON((..."
```

Here's how to get the WKT for a state:

```python
wkt.omf(sedona, table_name).state("US", "US-AZ") # => "POLYGON((..."
```

Here is how to get the WKT for a city:

```python
wkt.omf(sedona, table_name).city("US", "US-AZ", "Phoenix") # => "POLYGON((..."
```

# Contributing

Feel free to submit a pull request with additional WKTs!

You can also create an issue to discuss ideas before writing any code.

You can also check issues with the "help wanted" tag for contribution ideas.

## Developing

You can run the test suite with `uv run pytest tests`.
