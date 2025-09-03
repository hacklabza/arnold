import logging
import math
import statistics
from typing import Optional

from mpu9250_jmdev.mpu_9250 import MPU9250

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
        )

        # Set the bias from a previous calibration using the saved config
        self.sensor.abias = self.config['bias']['accelerometer']
        self.sensor.gbias = self.config['bias']['gyroscope']
        self.sensor.mbias = self.config['bias']['magnetometer']

        self.sensor.configure()

    def _get_data(self, data: list) -> dict:
        """
        Map the x, y & z list to a dict and round the readings.

        Args:
            data (dict): The original axes to be mapped

        Returns:
            dict: Mapped axes dict
        """
        x, y, z = data
        return {'x': x, 'y': y, 'z': z}

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

    def get_accelerometer_data(self, sample_size: int | None = None) -> dict:
        """
        Get the current accelerometer data from the module.

        Args:
            sample_size (int | None): The number of samples to take. If None,
            uses the default from config.

        Returns:
            dict: X, Y & Z
        """
        accelerometer_samples = []
        sample_size = sample_size or self.config['sample_size']
        for _ in range(sample_size):
            accelerometer_samples.append(
                self._get_data(self.sensor.readAccelerometerMaster())
            )

        # Get the mean of all samples taken by the sensor
        data = {
            'x': statistics.mean([sample['x'] for sample in accelerometer_samples]),
            'y': statistics.mean([sample['y'] for sample in accelerometer_samples]),
            'z': statistics.mean([sample['z'] for sample in accelerometer_samples]),
        }

        self._logger.info(f'Accelerometer: {data}')
        return self._map_orientation(data)

    def get_gyroscope_data(self, sample_size: int | None = None) -> dict:
        """
        Get the current gyroscope data from the module.

        Args:
            sample_size (int | None): The number of samples to take. If None,
            uses the default from config.

        Returns:
            dict: X, Y & Z
        """
        gyroscope_samples = []
        sample_size = sample_size or self.config['sample_size']
        for _ in range(sample_size):
            gyroscope_samples.append(
                self._get_data(self.sensor.readGyroscopeMaster())
            )

        # Get the mean of all samples taken by the sensor
        data = {
            'x': statistics.mean([sample['x'] for sample in gyroscope_samples]),
            'y': statistics.mean([sample['y'] for sample in gyroscope_samples]),
            'z': statistics.mean([sample['z'] for sample in gyroscope_samples]),
        }

        self._logger.info(f'Gyroscope: {data}')
        return self._map_orientation(data)

    def get_magnetometer_data(self, sample_size: int | None = None) -> dict:
        """
        Get the current magnetometer data from the module.

        Args:
            sample_size (int | None): The number of samples to take. If None,
            uses the default from config.

        Returns:
            dict: X, Y & Z
        """
        magnetometer_samples = []
        sample_size = sample_size or self.config['sample_size']
        for _ in range(sample_size):
            magnetometer_samples.append(
                self._get_data(self.sensor.readMagnetometerMaster())
            )

        # Get the mean of all samples taken by the sensor
        data = {
            'x': statistics.mean([sample['x'] for sample in magnetometer_samples]),
            'y': statistics.mean([sample['y'] for sample in magnetometer_samples]),
            'z': statistics.mean([sample['z'] for sample in magnetometer_samples]),
        }
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
            dict: Roll, pitch and yaw degree estimates
        """
        accelerometer_data = accelerometer_data or self.get_accelerometer_data()
        magnetometer_data = magnetometer_data or self.get_magnetometer_data()

        roll = math.atan2(
            accelerometer_data['x'],
            math.sqrt(accelerometer_data['y'] ** 2 + accelerometer_data['z'] ** 2)
        )
        pitch = math.atan2(
            accelerometer_data['y'],
            math.sqrt(accelerometer_data['x'] ** 2 + accelerometer_data['z'] ** 2)
        )

        # Tilt-compensated magnetometer
        magnetometer_x = magnetometer_data['x']
        magnetometer_y = magnetometer_data['y']
        magnetometer_z = magnetometer_data['z']

        # Apply tilt compensation
        magnetometer_x_tilt = magnetometer_x * math.cos(pitch) + magnetometer_z * math.sin(pitch)
        magnetometer_y_tilt = (
            magnetometer_x * math.sin(roll) * math.sin(pitch) + magnetometer_y *
            math.cos(roll) - magnetometer_z * math.sin(roll) * math.cos(pitch)
        )

        yaw = math.atan2(-magnetometer_y_tilt, magnetometer_x_tilt)

        return {
            'roll': math.degrees(roll),
            'pitch': math.degrees(pitch),
            'yaw': math.degrees(yaw)
        }
