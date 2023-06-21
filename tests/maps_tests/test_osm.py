import pytest

from modules.maps.location_data import LocationData
from modules.maps.maps import get_locations

locations_sample_response_osm = [LocationData(
    address='Marina Bay Sands, 10, Bayfront Avenue, Bayfront, Downtown Core, Singapore, Central, 018956, Singapore',
    name='Marina Bay Sands', latitude=1.2836965, longitude=103.8607226), LocationData(
    address='Marina Bay Sands, Bayfront Link, Bayfront, Downtown Core, Singapore, Central, 018940, Singapore',
    name='Marina Bay Sands', latitude=1.2817723, longitude=103.8574685), LocationData(
    address='Marina Bay Sands, Bayfront Avenue, Bayfront, Downtown Core, Singapore, Central, 018971, Singapore',
    name='Marina Bay Sands', latitude=1.2856255, longitude=103.8610678)]


@pytest.mark.asyncio
async def test_locations_osm_success():
    response = await get_locations("Marina Bay Sands", 0)
    assert response == locations_sample_response_osm
