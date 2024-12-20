from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

from collections import deque
from enum import Enum
from math import ceil
import time

from .sensor import moisture_level, reservoir_low

# Define some arbitrary period (and steps) for which we assume will be enough to
# fully extend/retract cover
COVER_PERIOD = 30
COVER_STEPS = 10000


# Define types of motors, direction
class MotorType(Enum):
    STEPPER = 1
    DC = 2


class MotorDirection(Enum):
    FORWARD = 1
    BACKWARD = 2


# Whether shade is extended or retracted (or in between)
class ShadeStatus(Enum):
    RETRACTED = 1
    EXTENDED = 2
    # RETRACTING = 3
    # EXTENDING = 4


# Class definition for controlling motor/pump mechanisms
class PlanterControl:

    def __init__(self, threshold=60, backoff=10, motor=MotorType.DC):
        # Moisture threshold (when to stop watering).
        self._moisture_threshold = threshold

        # Backoff period (to prevent overheating).
        self._backoff = backoff

        # Activation statuses (off by default).
        self._waterOn = False
        self._shadeOn = False

        # Shade status
        self._shadeStatus = ShadeStatus.RETRACTED

        # Buffer for previous moisture levels.
        self._prev_moisture = deque(10 * [moisture_level()], 10)

        # Select type of motor used
        self._motortype = motor
        self._kit = MotorKit()

        if motor == MotorType.DC:
            self._motor = self._kit.motor1
            self._pump = self._kit.motor2
        else:
            self._motor = self._kit.stepper1
            self._pump = self._kit.motor3

    # Getter/setters.
    @property
    def moisture_threshold(self):
        return self._moisture_threshold

    @moisture_threshold.setter
    def moisture_threshold(self, val):
        self._moisture_threshold = val

    @property
    def previous_moisture(self):
        return list(self._prev_moisture)

    # Operate motor (with manual stop).
    def __operate_motor(self, incr, direction):
        if self._motortype == MotorType.DC:
            dc_dir = 1.0 if direction == MotorDirection.FORWARD else -1.0
            self._motor.throttle = dc_dir
            time.sleep(incr)
            self._motor.throttle = 0

        else:
            step_dir = (
                step.FORWARD
                if direction == MotorDirection.FORWARD
                else stepper.BACKWARD
            )

            for i in range(incr):
                self._motor.onestep(direction=step_dir, stype=stepper.DOUBLE)

    # Operate pump (single instance).
    def __operate_pump(self):
        self._pump.throttle = 1.0
        time.sleep(self._backoff)
        self._pump.throttle = 0

    # Run watering process over a period with constant backoff.
    def __run_water_backoff(self, period):
        reps = ceil(period / self._backoff)

        while reps > 0 and self._waterOn and not reservoir_low():
            self.__operate_pump()
            time.sleep(self._backoff)
            reps = reps - 1

    # Run shade in direction based on (assumed) previous position.
    def __run_shade(self):
        direction = (
            MotorDirection.FORWARD
            if self._shadeStatus == ShadeStatus.RETRACTED
            else MotorDirection.BACKWARD
        )

        incr = COVER_PERIOD if self._motortype == MotorType.DC else COVER_STEPS

        self.__operate_motor(incr, direction)

        self._shadeStatus = (
            ShadeStatus.EXTENDED
            if self._shadeStatus == ShadeStatus.RETRACTED
            else ShadeStatus.RETRACTED
        )

    # Manually toggle shade on/off.
    # TODO: incorporate button for detecting completion of movement.
    def toggle_shade(self, status):
        self._shadeOn = status == "on"

        if self._shadeOn:
            self.__run_shade()

    # Manually turn watering system on off for some time (or arbitrarily long if
    # no period defined).
    def toggle_water(self, status, period):
        self._waterOn = status == "on"

        if self._waterOn:
            self.__run_water_backoff(period if period else 100000)
        else:
            self._kit.motor2.throttle = 0

    # Returns true if previous moisture data shows rate is increasing on average
    # TODO: set rate at which rain is considered "heavy"
    def __moisture_increase(self):
        prev_list = list(self._prev_moisture)
        diff = [prev_list[i + 1] - prev_list[i] for i in range(len(prev_list) - 1)]
        return (sum(diff) / len(diff)) > 0

    # Update moisture levels
    def update_moisture(self):
        self._prev_moisture.append(moisture_level())

    # Turn shade on if moisture increase (i.e. rain) and shade retracted
    def auto_shade(self):
        if self.__moisture_increase() and self.shadeStatus == ShadeStatus.RETRACTED:
            self.__run_shade()

    # Water until soil moisture is at threshold
    def auto_water(self):
        if moisture_level() < self._moisture_threshold and not reservoir_low():
            self.__operate_pump()