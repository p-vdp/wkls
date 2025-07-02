import wkts

def test_access():
    
    assert(wkts.us.wkt().startswith("MULTIPOLYGON (((-160.4596628 21.8841845"))
    assert(wkts.us.ca.wkt().startswith("MULTIPOLYGON (((-119.621653 33.309252"))
    assert(wkts.us.ny.cityofnewyork.wkt().startswith("MULTIPOLYGON (((-74.046176 40.691092"))
    assert(wkts.us.ca.sanfrancisco.wkt().startswith("MULTIPOLYGON (((-122.9915659 37.7672733"))
    assert(wkts.us.ca.sanfrancisco.wkt().startswith("MULTIPOLYGON (((-122.9915659 37.7672733"))

    assert(len(wkts.countries()) == 219)
    assert(len(wkts.us.regions()) == 51)
    assert(len(wkts["IN"]["MH"].counties()) == 36)
    assert(len(wkts["IN"]["MH"].cities()) == 321)

    # Pass regex
    # assert(len(wkts["us"]["ca"]["%San Francisco%"]) == 2)

    # print("\n", wkts.us.ca.sanfrancisco)
    # print("\n", wkts['us']['ca']['San Francisco'])
    print("\ncountries: ")
    print(wkts.countries().head(200))
    print(wkts.countries().count())
    print("\nregions: ")
    print(wkts.IN.regions().head(10))
    print("\counties: ")
    print(wkts.IN.mh.counties().head(10))
    print("\ncities: ")
    print(wkts.IN.mh.cities().head(20))
    print("\nMumbai: ")
    print(wkts["in"]["mh"]["%Mumbai City%"])
    print("\nSan Francisco: ")
    print(wkts["us"]["ca"]["%San Francisco%"])
    # print("\nsubtypes: ")
    # print(wkts.subtypes().head(10))