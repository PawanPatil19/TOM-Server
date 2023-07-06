import pytest

from modules.maps.direction_data import DirectionData
from modules.maps.maps import get_walking_directions

directions_sample_response_ors = DirectionData(start_time=0, update_time=1688547782347, dest_dist=1572,
                                               dest_dist_str='1572 m', dest_duration=1132, dest_duration_str='19 min',
                                               curr_dist=36, curr_dist_str='36 m', curr_duration=26,
                                               curr_duration_str='1 min', curr_instr='Head east on Northbound, 7',
                                               curr_direction='42', num_steps='26', waypoint_dist=350,
                                               waypoint_dist_str='350 m', waypoint_duration=252,
                                               waypoint_duration_str='5 min', error_message='')

waypoints = [[51.5305457, -0.1243116], [51.5305794, -0.1211179], [51.531307, -0.1103626], [51.5330346, -0.1057646]]


@pytest.mark.asyncio
async def test_directions_ors_api_success():
    response = await get_walking_directions(0, waypoints, 45, 0)
    assert response.start_time == directions_sample_response_ors.start_time
    assert abs(response.dest_dist - directions_sample_response_ors.dest_dist) <= 5
    assert abs(response.dest_duration - directions_sample_response_ors.dest_duration) <= 5
    assert abs(response.curr_dist - directions_sample_response_ors.curr_dist) <= 5
    assert abs(response.curr_duration - directions_sample_response_ors.curr_duration) <= 5
    assert response.curr_instr == directions_sample_response_ors.curr_instr
    assert response.curr_direction == directions_sample_response_ors.curr_direction
    assert response.num_steps == directions_sample_response_ors.num_steps
    assert response.waypoint_dist == directions_sample_response_ors.waypoint_dist
    assert response.waypoint_dist_str == directions_sample_response_ors.waypoint_dist_str
    assert response.waypoint_duration == directions_sample_response_ors.waypoint_duration
    assert response.waypoint_duration_str == directions_sample_response_ors.waypoint_duration_str
    assert response.error_message == directions_sample_response_ors.error_message


# make sure to start docker first with map data covering greater london area
# https://download.geofabrik.de/europe/great-britain/england/greater-london.html
@pytest.mark.asyncio
async def test_directions_ors_localhost_success():
    response = await get_walking_directions(0, waypoints, 45, 0, 1)
    assert response.start_time == directions_sample_response_ors.start_time
    assert abs(response.dest_dist - directions_sample_response_ors.dest_dist) <= 5
    assert abs(response.dest_duration - directions_sample_response_ors.dest_duration) <= 5
    assert abs(response.curr_dist - directions_sample_response_ors.curr_dist) <= 5
    assert abs(response.curr_duration - directions_sample_response_ors.curr_duration) <= 5
    assert response.curr_instr == directions_sample_response_ors.curr_instr
    assert response.curr_direction == directions_sample_response_ors.curr_direction
    assert response.num_steps == directions_sample_response_ors.num_steps
    assert response.waypoint_dist == directions_sample_response_ors.waypoint_dist
    assert response.waypoint_dist_str == directions_sample_response_ors.waypoint_dist_str
    assert response.waypoint_duration == directions_sample_response_ors.waypoint_duration
    assert response.waypoint_duration_str == directions_sample_response_ors.waypoint_duration_str
    assert response.error_message == directions_sample_response_ors.error_message
