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

TODO

## GeoPandas + wkt

TODO

## Sedona + wkt

TODO

## Creating wkts

TODO

## Contributing

Feel free to submit a pull request with additional WKTs!

You can also create an issue to discuss ideas before writing any code.

You can also check issues with the "help wanted" tag for contribution ideas.

## Developing

You can run the test suite with `uv run pytest tests`.
