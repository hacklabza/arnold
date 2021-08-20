from time import sleep
from typing import Optional

from gpiozero import Motor

from arnold.config import MOTION_CONFIG
from arnold.utils import InterruptibleDelay


class PauseDurationError(Exception):
    def __init__(self, message: Optional[str]):
        self.message = message or 'The pause duration must be greater than 0.1.'
        super().__init__(message)


class DriveTrain(object):
    """A controller class which initialises the motor gpio instances for the
    left and right hand side of Arnold.

    Args:
        config (dict, optional): A dict containing left and right pin configs
        pause_duration (float, optional): The duration to pause between direction
            changes
        enable_pwm (bool, optional): Set the Driver to use pwm or not
    """

    def __init__(
        self,
        config: Optional[dict] = None,
        pause_duration: Optional[float] = None,
        enable_pwm: Optional[bool] = None
    ):
        self.config = config or MOTION_CONFIG['drivetrain']
        self.gpio_config = self.config['gpio']
        self.enable_pwm = self.config['enable_pwm'] if enable_pwm is None else enable_pwm

        self.left_motor = Motor(
            *self.config['gpio']['left']['pins'], pwm=self.enable_pwm
        )
        self.right_motor = Motor(
            *self.config['gpio']['right']['pins'], pwm=self.enable_pwm
        )

        self.pause_duration = pause_duration or self.config['pause_duration']

        self.delay = InterruptibleDelay(halt_callback=self._pause)


    @property
    def _direction_map(self) -> dict:
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

    @property
    def status(self) -> dict:
        """The current status of the motors.

        Returns:
            dict: left and right motor activity a boolean
        """
        return {
            'left': self.left_motor.is_active,
            'right': self.right_motor.is_active
        }

    def _pause(self) -> None:
        """Pauses motion between commands preventing weird seg faults.

        Raises:
            PauseDurationError: Raised if the pause duration is too
            low to prevent seg fault
        """
        if self.pause_duration < 0.1:
            raise PauseDurationError()

        self.left_motor.stop()
        self.right_motor.stop()
        sleep(self.pause_duration)

    def _delay(self, duration: int) -> None:
        if self.delay.is_active():
            self.stop()
        self.delay.async_delay(duration)

    def go(self, direction: str, duration: int, speed: Optional[float]=1) -> None:
        """Move Arnold in a specific direction for a specified duration.

        Args:
            direction (str): stop, forward, backward, right or left.
            duration (int): the durance to run the motors in secs.
            speed (int, optional): The speed of the motors 0.0-1.0. Defaults to
                0.5.

        Raises:
            KeyError: Raised if the direction map has been configured
                incorrectly.
        """
        try:
            left, right = self._direction_map[direction]
        except KeyError:
            raise KeyError(
                f'Mapping not found for direction `{direction}`'
            )
        else:
            getattr(self.left_motor, left)(speed)
            getattr(self.right_motor, right)(speed)

        self._delay(duration)

    def forward(self, duration: int) -> None:
        self.go('forward', duration)

    def back(self, duration: int) -> None:
        self.go('back', duration)

    def turn(self, direction: str, duration: int) -> None:
        self.go(direction, duration)

    def stop(self) -> None:
        self.delay.terminate()
