import wkts
import pandas as pd

def test_access():
    print("Access ID:", wkts.us.id)
    print("Access region_iso:", wkts.us.region_iso)
    print("Access region_iso:", wkts.us.ca.region_iso)
    print("Access name: ", wkts.us.ny.cityofnewyork.name)
    print("Access subtype:", wkts.us.ca.sanfrancisco.subtype)
    
    print(wkts.us.ca.sanfrancisco)
    print(wkts['us']['ca']['sanfrancisco'])

    sf = wkts.us.ca.sanfrancisco
    df = pd.DataFrame(sf.data)
    print(df.head(10))
    
    assert(wkts.us.wkt().startswith("MULTIPOLYGON (((-160.4596628 21.8841845"))
    assert(wkts.us.ca.wkt().startswith("MULTIPOLYGON (((-119.621653 33.309252"))
    assert(wkts.us.ny.cityofnewyork.wkt().startswith("MULTIPOLYGON (((-74.046176 40.691092"))
    assert(wkts.us.ca.sanfrancisco.wkt().startswith("MULTIPOLYGON (((-122.9915659 37.7672733"))
