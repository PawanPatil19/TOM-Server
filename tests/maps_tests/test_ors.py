import pytest

from modules.maps.direction_data import DirectionData
from modules.maps.maps import get_directions

directions_sample_response_ors = DirectionData(start_time=0, update_time=1687246877438, dest_dist=2458,
                                               dest_dist_str='2458 m', dest_duration=1770, dest_duration_str='30 min',
                                               curr_dist=21, curr_dist_str='21 m', curr_duration=15,
                                               curr_duration_str='1 min', curr_instr='Head south on 5, 5',
                                               curr_direction='u-turn', next_direction='turn-right',
                                               error_message='')


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


# make sure to start docker first with map data covering greater london area
# https://download.geofabrik.de/europe/great-britain/england/greater-london.html
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
