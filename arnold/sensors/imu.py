import logging
from typing import Optional

from mpu9250_jmdev.mpu_9250 import MPU9250
from mpu9250_jmdev.registers import AK8963_MODE_C100HZ

from arnold import config


_logger = logging.getLogger(__name__)


class IMU(object):
    """A sensor class which gets data from the acceleration, gyroscope, temperature
    sensor and magnetometer on the MPU-9250 module.

    Args:
        address (str, optional): I2C address of the device
        orientation (dict, optional): Orientation map based on the physical position
            of the module on Arnold
    """

    def __init__(
        self,
        address: Optional[str] = None,
        orientation: Optional[dict] = None
    ) -> None:
        self.config = config.SENSOR['imu']

        # Module config
        self.address = int(address or self.config['address'], 16)
        self.orientation = orientation or self.config['orientation']

        # Setup logging
        self._logger = _logger

        self.sensor = MPU9250(
            address_mpu_master=self.address,
            mode=AK8963_MODE_C100HZ
        )
        self.sensor.configure()

    def _get_data(self, data: list) -> dict:
        """Map the x, y & z list to a dict.

        Args:
            data (dict): The original axes to be mapped

        Returns:
            dict: Mapped axes dict
        """
        return {'x': data[0], 'y': data[1], 'z': data[2]}

    def _map_orientation(self, data: dict) -> dict:
        """Map x, y & z based on the physical orientation of the module.

        Args:
            data (dict): The original axes to be mapped

        Returns:
            dict: Mapped axes dict
        """
        return {
            new_key: data[old_key]
            for new_key, old_key in self.orientation.items()
        }

    def calibrate(self) -> None:
        """Calibrate all 3 MPU-9250 sensors.
        """
        self.sensor.calibrate()

    def get_accelerometer_data(self) -> dict:
        """Get the current accelerometer data from the module.

        Returns:
            dict: X, Y & Z
        """
        data = self._get_data(
            self.sensor.readAccelerometerMaster()
        )
        self._logger.info(f'Accelerometer: {data}')
        return self._map_orientation(data)

    def get_gyroscope_data(self) -> dict:
        """Get the current gyroscope data from the module.

        Returns:
            dict: X, Y & Z
        """
        data = self._get_data(
            self.sensor.readGyroscopeMaster()
        )
        self._logger.info(f'Gyroscope: {data}')
        return self._map_orientation(data)

    def get_magnetometer_data(self) -> dict:
        """Get the current magnetometer data from the module.

        Returns:
            dict: X, Y & Z
        """
        data = self._get_data(
            self.sensor.readMagnetometerMaster()
        )
        self._logger.info(f'Magnetometer: {data}')
        return self._map_orientation(data)

    def get_temperature(self) -> float:
        """Get the current temperature from the module.

        Returns:
            float: Temperature in celsius
        """
        temperature = self.sensor.readTemperatureMaster()
        self._logger.info(f'Temperature: {temperature}')
        return temperature
