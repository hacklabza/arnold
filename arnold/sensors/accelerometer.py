import logging
from typing import Optional

import adxl345

from arnold import config


_logger = logging.getLogger(__name__)


class Accelerometer(object):
    """A sensor class which gets 3-axes acceleration from an ADXL345 module.

    Args:
        address (str, optional): The I2C address of the device
    """

    def __init__(self, address: Optional[str] = None) -> None:
        self.config = config.SENSOR['accelerometer']

        # Module config
        self.address = address or config['address']

        # Setup logging
        self._logger = _logger

        self.sensor = adxl345.ADXL345(address=hex(int(self.address, 16)))

    def get_axes(self) -> dict:
        """Get the current axes from the module.

        Returns:
            dict: X, Y & Z axes
        """
        return self.sensor.get_axes()
