def get_directions_from_bearings(bearing_before, bearing_after):
    bearing_diff = bearing_after - bearing_before

    if bearing_diff in range(-10, 11) or bearing_diff in range(350, 361) or bearing_diff in range(-360, -349):
        return "straight"
    elif bearing_diff in range(170, 191) or bearing_diff in range(-190, -169):
        return "u-turn"
    elif bearing_diff in range(11, 46) or bearing_diff in range(-225, -190):
        return "turn-slight-right"
    elif bearing_diff in range(46, 136) or bearing_diff in range(-315, -225):
        return "turn-right"
    elif bearing_diff in range(136, 170) or bearing_diff in range(-349, -315):
        return "turn-sharp-right"
    elif bearing_diff in range(316, 350) or bearing_diff in range(-45, -10):
        return "turn-slight-left"
    elif bearing_diff in range(226, 316) or bearing_diff in range(-135, -45):
        return "turn-left"
    elif bearing_diff in range(191, 226) or bearing_diff in range(-169, -136):
        return "turn-sharp-left"
    else:
        return "unknown"