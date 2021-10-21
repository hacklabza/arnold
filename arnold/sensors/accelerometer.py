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

    def __init__(
        self,
        address: Optional[str] = None,
        orientation: Optional[dict] = None
    ) -> None:
        self.config = config.SENSOR['accelerometer']

        # Module config
        self.address = int(address or self.config['address'], 16)
        self.orientation = orientation or self.config['orientation']

        # Setup logging
        self._logger = _logger

        self.sensor = adxl345.ADXL345(address=self.address)

    def _map_orientation(self, axes: dict) -> dict:
        """Map the x, y & z axes based on the physical orientation of the module.

        Args:
            axes (dict): The original axes to be mapped

        Returns:
            dict: Mapped axes dict
        """
        return {
            new_key: axes[old_key]
            for new_key, old_key in self.orientation.items()
        }

    def get_axes(self) -> dict:
        """Get the current axes from the module.

        Returns:
            dict: X, Y & Z axes
        """
        axes = self.sensor.get_axes()
        self._logger.info(f'Axes: {axes}')
        return self._map_orientation(axes)
