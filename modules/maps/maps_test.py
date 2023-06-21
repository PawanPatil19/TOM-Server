import pytest

from modules.maps.direction_data import DirectionData
from modules.maps.location_data import LocationData
from modules.maps.maps import get_locations, get_directions

locations_sample_response_osm = [LocationData(
    address='Marina Bay Sands, 10, Bayfront Avenue, Bayfront, Downtown Core, Singapore, Central, 018956, Singapore',
    name='Marina Bay Sands', latitude=1.2836965, longitude=103.8607226), LocationData(
    address='Marina Bay Sands, Bayfront Link, Bayfront, Downtown Core, Singapore, Central, 018940, Singapore',
    name='Marina Bay Sands', latitude=1.2817723, longitude=103.8574685), LocationData(
    address='Marina Bay Sands, Bayfront Avenue, Bayfront, Downtown Core, Singapore, Central, 018971, Singapore',
    name='Marina Bay Sands', latitude=1.2856255, longitude=103.8610678)]

locations_sample_response_google = [
    LocationData(address='Computing Dr, Singapore', name='The Deck', latitude=1.2944323, longitude=103.7725605),
    LocationData(address='Ang Mo Kio Ave 8, Singapore', name='The Deck', latitude=1.3682795, longitude=103.8503844),
    LocationData(address='120A Prinsep St, Singapore 187937', name='DECK', latitude=1.3017242, longitude=103.8516775),
    LocationData(address='2 Andover Rd, Singapore 509984', name='The Deck Bar by Changi Beach Club', latitude=1.3909075,
                 longitude=103.9748168),
    LocationData(address='20 Warwick Rd, Singapore 139010', name='The Deck', latitude=1.288321, longitude=103.7978444),
    LocationData(address='209 Henderson Rd, Singapore 159551', name='The Deck', latitude=1.2815748,
                 longitude=103.8199716),
    LocationData(address='2 Kallang Ave, #01-K1, Singapore 339407', name='Deck Bar', latitude=1.3124182,
                 longitude=103.8631868),
    LocationData(address='#01-26, 111 Jln Hang Jebat, Singapore 139532', name='The Deck Media Group Pte. Ltd.',
                 latitude=1.2823257, longitude=103.8455755)]

directions_sample_response_google = DirectionData(start_time=0, update_time=1687242228802, dest_dist=587,
                                                  dest_dist_str='0.6 km', dest_duration=457, dest_duration_str='8 mins',
                                                  curr_dist=192, curr_dist_str='0.2 km', curr_duration=128,
                                                  curr_duration_str='2 mins',
                                                  curr_instr='Head south on Business Link toward Heng Mui Keng Terrace',
                                                  curr_direction='straight', next_direction='turn-right',
                                                  error_message='')

directions_sample_response_ors = DirectionData(start_time=0, update_time=1687246877438, dest_dist=2458,
                                               dest_dist_str='2458 m', dest_duration=1770, dest_duration_str='30 min',
                                               curr_dist=21, curr_dist_str='21 m', curr_duration=15,
                                               curr_duration_str='1 min', curr_instr='Head south on 5, 5',
                                               curr_direction='u-turn', next_direction='turn-right',
                                               error_message='')


@pytest.mark.asyncio
async def test_locations_osm_success():
    response = await get_locations("Marina Bay Sands", 0)
    assert response == locations_sample_response_osm


@pytest.mark.asyncio
async def test_locations_google_success():
    response = await get_locations("The Deck", 1)
    assert response == locations_sample_response_google


@pytest.mark.asyncio
async def test_directions_ors_api_success():
    response = await get_directions(51.5311558, -0.1233187, 51.5136558, -0.123213, 0, 0)
    assert response.start_time == directions_sample_response_ors.start_time
    assert abs(response.dest_dist - directions_sample_response_ors.dest_dist) <= 5
    assert abs(response.dest_duration - directions_sample_response_ors.dest_duration) <= 5
    assert abs(response.curr_dist - directions_sample_response_ors.curr_dist) <= 5
    assert abs(response.curr_duration - directions_sample_response_ors.curr_duration) <= 5
    assert response.curr_instr == directions_sample_response_ors.curr_instr
    assert response.curr_direction == directions_sample_response_ors.curr_direction
    assert response.next_direction == directions_sample_response_ors.next_direction
    assert response.error_message == directions_sample_response_ors.error_message


@pytest.mark.asyncio
async def test_directions_ors_localhost_success():
    response = await get_directions(51.5311558, -0.1233187, 51.5136558, -0.123213, 0, 1)
    assert response.start_time == directions_sample_response_ors.start_time
    assert abs(response.dest_dist - directions_sample_response_ors.dest_dist) <= 5
    assert abs(response.dest_duration - directions_sample_response_ors.dest_duration) <= 5
    assert abs(response.curr_dist - directions_sample_response_ors.curr_dist) <= 5
    assert abs(response.curr_duration - directions_sample_response_ors.curr_duration) <= 5
    assert response.curr_instr == directions_sample_response_ors.curr_instr
    assert response.curr_direction == directions_sample_response_ors.curr_direction
    assert response.next_direction == directions_sample_response_ors.next_direction
    assert response.error_message == directions_sample_response_ors.error_message


@pytest.mark.asyncio
async def test_directions_google_success():
    response = await get_directions(1.2936937, 103.7752589, 1.293326, 103.7715489, 1)
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
