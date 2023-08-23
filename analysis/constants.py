from enum import Enum

class ResultType(Enum):
    MILLIS = 0
    SECONDS = 1
    INDEX = 2


LABELS = {
    "accelerometer": "acc",
    "gyroscope": "gyr",
    "magnetometer": "mag",
}

UNITS = {
    "accelerometer": "$m/s^2$",
    "gyroscope": "$deg/s$",
    "magnetometer": "$gauss$",
}

ACC_TO_SI = 9.81

DATA_TAGS = ["Left Wrist", "Right Wrist", "Shoulder", "Object"]
ACC_TAGS = ["".join(x) for x in zip(sorted(tuple(DATA_TAGS) * 3), (' [accX]', ' [accY]', ' [accZ]') * 4)]

UI_FORWARD_TOUCH_VIEW = "right"
UI_BACKWARD_TOUCH_VIEW = "left"
UI_CALIBRATION_VIEW = "c"
UI_SHOW_HELP = "f1"
UI_IGNORE_PRESSES = ['shift', 'win', 'control', 'ctrl', 'alt', 'escape']