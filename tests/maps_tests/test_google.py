import pytest

from modules.maps.direction_data import DirectionData
from modules.maps.location_data import LocationData
from modules.maps.maps import get_locations, get_walking_directions

locations_sample_response_google = [
    LocationData(address='Computing Dr, Singapore', name='The Deck', latitude=1.2944323, longitude=103.7725605),
    LocationData(address='20 Warwick Rd, Singapore 139010', name='The Deck', latitude=1.288321, longitude=103.7978444)]

directions_sample_response_google = DirectionData(start_time=0, update_time=1687242228802, dest_dist=587,
                                                  dest_dist_str='0.6 km', dest_duration=457, dest_duration_str='8 mins',
                                                  curr_dist=192, curr_dist_str='0.2 km', curr_duration=128,
                                                  curr_duration_str='2 mins',
                                                  curr_instr='Head south on Business Link toward Heng Mui Keng Terrace',
                                                  curr_direction='straight', next_direction='turn-right',
                                                  error_message='')


# sometimes returns no results not sure why
@pytest.mark.asyncio
async def test_locations_google_success():
    response = await get_locations("The Deck", 1)
    assert response == locations_sample_response_google


@pytest.mark.asyncio
async def test_directions_google_success():
    response = await get_walking_directions(1.2936937, 103.7752589, 1.293326, 103.7715489, 1)
    assert response.start_time == directions_sample_response_google.start_time
    assert response.dest_dist == directions_sample_response_google.dest_dist
    assert response.dest_dist_str == directions_sample_response_google.dest_dist_str
    assert response.dest_duration == directions_sample_response_google.dest_duration
    assert response.dest_duration_str == directions_sample_response_google.dest_duration_str
    assert response.curr_dist == directions_sample_response_google.curr_dist
    assert response.curr_dist_str == directions_sample_response_google.curr_dist_str
    assert response.curr_duration == directions_sample_response_google.curr_duration
    assert response.curr_duration_str == directions_sample_response_google.curr_duration_str
    assert response.curr_instr == directions_sample_response_google.curr_instr
    assert response.curr_direction == directions_sample_response_google.curr_direction
    assert response.next_direction == directions_sample_response_google.next_direction
    assert response.error_message == directions_sample_response_google.error_message
