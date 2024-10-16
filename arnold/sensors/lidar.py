import logging
import serial
import statistics
from typing import Optional

from arnold import config


_logger = logging.getLogger(__name__)


class Lidar(object):
    """
    A sensor class which gets the distance from the lidar module to the closest
    object in range.

    Args:
        serial_port (str, optional): The serial port which the lidar sensor is
        connect to (UART)
        baud_rate (int, optional): The communication baud rate
    """

    def __init__(
        self,
        serial_port: Optional[str] = None,
        baudrate: Optional[int] = None
    ) -> None:
        self.config = config.SENSOR['lidar']

        # UART serial config
        self.serial_port = serial_port or self.config['serial_port']
        self.baudrate = baudrate or self.config['baudrate']

        # Setup logging
        self._logger = _logger

        self.lidar_sensor = serial.Serial(
            port=self.serial_port,
            baudrate=self.baudrate
        )

    def get_distance(self) -> int:
        """
        The calculated distance to the nearest object in range.

        Returns:
            int: Distance in cm to the closest object
        """
        distance = 0
        while True:

            counter = self.lidar_sensor.in_waiting
            if counter > 8:
                bytes_serial = self.lidar_sensor.read(9)

                if bytes_serial[0] == 0x59 and bytes_serial[1] == 0x59:
                    distance = (bytes_serial[2] + bytes_serial[3])
                    self.lidar_sensor.reset_input_buffer()
                    break

                self.lidar_sensor.reset_input_buffer()

        self._logger.info(f'Distance: {distance}')

        return distance

    def get_mean_distance(self, sample_size: int) -> int:
        """
        The calculated the mean distance to the nearest object in range for a
        selected sample size.

        Args:
            sample_size (int): Sample size to take measurement of

        Returns:
            int: The mean distance in cm to the closest object
        """
        return int(
            statistics.mean([self.get_distance() for _ in range(sample_size)])
        )

