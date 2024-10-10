import logging
import math
from typing import Optional

from mpu9250_jmdev.mpu_9250 import MPU9250
from mpu9250_jmdev.registers import AK8963_MODE_C100HZ

from arnold import config


_logger = logging.getLogger(__name__)


class IMU(object):
    """
    A sensor class which gets data from the acceleration, gyroscope, temperature
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
            mode=AK8963_MODE_C100HZ,
        )

        # Set the bias from a previous calibration using the saved config
        self.abias = self.config['bias']['accelerometer']
        self.gbias = self.config['bias']['gyroscope']
        self.mbias = self.config['bias']['magnetometer']

        self.sensor.configure()

    def _get_data(self, data: list) -> dict:
        """
        Map the x, y & z list to a dict and round the readings.

        Args:
            data (dict): The original axes to be mapped

        Returns:
            dict: Mapped axes dict
        """
        return {'x': data[0], 'y': data[1], 'z': data[2]}

    def _map_orientation(self, data: dict) -> dict:
        """
        Map x, y & z based on the physical orientation of the module.

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
        """
        Calibrate all 3 MPU-9250 sensors.
        """
        self.sensor.calibrate()

    def get_accelerometer_data(self) -> dict:
        """
        Get the current accelerometer data from the module.

        Returns:
            dict: X, Y & Z
        """
        data = self._get_data(
            self.sensor.readAccelerometerMaster()
        )
        self._logger.info(f'Accelerometer: {data}')
        return self._map_orientation(data)

    def get_gyroscope_data(self) -> dict:
        """
        Get the current gyroscope data from the module.

        Returns:
            dict: X, Y & Z
        """
        data = self._get_data(
            self.sensor.readGyroscopeMaster()
        )
        self._logger.info(f'Gyroscope: {data}')
        return self._map_orientation(data)

    def get_magnetometer_data(self) -> dict:
        """
        Get the current magnetometer data from the module.

        Returns:
            dict: X, Y & Z
        """
        data = self._get_data(
            self.sensor.readMagnetometerMaster()
        )
        self._logger.info(f'Magnetometer: {data}')
        return self._map_orientation(data)

    def get_temperature(self) -> float:
        """
        Get the current temperature from the module.

        Returns:
            float: Temperature in celsius
        """
        temperature = self.sensor.readTemperatureMaster()
        self._logger.info(f'Temperature: {temperature}')
        return temperature

    def get_attitude(
        self,
        accelerometer_data: Optional[dict] = None,
        magnetometer_data: Optional[dict] = None,
    ) -> dict:
        """
        Get the roll, pitch and yaw as calculated by the 9 axes module.

        Args:
            accelerometer_data (dict): Accelerometer's x, y, z data. Defaults to
            getting the data from the sensor
            magnetometer_data (dict): Magnetometer's x, y, z data. Defaults to getting
            the data from the sensor

        Returns:
            dict: Roll, pitch and yaw estimates
        """
        accelerometer_data = accelerometer_data or self.get_accelerometer_data()
        magnetometer_data = magnetometer_data or self.get_magnetometer_data()

        roll = 180 * math.atan2(
            accelerometer_data['x'],
            math.sqrt(
                (accelerometer_data['y'] * accelerometer_data['y']) +
                (accelerometer_data['z'] * accelerometer_data['z'])
            ) / math.pi
        )
        pitch = 180 * math.atan2(
            accelerometer_data['y'],
            math.sqrt(
                (
                    (accelerometer_data['x'] * accelerometer_data['x']) +
                    (accelerometer_data['z'] * accelerometer_data['z'])
                ) / math.pi
            )
        )
        yaw = 180 * math.atan2(
            -(
                (magnetometer_data['y'] * math.cos(roll)) -
                (magnetometer_data['z'] * math.sin(roll))
            ),
            (
                (magnetometer_data['x'] * math.cos(pitch)) +
                (magnetometer_data['y'] * math.sin(roll) * math.sin(pitch)) +
                (magnetometer_data['z'] * math.cos(roll) * math.sin(pitch))
            ) / math.pi
        )

        return {
            'roll': roll,
            'pitch': pitch,
            'yaw': yaw
        }
