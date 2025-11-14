import pytest
from server import search_indicators, get_observations


@pytest.mark.asyncio
async def test_search_indicators_basic():
    """Test basic search for indicators"""
    result = await search_indicators.fn(
        query="population",
        places=["United States"],
        per_search_limit=5,
        include_topics=False,
        maybe_bilateral=False
    )

    assert result is not None
    assert hasattr(result, 'variables')
    assert hasattr(result, 'dcid_name_mappings')
    assert hasattr(result, 'status')
    assert result.status == "SUCCESS"
    # Should find population-related variables
    assert len(result.variables) > 0


@pytest.mark.asyncio
async def test_search_indicators_with_topics():
    """Test search including topics"""
    result = await search_indicators.fn(
        query="health",
        places=["California, USA"],
        per_search_limit=5,
        include_topics=True,
        maybe_bilateral=False
    )

    assert result is not None
    assert hasattr(result, 'topics')
    assert hasattr(result, 'variables')
    assert result.status == "SUCCESS"


@pytest.mark.asyncio
async def test_search_indicators_multiple_places():
    """Test search with multiple places"""
    result = await search_indicators.fn(
        query="GDP",
        places=["United States", "Canada", "Mexico"],
        per_search_limit=5,
        include_topics=False,
        maybe_bilateral=False
    )

    assert result is not None
    assert result.status == "SUCCESS"
    assert len(result.variables) > 0
    # Should have place mappings
    assert len(result.dcid_name_mappings) > 0


@pytest.mark.asyncio
async def test_search_indicators_child_places():
    """Test search with parent place and child sampling"""
    result = await search_indicators.fn(
        query="unemployment",
        places=["California, USA", "Texas, USA", "Florida, USA"],
        parent_place="United States",
        per_search_limit=5,
        include_topics=False,
        maybe_bilateral=False
    )

    assert result is not None
    assert result.status == "SUCCESS"
    assert hasattr(result, 'resolved_parent_place')
    assert result.resolved_parent_place is not None


@pytest.mark.asyncio
async def test_get_observations_latest():
    """Test getting latest observation for a place"""
    result = await get_observations.fn(
        variable_dcid="Count_Person",
        place_dcid="country/USA",
        date="latest"
    )

    assert result is not None
    assert hasattr(result, 'place_observations')
    assert len(result.place_observations) > 0
    # Should have at least one observation
    place_obs = result.place_observations[0]
    assert hasattr(place_obs, 'place')
    assert hasattr(place_obs, 'time_series')
    assert len(place_obs.time_series) > 0


@pytest.mark.asyncio
async def test_get_observations_date_range():
    """Test getting observations with date range"""
    result = await get_observations.fn(
        variable_dcid="Count_Person",
        place_dcid="country/USA",
        date="range",
        date_range_start="2020",
        date_range_end="2022"
    )

    assert result is not None
    assert len(result.place_observations) > 0
    place_obs = result.place_observations[0]
    assert len(place_obs.time_series) > 0
    # Verify dates are within range
    for date_str, value in place_obs.time_series:
        year = int(date_str.split('-')[0])
        assert 2020 <= year <= 2022


@pytest.mark.asyncio
async def test_get_observations_specific_date():
    """Test getting observation for a specific date"""
    result = await get_observations.fn(
        variable_dcid="Count_Person",
        place_dcid="country/USA",
        date="2020"
    )

    assert result is not None
    assert len(result.place_observations) > 0
    place_obs = result.place_observations[0]
    # Should have data for or near 2020
    assert len(place_obs.time_series) > 0
