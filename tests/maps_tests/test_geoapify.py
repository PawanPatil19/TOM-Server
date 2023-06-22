import pytest

from io import BytesIO
from PIL import Image

from modules.maps.maps import get_static_maps
from tests.maps_tests.test_map_util import compare_images, coordinates, size


@pytest.mark.asyncio
async def test_find_static_maps_geoapify():
    image_data = await get_static_maps(coordinates, size, 0)
    actual_image = Image.open(BytesIO(image_data))
    assert actual_image.size == size
    assert actual_image.format == 'JPEG'

    expected_image = Image.open("map_images/geoapify/static_map_1.jpeg")
    similarity = compare_images(actual_image, expected_image, 5)
    assert similarity > 0.9
