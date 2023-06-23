import logging
import socket

from modules.geoapify_api import geoapify_api
from modules.maps.direction_data import DirectionData
from modules.ors_api import ors_api
from modules.osm_api import osm_api
from modules.google_api import google_api
from googlemaps.exceptions import ApiError


async def get_walking_directions(start_time, src_lat, src_lng, dest_lat, dest_lng, bearing, option, ors_option=0):
    direction_data = DirectionData()
    try:
        if option == 0:
            # Use OpenRouteService API
            direction_data = await ors_api.find_directions_ors(start_time, src_lat, src_lng, dest_lat, dest_lng,
                                                               bearing, ors_option)
        elif option == 1:
            # Use Google Maps Directions API
            direction_data = await google_api.find_directions_google(start_time, src_lat, src_lng, dest_lat, dest_lng,
                                                                     bearing)
    except Exception as e:
        error_message = str(e)
        if isinstance(e, ApiError):
            error_message = "Google Maps API error occurred. Please try again later."
        # elif isinstance(e, MaxRouteLengthExceededException):
        #     error_message = "Route length exceeded. Please try again with a different location."
        elif isinstance(e, socket.timeout):
            error_message = "Connection timed out. Please check your internet connection."
        elif isinstance(e, socket.gaierror):
            error_message = "Failed to resolve hostname. Please check your internet connection."
        elif isinstance(e, socket.error):
            error_message = "Failed to connect to the server. Please check your internet connection."
        logging.error("get_directions: %s", error_message)
        direction_data.error_message = error_message

    return direction_data


async def get_locations(search_text, option, location=None):
    try:
        if option == 0:
            # Use Nominatim OpenStreetMap API
            return await osm_api.find_locations_osm(search_text)
        elif option == 1:
            # Use Google Maps Places API
            return await google_api.find_locations_google(search_text, location)
    except Exception as e:
        error_message = str(e)
        if isinstance(e, ApiError):
            error_message = "Google Maps API error occurred. Please try again later."
        elif isinstance(e, socket.timeout):
            error_message = "Connection timed out. Please check your internet connection."
        elif isinstance(e, socket.gaierror):
            error_message = "Failed to resolve hostname. Please check your internet connection."
        elif isinstance(e, socket.error):
            error_message = "Failed to connect to the server. Please check your internet connection."
        logging.error("get_locations: %s", error_message)
        return list()


async def get_static_maps(coordinates, size, option):
    try:
        if option == 0:
            return await geoapify_api.find_static_maps_geoapify(coordinates, size)
        elif option == 1:
            return await google_api.find_static_maps_google(coordinates, size)
    except Exception as e:
        error_message = str(e)
        if isinstance(e, ApiError):
            error_message = "Google Maps API error occurred. Please try again later."
        elif isinstance(e, socket.timeout):
            error_message = "Connection timed out. Please check your internet connection."
        elif isinstance(e, socket.gaierror):
            error_message = "Failed to resolve hostname. Please check your internet connection."
        elif isinstance(e, socket.error):
            error_message = "Failed to connect to the server. Please check your internet connection."
        logging.error("get_static_maps: %s", error_message)
