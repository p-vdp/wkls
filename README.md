# 🌐 `wkls`: Well-Known Locations

`wkls` makes it easy to explore global administrative boundaries — from countries to cities — using clean, chainable Python syntax. It reads directly from [Overture Maps Foundation](https://overturemaps.org/) GeoParquet data hosted on the AWS Open Data Registry.

You can instantly get geometries in formats like WKT, WKB, HexWKB, GeoJSON, and SVG:

```python
import wkls
print(wkls.us.ca.sanfrancisco.wkt()) # => "MULTIPOLYGON (((-122.9915659 37.7672733...)))"
```

## Installation

```python
pip install wkls
```

> Requires DuckDB with the spatial extension (loaded automatically). The package is self-contained and lightweight.

## Usage

### 🔹 Accessing geometry

WKLS supports **up to 3 chained attributes**:
1. **Country** (required) – must be a 2-letter ISO 3166-1 alpha-2 code (e.g. `us`, `de`, `fr`)
2. **Region** (optional) – must be a valid region ISO code suffix (e.g. `ca` for `US-CA`, `ny` for `US-NY`)
3. **Place** (optional) – a **name** match against subtypes: `county`, `locality`, or `neighborhood`

Examples:
```python
wkls.us.wkt()                          # country: United States
wkls.us.ca.wkt()                       # region: California
wkls.us.ca.sanfrancisco.wkt()          # city/county: San Francisco
wkls["us"]["ca"]["sanfrancisco"].wkt() # dictionary-style access
```

Supported formats:
- `.wkt()` – Well-Known Text
- `.wkb()` – Raw binary WKB
- `.hexwkb()` – Hex-encoded WKB
- `.geojson()` – GeoJSON string
- `.svg()` – SVG path string

### 🔎 What does `wkls.us.ca.sanfrancisco` return?

Chained expressions like wkls.us.ca.sanfrancisco return a Wkl object. Internally, this holds a Pandas DataFrame containing one or more rows that match the given chain.

```python
        id           country    region   subtype       name           division_id
0  085718963fffff...   US       US-CA    county    San Francisco  085718963fffff...
```

In most cases, it resolves to a single administrative boundary — for example, San Francisco county or locality. But if there are name collisions (e.g., both a county and a locality called “San Francisco”), multiple rows may be returned.

By default, geometry methods like `.wkt()` will use the first matching row.

### 🧠 Helper methods

The following methods return Pandas DataFrames for easy exploration:

| Method                     | Description                        |
|----------------------------|------------------------------------|
| `wkls.countries()`         | List all countries                 |
| `wkls.us.regions()`        | List regions in the US             |
| `wkls.us.ca.counties()`    | List counties in California        |
| `wkls.us.ca.cities()`      | List cities in California          |
| `wkls.subtypes()`          | Show all distinct division subtypes |


## How It Works

WKLS works in two stages:

### 1. 🧩 In-memory GERS ID resolution

Your chained attributes — up to 3 levels — are parsed in this order:

1. `country` → matched by ISO 2-letter code (e.g. `"us"`)
2. `region` → matched using region ISO code suffix (e.g. `"ca"` → `"US-CA"`)
3. `place` → fuzzy-matched against names in subtypes: `county`, `locality`, or `neighborhood`

This resolves to a Pandas DataFrame containing one or more rows from the in-memory wkls metadata table. At this stage, no geometry is loaded yet — only metadata (like id, name, region, subtype, etc.).

### 2. 📡 Geometry lookup using DuckDB

The geometry lookup is triggered only when you call one of the geometry methods:
- `.wkt()`
- `.wkb()`
- `.hexwkb()`
- `.geojson()`
- `.svg()`

At that point, WKLS uses the previously resolved **GERS ID** to query the Overture **division_area** GeoParquet directly from S3.

# Contributing

Feel free to submit a pull request with additional WKTs!

You can also create an issue to discuss ideas before writing any code.

You can also check issues with the "help wanted" tag for contribution ideas.

## Developing

You can run the test suite with `uv run pytest tests`.
