import modules.utilities.time as time_utility


class CurrentData:
    curr_heart_rate = 0  # bpm
    curr_distance = 0.0  # km
    prev_distance = 0.0  # km
    avg_speed = -1.0  # min/km

    start_time = 0.0
    start_time_string = time_utility.get_date_string("%d %B %I:%M %p")
    start_place = 'NUS'
    exercise_type = 'Running'

    curr_lat = 0.0
    curr_lng = 0.0

    curr_route = []  # list of predefined coordinates by user? that have not been reached yet
    coords = []  # actual coordinates user has travelled

    map_size = (600, 400)  # width, height
    bearing = 0
    total_steps = 0
    curr_steps = 0

    @classmethod
    def reset_values(cls):
        cls.curr_heart_rate = 0
        cls.curr_distance = 0.0
        cls.prev_distance = 0.0
        cls.avg_speed = -1.0

        cls.start_time = 0.0
        cls.start_time_string = time_utility.get_date_string("%d %B %I:%M %p")
        cls.start_place = 'NUS'
        cls.exercise_type = 'Running'

        cls.curr_lat = 0.0
        cls.curr_lng = 0.0

        cls.curr_route = []
        cls.coords = []

        cls.map_size = (600, 400)
        cls.bearing = 0
        cls.total_steps = 0
        cls.curr_steps = 0
