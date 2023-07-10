import json
import requests

from config import GEOAPIFY_CREDENTIAL_FILE
from io import BytesIO

from PIL import Image

KEY_MAP_API = 'map_api_key'


# return {"map_api_key": "YYY"}
def read_geoapify_credential():
    print('Reading Geoapify credentials')
    with open(GEOAPIFY_CREDENTIAL_FILE, 'r') as f:
        credential = json.load(f)
    return credential


def get_geoapify_credential(key, credential=None):
    _credential = credential
    if _credential is None:
        _credential = read_geoapify_credential()

    return _credential[key]


async def find_static_maps_geoapify(coordinates, size):
    base_url = "https://maps.geoapify.com/v1/staticmap"
    api_key = get_geoapify_credential(KEY_MAP_API)
    start_coordinate = coordinates[0]
    markers_str = f"lonlat:{start_coordinate[1]},{start_coordinate[0]};color:%230000ff;type:material;size:small;iconsize:small"

    if len(coordinates) > 1:
        end_coordinate = coordinates[-1]
        markers_str += f"|lonlat:{end_coordinate[1]},{end_coordinate[0]};color:%23ff0000;type:material;size:small;iconsize:small"

    path_str = "polyline:" + ",".join(f"{lng},{lat}" for lat, lng in coordinates) + ";linecolor:%23ff0000"

    url = f"{base_url}?apiKey={api_key}&width={size[0]}&height={size[1]}&marker={markers_str}&geometry={path_str}"

    response = requests.get(url)

    if response.status_code == 200:
        # Uncomment to save image in a jpg file
        # image = Image.open(BytesIO(response.content))
        # image.show()
        # image.save("static_map_1.jpeg", format="JPEG", quality=100)

        return response.content
    else:
        error_data = json.loads(response.content)
        error_message = error_data.get("message", "Unknown error")
        raise Exception(error_message)
