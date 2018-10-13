from time import sleep


class Motion(object):
    def __init__(self, left_motor, right_motor, pause_duration=None):
        self.left_motor = left_motor
        self.right_motor = right_motor
        self.pause_duration = pause_duration or 0.2

    def _direction_map(self):
        """Maps directions to motor instances, left first than right.
        """
        return {
            "stop": ["stop", "stop"],
            "forward": ["forward", "forward"],
            "backward": ["backward", "backward"],
            "right": ["backward", "forward"],
            "left": ["forward", "backward"]
        }

    def _pause(self):
        """Pauses motion between commands preventing weird seg faults
        """
        self.left_motor.stop()
        self.right_motor.stop()
        sleep(self.pause_duration)

    def move(self, direction, speed=1, duration=None):
        try:
            left, right = self._direction_map()[direction]
        except KeyError:
            raise AttributeError(
                "Mapping not found for direction '{}'".format(direction)
            )
        else:
            getattr(self.left_motor, left)(speed)
            getattr(self.right_motor, right)(speed)

        if duration is not None:
            sleep(duration)
            self._pause()

    def status(self):
        return {
            "left": self.left_motor.is_active,
            "right": self.right_motor.is_active
        }
