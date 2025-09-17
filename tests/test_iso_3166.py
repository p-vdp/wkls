import pytest
import iso3166_2

import wkls


@pytest.fixture
def iso():
    return iso3166_2.Subdivisions()


@pytest.fixture
def iso_countries(iso) -> set[str]:
    return set(iso.all.keys())


@pytest.fixture
def iso_subdivisions(iso, iso_countries) -> set[str]:
    subdivisions = list()
    for country in iso_countries:
        subdivisions.extend(list(iso.all[country].keys()))
    return set(subdivisions)


@pytest.fixture
def wkls_countries() -> set[str]:
    # noinspection PyUnresolvedReferences
    return set(wkls.countries()["country"].tolist())


@pytest.fixture
def wkls_regions(wkls_countries) -> set[str]:
    regions = list()
    for country in wkls_countries:
        # noinspection PyUnresolvedReferences
        for region in wkls[country].regions()["region"].tolist():
            if region:
                regions.append(region)
    return set(regions)


def test_compare_countries(iso_countries, wkls_countries):
    assert len(wkls_countries) == len(iso_countries), (
        f"\n{len(iso_countries - wkls_countries)} countries in ISO 3166 not in wkls: {sorted(iso_countries - wkls_countries)}\n"
        f"{len(wkls_countries - iso_countries)} countries in wkls not in ISO 3166: {sorted(wkls_countries - iso_countries)}"
    )


def test_compare_regions(iso_subdivisions, wkls_regions):
    assert len(wkls_regions) == len(iso_subdivisions), (
        f"\n{len(iso_subdivisions - wkls_regions)} regions in ISO 3166 not in wkls: {sorted(iso_subdivisions - wkls_regions)}\n"
        f"{len(wkls_regions - iso_subdivisions)} regions in wkls not in ISO 3166: {sorted(wkls_regions - iso_subdivisions)}"
    )
