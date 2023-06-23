from geographiclib.geodesic import Geodesic


def calculate_turn_angle(bearing_before, bearing_after):
    angle = bearing_after - bearing_before
    if angle < 0:
        angle += 360
    return angle


# from https://stackoverflow.com/a/54875237/18753727
def calculate_bearing_after(src_lat, src_lng, dest_lat, dest_lng):
    return int(Geodesic.WGS84.Inverse(src_lat, src_lng, dest_lat, dest_lng)['azi1'])
