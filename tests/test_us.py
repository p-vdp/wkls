import wkts

def test_access():
    
    assert(wkts.us.wkt().startswith("MULTIPOLYGON (((-160.4596628 21.8841845"))
    assert(wkts.us.ca.wkt().startswith("MULTIPOLYGON (((-119.621653 33.309252"))
    assert(wkts.us.ny.cityofnewyork.wkt().startswith("MULTIPOLYGON (((-74.046176 40.691092"))
    assert(wkts.us.ca.sanfrancisco.wkt().startswith("MULTIPOLYGON (((-122.9915659 37.7672733"))

    assert(len(wkts.countries()) == 219)
    assert(len(wkts.us.regions()) == 51)
    assert(len(wkts["IN"]["MH"].counties()) == 36)
    assert(len(wkts["IN"]["MH"].cities()) == 321)

    # Test San Francisco search returns DataFrame directly
    san_francisco_results = wkts["us"]["ca"]["%San Francisco%"]
    assert len(san_francisco_results) > 0, "San Francisco search should return at least one result"
    assert "San Francisco" in san_francisco_results["name"].str.cat(sep=" "), "Results should contain San Francisco"
    
    # Test Seattle search returns DataFrame directly
    seattle_results = wkts["us"]["wa"]["%Seattle%"]
    assert len(seattle_results) > 0, "Seattle search should return at least one result"
    assert seattle_results["country"].iloc[0] == "US", "Seattle should be in the US"
    assert "Seattle" in seattle_results["name"].iloc[0], "Result should contain Seattle"
    
    # Test subtypes
    subtypes_df = wkts.subtypes()
    expected_subtypes = ["country", "region", "county", "locality", "localadmin"]
    for subtype in expected_subtypes:
        assert subtype in subtypes_df["subtype"].values, f"Subtype '{subtype}' should exist"