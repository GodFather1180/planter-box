import explorerhat
from math import exp

MAX_MOISTURE = 4.5
LEVEL_THRESHOLD = 1

soil_input = explorerhat.analog.one
level_input = explorerhat.analog.two


def moisture_level():
    sensor_data = soil_input.read()

    # Assume sensor values are exponential
    ratio = exp(sensor_data) / exp(MAX_MOISTURE)

    return int(ratio * 100)


def reservoir_level():
    return explorerhat.analog.two.read()


def reservoir_low():
    return reservoir_level() < 1