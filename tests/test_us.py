import wkts

def test_access():
    print("wkt output:", wkts.us.ca.wkt()[:250] + "...")
    print("wkt output:", wkts.us.ca.sanfrancisco.wkt()[:250] + "...")
    print("wkt output:", wkts.us.ny.cityofnewyork.wkt()[:250] + "...")
    assert(wkts.us.ca.wkt().startswith("MULTIPOLYGON (((-119.621653 33.309252"))
