
from . import running_display as running_display
from . import running_data_handler as running_data_handler

class RunningTrainingMode(Enum):
    SpeedTraining = 0
    DistanceTraining= 1


def start_training(training_mode, training_route, training_speed = None):
    if training_mode == RunningTrainingMode.SpeedTraining:
        start_speed_training(training_route, training_speed)
    elif training_mode == RunningTrainingMode.DistanceTraining:
        start_distance_training(training_route)
    else:
        print('Unsupported training mode')

def start_speed_training(training_route, training_speed):
    # FIXME: Implement this
    # decide the route
    # show all running info intermittently (say evey 400m for 5 seconds - customizable parameters)
    # show the running speed intermittently when it's higher/lower than the target speed (+ error) - const, may be give visual instructions also


    pass

def start_distance_training(training_route):
    # FIXME: Implement this
    pass