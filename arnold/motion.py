from time import sleep


class Motion(object):
    def __init__(self, left_motor, right_motor):
        self.left_motor = left_motor,
        self.right_motor = right_motor

    def _direction_map(self):
        """Maps directions to motor instances, left first than right.
        """
        return {
            "stop": ["stop", "stop"],
            "forward": ["forward", "forward"],
            "backward": ["backward", "backward"],
            "right": ["backward", "forward"],
            "right": ["forward", "backward"]
        }

    def move(self, direction, speed=1, duration=None):
        try:
            left, right = self._direction_map()[direction]
        except KeyError:
            raise AttributeError("Mapping not found for direction '{}'".format(attr))
        finally:
            getattr(self.left_motor, left)(speed)
            getattr(self.right_motor, right)(speed)

        if duration is not None:
            sleep(duration)
