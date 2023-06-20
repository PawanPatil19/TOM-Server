from dataclasses import dataclass


@dataclass
class DirectionData:
    # Refers to the system time of the watch when an exercise has started. Stored in ms.
    start_time: int = 0
    # Refers to the system time of the server when the data is updated. Stored in ms.
    update_time: int = 0
    # Refers to the total distance from current location to destination set by the user. Stored in meters.
    dest_dist: int = 0
    # same as above but in string format.
    dest_dist_str: str = ""
    # Refers to the total estimated time to reach the destination set by the user. Stored in seconds.
    dest_duration: int = 0
    # same as above but in string format.
    dest_duration_str: str = ""
    # Refers to the current step distance from the current location to the next step. Stored in meters.
    curr_dist: int = 0
    # Same as above but in string format.
    curr_dist_str: str = ""
    # Refers to the duration needed to walk from the current location to the next step. Stored in seconds.
    curr_duration: int = 0
    # Same as above but in string format.
    curr_duration_str: str = ""
    # Text instruction of which road to take, for example.
    curr_instr: str = ""
    # consists of 5 possible values: "turn-left", "turn-slightly-left", "turn-right", "turn-slightly-right", "straight"
    curr_direction: str = ""
    # Refers to the next direction turn to take.
    next_direction: str = ""
    error_message: str = ""
