import logging
from time import sleep
from typing import Optional

from gpiozero import Motor

from arnold.config import MOTION_CONFIG
from arnold.utils import InterruptibleDelay


_logger = logging.getLogger(__name__)


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
        pause_duration: Optional[float] = None,
        enable_pwm: Optional[bool] = None
    ) -> None:
        self.config = MOTION_CONFIG['drivetrain']

        # Pin configuration
        self.gpio_config = self.config['gpio']
        self.enable_pwm = self.config['enable_pwm'] if enable_pwm is None else enable_pwm

        # Motor setup
        self.left_motor = Motor(
            *self.config['gpio']['left']['pins'], pwm=self.enable_pwm
        )
        self.right_motor = Motor(
            *self.config['gpio']['right']['pins'], pwm=self.enable_pwm
        )

        # Setup logging
        self._logger = _logger

        # Pause duration and delay class setup
        self.pause_duration = pause_duration or self.config['pause_duration']
        self.delay = InterruptibleDelay(halt_callback=self._pause)

    def release(self):
        """Release the device pins for both motors.
        """
        self.right_motor.close()
        self.left_motor.close()

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
            'right': ['forward', 'backward'],
            'left': ['backward', 'forward']
        }

    @property
    def status(self) -> dict:
        """The current status of the motors.

        Returns:
            dict: left and right motor activity a boolean
        """
        return {
            'left': {
                'direction': self._get_motor_direction(self.left_motor),
                'is_active': self.left_motor.is_active,
            },
            'right': {
                'direction': self._get_motor_direction(self.right_motor),
                'is_active': self.right_motor.is_active,
            }
        }

    def _get_motor_direction(self, motor: Motor) -> str:
        """Get the current direction for a motor instance.

        Args:
            motor (Motor): A motor instance

        Returns:
            str: The direction it is current set to: forward, back or stopped
        """
        if motor.forward_device.value:
            return 'forward'
        elif motor.backward_device.value:
            return 'back'
        return 'stopped'


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
        if self.delay.is_active():
            self.stop()
            sleep(self.pause_duration)

        try:
            left, right = self._direction_map[direction]
        except KeyError:
            raise KeyError(
                f'Mapping not found for direction `{direction}`'
            )
        else:
            getattr(self.left_motor, left)(speed)
            getattr(self.right_motor, right)(speed)

        self.delay.async_delay(duration)

    def forward(self, duration: int) -> None:
        self.go('forward', duration)

    def back(self, duration: int) -> None:
        self.go('back', duration)

    def turn(self, direction: str, duration: int) -> None:
        self.go(direction, duration)

    def stop(self) -> None:
        self.delay.terminate()
        self._pause()
