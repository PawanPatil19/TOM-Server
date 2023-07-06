import pytest

from io import BytesIO
from modules.maps.direction_data import DirectionData
from modules.maps.location_data import LocationData
from modules.maps.maps import get_locations, get_walking_directions, get_static_maps
from PIL import Image
from tests.maps_tests.test_map_util import coordinates, size, compare_images

locations_sample_response_google = [LocationData(address='Computing Dr, Singapore',
                                                 name='The Deck',
                                                 latitude=1.2944323,
                                                 longitude=103.7725605),
                                    LocationData(address='Ang Mo Kio Ave 8, Singapore',
                                                 name='The Deck',
                                                 latitude=1.3682795,
                                                 longitude=103.8503844),
                                    LocationData(address='120A Prinsep St, Singapore 187937',
                                                 name='DECK',
                                                 latitude=1.3017242,
                                                 longitude=103.8516775),
                                    LocationData(address='2 Andover Rd, Singapore 509984',
                                                 name='The Deck Bar by Changi Beach Club',
                                                 latitude=1.3909075,
                                                 longitude=103.9748168),
                                    LocationData(address='20 Warwick Rd, Singapore 139010',
                                                 name='The Deck',
                                                 latitude=1.288321,
                                                 longitude=103.7978444),
                                    LocationData(address='209 Henderson Rd, Singapore 159551',
                                                 name='The Deck',
                                                 latitude=1.2815748,
                                                 longitude=103.8199716),
                                    LocationData(address='2 Kallang Ave, #01-K1, Singapore 339407',
                                                 name='Deck Bar',
                                                 latitude=1.3124182,
                                                 longitude=103.8631868),
                                    LocationData(address='#01-26, 111 Jln Hang Jebat, Singapore 139532',
                                                 name='The Deck Media Group Pte. Ltd.',
                                                 latitude=1.2823257,
                                                 longitude=103.8455755)]

directions_sample_response_google = DirectionData(start_time=0, update_time=1688547488474, dest_dist=1039,
                                                  dest_dist_str='1039 m', dest_duration=741, dest_duration_str='13 min',
                                                  curr_dist=35, curr_dist_str='35 m', curr_duration=33,
                                                  curr_duration_str='1 min',
                                                  curr_instr='Head west toward Kent Ridge Dr', curr_direction='189',
                                                  num_steps='9', waypoint_dist=251, waypoint_dist_str='0.3 km',
                                                  waypoint_duration=195, waypoint_duration_str='3 mins',
                                                  error_message='')

waypoints = [[1.2934043, 103.7730927], [1.2925769, 103.7725056], [1.2934142, 103.7704343], [1.2951112, 103.7697015]]


@pytest.mark.asyncio
async def test_locations_google_success():
    # current location is set to a default location to get consistent results
    response = await get_locations("The Deck", 1, (1.3369344, 103.9027994))
    assert response == locations_sample_response_google


@pytest.mark.asyncio
async def test_directions_google_success():
    response = await get_walking_directions(0, waypoints, 45, 1)
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
    assert response.num_steps == directions_sample_response_google.num_steps
    assert response.waypoint_dist == directions_sample_response_google.waypoint_dist
    assert response.waypoint_dist_str == directions_sample_response_google.waypoint_dist_str
    assert response.waypoint_duration == directions_sample_response_google.waypoint_duration
    assert response.waypoint_duration_str == directions_sample_response_google.waypoint_duration_str
    assert response.error_message == directions_sample_response_google.error_message


@pytest.mark.asyncio
async def test_static_maps_google_success():
    image_data = await get_static_maps(coordinates, size, 1)
    actual_image = Image.open(BytesIO(image_data))
    assert actual_image.size == size
    assert actual_image.format == 'JPEG'

    expected_image = Image.open("map_images/google/static_map_1.jpeg")
    similarity = compare_images(actual_image, expected_image, 5)
    assert similarity > 0.9
