import logging
from time import sleep
from typing import Optional

from gpiozero import GPIODeviceError, Motor

from arnold import config
from arnold.utils import InterruptibleDelay


_logger = logging.getLogger(__name__)


class PauseDurationError(Exception):
    def __init__(self, message: Optional[str]):
        self.message = message or 'The pause duration must be greater than 0.1.'
        super().__init__(message)


class DriveTrain(object):
    """
    A controller class which initialises the motor gpio instances for the
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
        self.config = config.MOTION['drivetrain']

        # Pin configuration
        self.gpio_config = self.config['gpio']
        self.enable_pwm = self.config['enable_pwm'] if enable_pwm is None else enable_pwm

        # Motor setup
        self.left_motor, self.right_motor = self.init_motors()

        # Setup logging
        self._logger = _logger

        # Pause duration and delay class setup
        self.pause_duration = pause_duration or self.config['pause_duration']
        self.delay = InterruptibleDelay(halt_callback=self._pause)

    def init_motors(self) -> None:
        """
        Initialise the motors.
        """
        try:
            left_motor = Motor(
                *self.config['gpio']['left']['pins'], pwm=self.enable_pwm
            )
            right_motor = Motor(
                *self.config['gpio']['right']['pins'], pwm=self.enable_pwm
            )
        except GPIODeviceError as exc:
            self._logger.warning(exc)
            self.delay.terminate()
            self.release()
            left_motor = Motor(
                *self.config['gpio']['left']['pins'], pwm=self.enable_pwm
            )
            right_motor = Motor(
                *self.config['gpio']['right']['pins'], pwm=self.enable_pwm
            )

        return left_motor, right_motor

    def release(self):
        """
        Release the device pins for both motors.
        """
        self.right_motor.close()
        self.left_motor.close()
        self._logger.info(f'GPIO pins released')

    @property
    def _direction_map(self) -> dict:
        """
        Maps directions to motor instances.

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
        """
        The current status of the motors.

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

    @property
    def is_active(self) -> bool:
        """
        Shortcut to assert if drivetrain is active.

        Returns:
            bool: either left or right motor is active
        """
        is_active = self.delay.is_active()
        self._logger.info(f'Is Active: {is_active}')
        return is_active

    def _get_motor_direction(self, motor: Motor) -> str:
        """
        Get the current direction for a motor instance.

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
        """
        Pauses motion between commands preventing weird seg faults.

        Raises:
            PauseDurationError: Raised if the pause duration is too low to prevent
            seg fault
        """
        if self.pause_duration < 0.1:
            raise PauseDurationError()

        self.left_motor.stop()
        self.right_motor.stop()
        sleep(self.pause_duration)

    def go(
        self,
        direction: str,
        duration: Optional[int] = 30,
        speed: Optional[float] = 1.0
    ) -> None:
        """
        Move Arnold in a specific direction for a specified duration.

        Args:
            direction (str): stop, forward, backward, right or left.
            duration (int, optional): the durance to run the motors in secs. Defaults to
            30 secs.
            speed (int, optional): The speed of the motors 0.0-1.0. Defaults to 1.0.

        Raises:
            KeyError: Raised if the direction map has been configured incorrectly.
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

    def forward(self, duration: Optional[int]) -> None:
        """
        Move Arnold forward for the specified duration.

        Args:
            duration (int, optional): The duration to run the motors in seconds.
            Defaults to 30 seconds.
        """
        self._logger.info(f'Go Forward: {duration} sec')
        self.go('forward', duration)

    def back(self, duration: Optional[int]) -> None:
        """
        Move Arnold back for the specified duration.

        Args:
            duration (int, optional): The duration to run the motors in seconds.
            Defaults to 30 seconds.
        """
        self._logger.info(f'Go Back: {duration} sec')
        self.go('back', duration)

    def turn(self, direction: str, duration: Optional[int]) -> None:
        """
        Turn Arnold in a specific direction for the specified duration.

        Args:
            direction (str): right or left.
            duration (int, optional): The duration to run the motors in seconds.
            Defaults to 30 seconds.
        """
        self._logger.info(f'Go {direction.capitalize()}: {duration} sec')
        self.go(direction, duration)

    def stop(self) -> None:
        """
        Stops Arnold's motion by terminating the delay and pausing the motors.
        """
        self.delay.terminate()
        self._pause()
        self._logger.info(f'Stopped')
