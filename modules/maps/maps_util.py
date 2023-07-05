from geographiclib.geodesic import Geodesic


def calculate_turn_angle(bearing_before, bearing_after):
    angle = bearing_after - bearing_before
    if angle < 0:
        angle += 360
    return angle


def get_direction_str(angle):
    if angle > 350 or angle < 10:
        return "straight"
    else:
        direction_map = {
            (10, 45): "turn_slight_right",
            (45, 135): "turn_right",
            (135, 170): "turn_sharp_right",
            (170, 190): "u_turn",
            (190, 225): "turn_sharp_left",
            (225, 315): "turn_left",
            (315, 350): "turn_slight_left"
        }
        for direction_range, direction in direction_map.items():
            if direction_range[0] <= angle < direction_range[1]:
                return direction

# from https://stackoverflow.com/a/54875237/18753727
def calculate_bearing_after(src_lat, src_lng, dest_lat, dest_lng):
    return int(Geodesic.WGS84.Inverse(src_lat, src_lng, dest_lat, dest_lng)['azi1'])


def calculate_distance(lat1, lng1, lat2, lng2):
    return Geodesic.WGS84.Inverse(lat1, lng1, lat2, lng2)['s12']
