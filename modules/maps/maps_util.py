def calculate_turn_angle(bearing_before, bearing_after):
    angle = bearing_after - bearing_before
    if angle < 0:
        angle += 360
    return angle
