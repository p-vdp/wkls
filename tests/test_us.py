import wkls


def test_access():
    assert wkls.us.wkt().startswith("MULTIPOLYGON (((-160.4596628 21.8841845")
    assert wkls.us.ca.wkt().startswith("MULTIPOLYGON (((-119.621653 33.309252")
    assert wkls.us.ny.cityofnewyork.wkt().startswith(
        "MULTIPOLYGON (((-74.046176 40.691092"
    )
    assert wkls.us.ca.sanfrancisco.wkt().startswith(
        "MULTIPOLYGON (((-122.9915659 37.7672733"
    )

    assert len(wkls.countries()) == 219
    assert len(wkls.us.regions()) == 51
    assert len(wkls["IN"]["MH"].counties()) == 36
    assert len(wkls["IN"]["MH"].cities()) == 321

    # Test San Francisco search returns DataFrame directly
    san_francisco_results = wkls["us"]["ca"]["%San Francisco%"]
    assert len(san_francisco_results) == 2, (
        "San Francisco search should return exactly two results"
    )
    assert "San Francisco" in san_francisco_results["name"].str.cat(sep=" "), (
        "Results should contain San Francisco"
    )

    # Test subtypes
    subtypes_df = wkls.subtypes()
    expected_subtypes = ["country", "region", "county", "locality", "localadmin"]
    for subtype in expected_subtypes:
        assert subtype in subtypes_df["subtype"].values, (
            f"Subtype '{subtype}' should exist"
        )
