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

DATA_TAGS = ["Left Wrist", "Right Wrist", "Shoulder", "Object"]

UI_FORWARD_TOUCH_VIEW = "."
UI_BACKWARD_TOUCH_VIEW = ","
UI_CALIBRATION_VIEW = "c"