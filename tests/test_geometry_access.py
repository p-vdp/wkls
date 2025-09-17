import json

import pytest

import wkls


@pytest.fixture
def sf() -> wkls.Wkl:
    # noinspection PyUnresolvedReferences
    return wkls.us.ca.sanfrancisco


def test_wkt(sf):
    geom = sf.wkt()
    assert isinstance(geom, str)
    assert geom.startswith("MULTIPOLYGON")


def test_wkb(sf):
    geom = sf.wkb()
    assert isinstance(geom, bytearray)


def test_hexwkb(sf):
    geom = sf.hexwkb()
    assert isinstance(geom, str)


def test_geojson(sf):
    geom = sf.geojson()
    geom = json.loads(geom)
    assert isinstance(geom, dict)


def test_svg(sf):
    geom = sf.svg()
    assert isinstance(geom, str)
