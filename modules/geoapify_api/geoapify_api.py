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

    coordinates_str = "|".join(
        [f"lonlat:{lng},{lat};color:%230000ff;type:material;size:small;iconsize:small;size:small" for lat, lng in
         coordinates])
    path_str = "polyline:" + ",".join(f"{lng},{lat}" for lat, lng in coordinates) + ";linecolor:%23ff0000"

    url = f"{base_url}?apiKey={api_key}&width={size[0]}&height={size[1]}&marker={coordinates_str}&geometry={path_str}"

    response = requests.get(url)

    if response.status_code == 200:
        # Uncomment to save image in a jpg file
        # image = Image.open(BytesIO(response.content))
        # image.save("static_map_1.jpeg", format="JPEG", quality=100)

        return response.content
    else:
        print(response)
        error_data = json.loads(response.content)
        error_message = error_data.get("message", "Unknown error")
        raise Exception(error_message)
