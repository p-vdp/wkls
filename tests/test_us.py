import wkt

def test_state_wkt():
    expected = "POLYGON((-109.0448 37.0004,-102.0424 36.9949,-102.0534 41.0006,-109.0489 40.9996,-109.0448 37.0004,-109.0448 37.0004))"
    assert(wkt.us.states.colorado() == expected)
