from time import sleep
from typing import Optional

from gpiozero import Motor

from arnold.config import MOTION_CONFIG
from arnold.motion import exceptions


class Drive(object):
    """A controller class which initialises the motor gpio instances for the
    left and right hand side of Arnold.

    Args:
        config (dict, optional): A dict containing left and right pin configs.
        pause_duration (float, optional): The duration to pause between direction
        changes.
    """

    def __init__(self, config: Optional[dict], pause_duration: Optional[float]):
        self.config = config or MOTION_CONFIG

        self.gpio_config = self.config['gpio']
        self.left_motor = Motor(*self.config['gpio']['left'])
        self.right_motor = Motor(*self.config['gpio']['right'])

        self.pause_duration = pause_duration or self.config['pause_duration']

    def _direction_map(self):
        """Maps directions to motor instances.

        Returns:
            dict: motor direction mapping with in order value [left, right]
        """
        return {
            'stop': ['stop', 'stop'],
            'forward': ['forward', 'forward'],
            'back': ['backward', 'backward'],
            'right': ['backward', 'forward'],
            'left': ['forward', 'backward']
        }

    def _pause(self):
        """Pauses motion between commands preventing weird seg faults.

        Raises:
            exceptions.PauseDurationError: Raised if the pause duration is too
            low to prevent seg fault
        """
        if self.pause_duration < 0.1:
            raise exceptions.PauseDurationError()

        self.left_motor.stop()
        self.right_motor.stop()
        sleep(self.pause_duration)


    def go(self, direction: str, duration: int, speed: Optional[float]=0.5):
        """Move Arnold in a specific direction for a specified duration.

        Args:
            direction (str): stop, forward, backward, right or left.
            duration (int): the durance to of the motion in secs.
            speed (int, optional): The speed of the motors 0.0-1.0. Defaults to
            0.5.


        Raises:
            KeyError: Raised if the direction map has been configured
            incorrectly.
        """
        try:
            left, right = self._direction_map()[direction]
        except KeyError:
            raise KeyError(
                f'Mapping not found for direction `{direction}`'
            )
        else:
            getattr(self.left_motor, left)(speed)
            getattr(self.right_motor, right)(speed)

        if duration is not None:
            sleep(duration)
            self._pause()

    @property
    def status(self):
        """The current status of the motors.

        Returns:
            dict: left and right motor activity a boolean
        """
        return {
            'left': self.left_motor.is_active,
            'right': self.right_motor.is_active
        }
