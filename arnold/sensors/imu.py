import collections
import logging
import math
import statistics
import struct
import threading
import time
from typing import Optional, Union

from smbus2 import SMBus

from arnold import config


_logger = logging.getLogger(__name__)

AXES = ('x', 'y', 'z')
GRAVITY = 9.80665
CARDINALS = ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')


def _to_address(address: Union[str, int, None]) -> Optional[int]:
    """
    Convert a hex string address (as used in the config) to an int.
    """
    if address is None or isinstance(address, int):
        return address
    return int(address, 16)


def _angle_difference(target: float, source: float) -> float:
    """
    The shortest signed angle in degrees to get from source to target.
    """
    return (target - source + 180.0) % 360.0 - 180.0


def _cross(a: tuple, b: tuple) -> tuple:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


class I2CDevice(object):
    """
    Thin register level wrapper around a single device on the I2C bus.

    Args:
        bus (SMBus): The opened I2C bus
        address (int): I2C address of the device
    """

    def __init__(self, bus: SMBus, address: int) -> None:
        self.bus = bus
        self.address = address

    @staticmethod
    def probe(bus: SMBus, address: int) -> bool:
        """
        Check if a device acknowledges on the given address.
        """
        try:
            bus.read_byte(address)
            return True
        except OSError:
            return False

    def read_byte(self, register: int) -> int:
        return self.bus.read_byte_data(self.address, register)

    def write_byte(self, register: int, value: int) -> None:
        self.bus.write_byte_data(self.address, register, value & 0xFF)

    def read_block(self, register: int, length: int) -> bytes:
        return bytes(self.bus.read_i2c_block_data(self.address, register, length))


class ADXL345(I2CDevice):
    """
    ADXL345 3 axis accelerometer. Port of FIMU_ADXL345 from DFRobot's
    FreeSixIMU library. Readings are in g.
    """

    DEFAULT_ADDRESS = 0x53
    DEVICE_ID = 0xE5

    REG_DEVID = 0x00
    REG_BW_RATE = 0x2C
    REG_POWER_CTL = 0x2D
    REG_DATA_FORMAT = 0x31
    REG_DATAX0 = 0x32

    BW_RATE_100HZ = 0x0A
    DATA_FORMAT_FULL_RES_4G = 0x09
    POWER_CTL_MEASURE = 0x08

    # Full resolution mode is always 3.9mg/LSB regardless of range
    SCALE = 0.0039

    def setup(self) -> None:
        device_id = self.read_byte(self.REG_DEVID)
        if device_id != self.DEVICE_ID:
            _logger.warning(
                f'ADXL345 at {self.address:#04x} returned device id {device_id:#04x}, '
                f'expected {self.DEVICE_ID:#04x}'
            )
        self.write_byte(self.REG_BW_RATE, self.BW_RATE_100HZ)
        self.write_byte(self.REG_DATA_FORMAT, self.DATA_FORMAT_FULL_RES_4G)
        self.write_byte(self.REG_POWER_CTL, self.POWER_CTL_MEASURE)

    def read(self) -> tuple:
        """
        Returns:
            tuple: x, y & z acceleration in g
        """
        # Data is little endian, LSB first
        raw = struct.unpack('<hhh', self.read_block(self.REG_DATAX0, 6))
        return tuple(value * self.SCALE for value in raw)


class ITG3205(I2CDevice):
    """
    ITG3205 (ITG3200 compatible) 3 axis gyroscope. Port of FIMU_ITG3200 from
    DFRobot's FreeSixIMU library. Readings are in degrees per second.
    """

    DEFAULT_ADDRESS = 0x68

    REG_WHO_AM_I = 0x00
    REG_SMPLRT_DIV = 0x15
    REG_DLPF_FS = 0x16
    REG_TEMP_OUT = 0x1B
    REG_GYRO_XOUT = 0x1D
    REG_PWR_MGM = 0x3E

    PWR_MGM_RESET = 0x80
    PWR_MGM_PLL_X_GYRO = 0x01
    DLPF_FS_2000DPS = 0x18
    DLPF_CFG_42HZ = 0x03
    # 1kHz internal rate / (9 + 1) = 100Hz output
    SMPLRT_DIV_100HZ = 9

    STARTUP_DELAY = 0.07
    SCALE = 14.375  # LSB per deg/s

    def setup(self) -> None:
        who_am_i = self.read_byte(self.REG_WHO_AM_I) & 0x7E
        if who_am_i != 0x68:
            _logger.warning(
                f'ITG3205 at {self.address:#04x} returned who am i {who_am_i:#04x}, '
                'expected 0x68'
            )
        self.write_byte(self.REG_PWR_MGM, self.PWR_MGM_RESET)
        time.sleep(self.STARTUP_DELAY)
        self.write_byte(self.REG_SMPLRT_DIV, self.SMPLRT_DIV_100HZ)
        self.write_byte(self.REG_DLPF_FS, self.DLPF_FS_2000DPS | self.DLPF_CFG_42HZ)
        self.write_byte(self.REG_PWR_MGM, self.PWR_MGM_PLL_X_GYRO)
        time.sleep(self.STARTUP_DELAY)

    def read(self) -> tuple:
        """
        Returns:
            tuple: x, y & z rotation rate in deg/s
        """
        # Data is big endian, MSB first
        raw = struct.unpack('>hhh', self.read_block(self.REG_GYRO_XOUT, 6))
        return tuple(value / self.SCALE for value in raw)

    def read_temperature(self) -> float:
        """
        Returns:
            float: Die temperature in celsius
        """
        (raw,) = struct.unpack('>h', self.read_block(self.REG_TEMP_OUT, 2))
        return 35 + (raw + 13200) / 280.0


class Compass(I2CDevice):
    """
    3 axis magnetometer. Port of DFRobot_QMC5883 which supports the HMC5883L,
    QMC5883 and VCM5883L chips. The chip is identified by its I2C address.
    Readings are raw counts as only the direction of the field is used.

    Args:
        bus (SMBus): The opened I2C bus
        address (int): I2C address of the device
        chip (str): One of HMC5883L, QMC5883 or VCM5883L
    """

    HMC5883L = 'HMC5883L'
    QMC5883 = 'QMC5883'
    VCM5883L = 'VCM5883L'

    # Same detection order as the DFRobot library
    ADDRESSES = {
        HMC5883L: 0x1E,
        QMC5883: 0x0D,
        VCM5883L: 0x0C,
    }

    def __init__(self, bus: SMBus, address: int, chip: str) -> None:
        super().__init__(bus, address)
        self.chip = chip

    @classmethod
    def detect(cls, bus: SMBus, address: Optional[int] = None) -> Optional['Compass']:
        """
        Find a supported compass chip on the bus.

        Args:
            bus (SMBus): The opened I2C bus
            address (int, optional): Only look for a chip on this address

        Returns:
            Compass | None: The detected compass or None if not found
        """
        for chip, chip_address in cls.ADDRESSES.items():
            if address is not None and address != chip_address:
                continue
            if cls.probe(bus, chip_address):
                return cls(bus, chip_address, chip)
        return None

    def setup(self) -> None:
        if self.chip == self.HMC5883L:
            ident = self.read_block(0x0A, 3)
            if ident != b'H43':
                _logger.warning(f'HMC5883L returned unexpected identity {ident!r}')
            self.write_byte(0x00, 0x10)  # 1 sample average, 15Hz
            self.write_byte(0x01, 0x20)  # ±1.3Ga
            self.write_byte(0x02, 0x00)  # Continuous measurement
        elif self.chip == self.QMC5883:
            self.write_byte(0x0B, 0x01)  # SET/RESET period
            self.write_byte(0x20, 0x40)
            self.write_byte(0x21, 0x01)
            # OSR 64 | ±8G | 50Hz | continuous - as configured by DFRobot's begin()
            self.write_byte(0x09, 0xD5)
        elif self.chip == self.VCM5883L:
            self.write_byte(0x0B, 0x00)
            self.write_byte(0x0A, 0x4D)

    def read(self) -> tuple:
        """
        Returns:
            tuple: x, y & z raw magnetic field
        """
        if self.chip == self.HMC5883L:
            # Big endian, register order is X, Z, Y
            x, z, y = struct.unpack('>hhh', self.read_block(0x03, 6))
            return x, y, z
        x, y, z = struct.unpack('<hhh', self.read_block(0x00, 6))
        if self.chip == self.VCM5883L:
            # DFRobot inverts all VCM5883L axes to match the other chips
            return -x, -y, -z
        return x, y, z


class IMU(object):
    """
    A sensor class for the DFRobot Fermion 10 DOF IMU (SEN0140 V2) which fuses
    the ADXL345 accelerometer, ITG3205 gyroscope and HMC5883L/QMC5883/VCM5883L
    compass to work out what Arnold is doing.

    All values are in Arnold's body frame once the orientation map is applied:
    x points forward, y points left and z points up.

    - pitch is positive when the nose is up
    - roll is positive when leaning right (right side down)
    - heading is 0-360 degrees clockwise from north
    - turn rate is positive when turning left

    Args:
        bus (int, optional): I2C bus number
        address (dict, optional): I2C addresses of the accelerometer, gyroscope and
        magnetometer. A magnetometer address of None auto-detects the chip
        orientation (dict, optional): Per sensor axis map based on the physical
        position of the module on Arnold, eg. {'x': '-y', 'y': 'x', 'z': 'z'}
        bias (dict, optional): Calibration values as returned by `get_bias`
    """

    def __init__(
        self,
        bus: Optional[int] = None,
        address: Optional[dict] = None,
        orientation: Optional[dict] = None,
        bias: Optional[dict] = None,
    ) -> None:
        self.config = config.SENSOR['imu']

        # Module config
        self.bus_number = bus if bus is not None else self.config['bus']
        self.address = {**self.config['address'], **(address or {})}
        self.orientation = orientation or self.config['orientation']
        self.filter = self.config['filter']
        self.thresholds = self.config['thresholds']
        self.declination = self.config['declination']

        # Setup logging
        self._logger = _logger

        # Setup sensors
        self._bus_lock = threading.Lock()
        self.bus = SMBus(self.bus_number)

        self.accelerometer = ADXL345(
            self.bus, _to_address(self.address['accelerometer'])
        )
        self.accelerometer.setup()

        self.gyroscope = ITG3205(self.bus, _to_address(self.address['gyroscope']))
        self.gyroscope.setup()

        self.magnetometer = Compass.detect(
            self.bus, _to_address(self.address['magnetometer'])
        )
        if self.magnetometer:
            self._logger.info(
                f'Found {self.magnetometer.chip} compass at '
                f'{self.magnetometer.address:#04x}'
            )
            self.magnetometer.setup()
        else:
            self._logger.warning(
                'No compass found, heading will be relative to the start position.'
            )

        # Set the bias from the saved bias config from initial calibration
        bias = bias or self.config['bias']
        self.accelerometer_bias = list(bias['accelerometer'])
        self.gyroscope_bias = list(bias['gyroscope'])
        self.magnetometer_hard_iron = list(bias['magnetometer']['hard_iron'])
        self.magnetometer_soft_iron = [
            scale or 1.0 for scale in bias['magnetometer']['soft_iron']
        ]

        # The gyro bias drifts with temperature so re-zero it on startup like
        # FreeSixIMU does. This only works if Arnold is standing still.
        if self.config['calibrate_gyroscope_on_start']:
            try:
                self.calibrate_gyroscope()
            except ValueError as error:
                self._logger.warning(f'{error} Using the saved gyroscope bias.')

        # Sensor fusion state
        self._lock = threading.Lock()
        self._running = threading.Event()
        self._thread = None
        self.reset()

    def __enter__(self) -> 'IMU':
        self.start()
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def _map_orientation(self, data: tuple, sensor: str) -> dict:
        """
        Map x, y & z to Arnold's body frame based on the physical orientation of
        the module. A leading `-` in the map inverts the axis.

        Args:
            data (tuple): The original x, y & z values
            sensor (str): accelerometer, gyroscope or magnetometer

        Returns:
            dict: Mapped axes dict
        """
        values = dict(zip(AXES, data))
        orientation = self.orientation.get(sensor, self.orientation)
        mapped = {}
        for axis in AXES:
            source = orientation.get(axis, axis)
            sign = -1 if source.startswith('-') else 1
            mapped[axis] = sign * values[source.lstrip('+-')]
        return mapped

    def _read_accelerometer(self, calibrated: bool = True) -> dict:
        with self._bus_lock:
            data = self._map_orientation(self.accelerometer.read(), 'accelerometer')
        if calibrated:
            for axis, bias in zip(AXES, self.accelerometer_bias):
                data[axis] -= bias
        return data

    def _read_gyroscope(self, calibrated: bool = True) -> dict:
        with self._bus_lock:
            data = self._map_orientation(self.gyroscope.read(), 'gyroscope')
        if calibrated:
            for axis, bias in zip(AXES, self.gyroscope_bias):
                data[axis] -= bias
        return data

    def _read_magnetometer(self, calibrated: bool = True) -> Optional[dict]:
        if not self.magnetometer:
            return None
        with self._bus_lock:
            data = self._map_orientation(self.magnetometer.read(), 'magnetometer')
        if calibrated:
            for axis, offset, scale in zip(
                AXES, self.magnetometer_hard_iron, self.magnetometer_soft_iron
            ):
                data[axis] = (data[axis] - offset) * scale
        return data

    def _merge_samples(
        self,
        func: callable,
        sample_size: Optional[int] = None,
        delay: float = 0.01,
    ) -> dict:
        """
        Merge multiple samples from a sensor function into a single averaged
        sample.

        Args:
            func (callable): The sensor function to call
            sample_size (int | None): The number of samples to take. If None,
            uses the default from config.
            delay (float): Seconds to wait between samples

        Returns:
            dict: Merged x, y & z dict
        """
        samples = []
        sample_size = sample_size or self.config['sample_size']
        for _ in range(sample_size):
            samples.append(func())
            time.sleep(delay)

        return {
            axis: statistics.fmean(sample[axis] for sample in samples)
            for axis in AXES
        }

    def _sample_statistics(self, func: callable, sample_size: int) -> tuple:
        """
        Take samples from a sensor function and return their mean and the largest
        standard deviation across the axes.
        """
        samples = []
        for _ in range(sample_size):
            samples.append(func())
            time.sleep(0.01)
        mean = [statistics.fmean(sample[axis] for sample in samples) for axis in AXES]
        deviation = max(
            statistics.pstdev(sample[axis] for sample in samples) for axis in AXES
        )
        return mean, deviation

    def get_accelerometer_data(self, sample_size: Optional[int] = None) -> dict:
        """
        Get the current calibrated accelerometer data from the module.

        Args:
            sample_size (int | None): The number of samples to take. If None,
            uses the default from config.

        Returns:
            dict: x, y & z in g
        """
        data = self._merge_samples(self._read_accelerometer, sample_size)
        self._logger.debug(f'Accelerometer: {data}')
        return data

    def get_gyroscope_data(self, sample_size: Optional[int] = None) -> dict:
        """
        Get the current calibrated gyroscope data from the module.

        Args:
            sample_size (int | None): The number of samples to take. If None,
            uses the default from config.

        Returns:
            dict: x, y & z in deg/s
        """
        data = self._merge_samples(self._read_gyroscope, sample_size)
        self._logger.debug(f'Gyroscope: {data}')
        return data

    def get_magnetometer_data(self, sample_size: Optional[int] = None) -> Optional[dict]:
        """
        Get the current calibrated magnetometer data from the module.

        Args:
            sample_size (int | None): The number of samples to take. If None,
            uses the default from config.

        Returns:
            dict | None: x, y & z or None if there is no compass
        """
        if not self.magnetometer:
            return None
        data = self._merge_samples(self._read_magnetometer, sample_size)
        self._logger.debug(f'Magnetometer: {data}')
        return data

    def get_temperature(self) -> float:
        """
        Get the current temperature from the gyroscope.

        Returns:
            float: Temperature in celsius
        """
        with self._bus_lock:
            temperature = self.gyroscope.read_temperature()
        self._logger.debug(f'Temperature: {temperature}')
        return temperature

    def calibrate_gyroscope(self, sample_size: int = 128) -> list:
        """
        Zero the gyroscope. Arnold must be standing still.

        Returns:
            list: The gyroscope x, y & z bias in deg/s
        """
        bias, deviation = self._sample_statistics(
            lambda: self._read_gyroscope(calibrated=False), sample_size
        )
        if deviation > self.thresholds['stationary_rotation']:
            raise ValueError('Arnold moved during gyroscope calibration.')
        self.gyroscope_bias = bias
        return bias

    def calibrate_accelerometer(self, sample_size: int = 128) -> list:
        """
        Zero the accelerometer so that it reads 0g, 0g, 1g. Arnold must be standing
        still on a level surface. This also cancels out the module not being
        mounted perfectly level.

        Returns:
            list: The accelerometer x, y & z bias in g
        """
        mean, deviation = self._sample_statistics(
            lambda: self._read_accelerometer(calibrated=False), sample_size
        )
        if deviation > self.thresholds['stationary_acceleration']:
            raise ValueError('Arnold moved during accelerometer calibration.')
        self.accelerometer_bias = [mean[0], mean[1], mean[2] - 1.0]
        return self.accelerometer_bias

    def calibrate_magnetometer(self, duration: float = 30.0) -> dict:
        """
        Calculate the hard and soft iron calibration of the compass. Slowly turn
        Arnold through at least one full rotation (ideally tilting it a little as
        well) while this runs.

        Args:
            duration (float): Seconds to collect samples for

        Returns:
            dict: hard_iron and soft_iron x, y & z values
        """
        if not self.magnetometer:
            raise ValueError('No compass found to calibrate.')

        minimum = [math.inf] * 3
        maximum = [-math.inf] * 3
        end = time.monotonic() + duration
        while time.monotonic() < end:
            data = self._read_magnetometer(calibrated=False)
            for index, axis in enumerate(AXES):
                minimum[index] = min(minimum[index], data[axis])
                maximum[index] = max(maximum[index], data[axis])
            time.sleep(0.02)

        spans = [(high - low) / 2 for low, high in zip(minimum, maximum)]
        if min(spans) <= 0:
            raise ValueError('Compass readings did not change during calibration.')
        average_span = statistics.fmean(spans)

        self.magnetometer_hard_iron = [
            (high + low) / 2 for low, high in zip(minimum, maximum)
        ]
        self.magnetometer_soft_iron = [average_span / span for span in spans]
        return {
            'hard_iron': self.magnetometer_hard_iron,
            'soft_iron': self.magnetometer_soft_iron,
        }

    def get_bias(self) -> dict:
        """
        Get the current calibration values in the format used by the config.

        Returns:
            dict: accelerometer, gyroscope and magnetometer bias
        """
        return {
            'accelerometer': [round(value, 5) for value in self.accelerometer_bias],
            'gyroscope': [round(value, 5) for value in self.gyroscope_bias],
            'magnetometer': {
                'hard_iron': [round(value, 2) for value in self.magnetometer_hard_iron],
                'soft_iron': [round(value, 5) for value in self.magnetometer_soft_iron],
            }
        }

    def reset(self) -> None:
        """
        Reset the sensor fusion state. The next update re-initialises the
        attitude and heading from the accelerometer and compass.
        """
        window = max(1, int(self.filter['stationary_window'] * self.filter['rate']))
        with self._lock:
            self._last_update = None
            self._pitch = 0.0
            self._gravity_pitch = 0.0
            self._roll = 0.0
            self._heading = 0.0
            self._turn_rate = 0.0
            self._velocity = 0.0
            self._movement = 'stationary'
            self._stationary = True
            self._acceleration_window = collections.deque(maxlen=window)
            self._rotation_window = collections.deque(maxlen=window)
            self._pitch_window = collections.deque(maxlen=window)

    def _up_vector(self) -> tuple:
        """
        The direction of up in Arnold's body frame from the current pitch and roll.
        """
        pitch = math.radians(self._pitch)
        roll = math.radians(self._roll)
        return (
            math.sin(pitch),
            math.cos(pitch) * math.sin(roll),
            math.cos(pitch) * math.cos(roll),
        )

    def _compass_heading(self, magnetometer: dict) -> float:
        """
        Tilt compensated compass heading using the current pitch and roll.

        Returns:
            float: Heading in degrees clockwise from north
        """
        down = tuple(-value for value in self._up_vector())
        field = (magnetometer['x'], magnetometer['y'], magnetometer['z'])
        east = _cross(down, field)
        north = _cross(east, down)
        heading = math.degrees(math.atan2(east[0], north[0])) + self.declination
        return heading % 360.0

    def _update_attitude(self, accelerometer: dict, gyroscope: dict, dt: float) -> None:
        """
        Complementary filter for pitch and roll. The gyroscope is trusted over
        short periods and the accelerometer corrects the drift over longer periods.
        """
        x, y, z = accelerometer['x'], accelerometer['y'], accelerometer['z']
        accelerometer_pitch = math.degrees(math.atan2(x, math.hypot(y, z)))
        accelerometer_roll = math.degrees(math.atan2(y, z))

        if self._last_update is None:
            self._pitch = accelerometer_pitch
            self._roll = accelerometer_roll
            return

        # Positive rotation about y (left) is nose down, about x (forward) is
        # left side up, ie. leaning right
        pitch = self._pitch - gyroscope['y'] * dt
        roll = self._roll + gyroscope['x'] * dt

        # Ignore the accelerometer while it is measuring a lot more than gravity,
        # eg. bumps and hard acceleration
        magnitude = math.sqrt(x * x + y * y + z * z)
        if abs(magnitude - 1.0) < self.thresholds['attitude_acceleration']:
            # While driving the accelerometer can't tell speeding up from tilting
            # back, so lean on the gyroscope for longer
            time_constant = (
                self.filter['attitude_time_constant']
                if self._stationary
                else self.filter['attitude_moving_time_constant']
            )
            alpha = time_constant / (time_constant + dt)
            pitch = alpha * pitch + (1 - alpha) * accelerometer_pitch
            roll = alpha * roll + (1 - alpha) * accelerometer_roll

        self._pitch = pitch
        self._roll = roll

    def _update_heading(
        self, gyroscope: dict, magnetometer: Optional[dict], dt: float
    ) -> None:
        """
        Complementary filter for heading. The gyroscope gives a smooth heading
        while turning and the compass corrects the drift.
        """
        compass_heading = (
            self._compass_heading(magnetometer) if magnetometer else None
        )

        if self._last_update is None:
            self._heading = compass_heading or 0.0
            return

        # Turning left (positive z) reduces the compass heading
        heading = self._heading - gyroscope['z'] * dt
        if compass_heading is not None:
            time_constant = self.filter['heading_time_constant']
            alpha = time_constant / (time_constant + dt)
            heading += (1 - alpha) * _angle_difference(compass_heading, heading)
        self._heading = heading % 360.0

    def _update_motion(self, accelerometer: dict, gyroscope: dict, dt: float) -> None:
        """
        Work out if Arnold is moving forward or backward and if it is turning.

        An accelerometer can only measure changes in speed, so the forward speed is
        estimated by integrating the forward acceleration and is zeroed every time
        Arnold is detected as standing still.
        """
        # Turning from the smoothed yaw rate
        smoothing = self.filter['turn_rate_smoothing']
        self._turn_rate = smoothing * self._turn_rate + (1 - smoothing) * gyroscope['z']

        # Standing still is when the vibration and rotation are both very low
        self._acceleration_window.append(
            math.sqrt(sum(accelerometer[axis] ** 2 for axis in AXES))
        )
        self._rotation_window.append(
            math.sqrt(sum(gyroscope[axis] ** 2 for axis in AXES))
        )
        self._pitch_window.append(self._pitch)
        if len(self._acceleration_window) < self._acceleration_window.maxlen:
            self._gravity_pitch = self._pitch_window[0]
            return
        self._stationary = (
            statistics.pstdev(self._acceleration_window)
            < self.thresholds['stationary_acceleration']
            and max(self._rotation_window) < self.thresholds['stationary_rotation']
        )

        if self._stationary:
            # The start of the window is the pitch before any movement crept in
            self._gravity_pitch = self._pitch_window[0]
            self._velocity = 0.0
            self._movement = 'stationary'
            return

        # While driving the accelerometer can't tell speeding up from tilting, so
        # track the pitch used to remove gravity with the gyroscope alone, starting
        # from the accurate pitch measured while standing still
        self._gravity_pitch -= gyroscope['y'] * dt

        # Remove gravity to get the forward acceleration in m/s²
        forward_acceleration = (
            accelerometer['x'] - math.sin(math.radians(self._gravity_pitch))
        ) * GRAVITY
        if abs(forward_acceleration) < self.thresholds['acceleration_deadband']:
            forward_acceleration = 0.0

        self._velocity += forward_acceleration * dt
        self._velocity *= math.exp(-dt / self.filter['velocity_time_constant'])

        # Once a direction is detected keep it until Arnold stops or clearly
        # starts going the other way. This holds the direction at a steady speed
        # when there is no acceleration to measure, and stops braking from being
        # mistaken for reversing.
        if self._movement in ('forward', 'backward'):
            threshold = self.thresholds['reverse_velocity']
        else:
            threshold = self.thresholds['velocity']
        if self._velocity > threshold:
            self._movement = 'forward'
        elif self._velocity < -threshold:
            self._movement = 'backward'
        elif self._movement == 'stationary':
            self._movement = 'moving'

    def update(self) -> dict:
        """
        Read all the sensors and update the sensor fusion. This is called in the
        background after `start`, or can be called in your own loop at roughly
        the configured filter rate.

        Returns:
            dict: The current state, see `get_state`
        """
        accelerometer = self._read_accelerometer()
        gyroscope = self._read_gyroscope()
        magnetometer = self._read_magnetometer()
        now = time.monotonic()

        with self._lock:
            if self._last_update is None:
                dt = 0.0
            else:
                # Cap dt so a stalled loop doesn't integrate a huge jump
                dt = min(now - self._last_update, 0.1)
            self._update_attitude(accelerometer, gyroscope, dt)
            self._update_heading(gyroscope, magnetometer, dt)
            self._update_motion(accelerometer, gyroscope, dt)
            self._last_update = now
            return self._get_state()

    def _run(self) -> None:
        period = 1.0 / self.filter['rate']
        while self._running.is_set():
            started = time.monotonic()
            try:
                self.update()
            except OSError as error:
                self._logger.warning(f'IMU read failed: {error}')
            time.sleep(max(0.0, period - (time.monotonic() - started)))

    def start(self) -> None:
        """
        Start updating the sensor fusion in a background thread.
        """
        if self._running.is_set():
            return
        self.update()
        self._running.set()
        self._thread = threading.Thread(target=self._run, name='imu', daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """
        Stop the background update thread.
        """
        self._running.clear()
        if self._thread:
            self._thread.join()
            self._thread = None

    def close(self) -> None:
        """
        Stop updating and release the I2C bus.
        """
        self.stop()
        self.bus.close()

    def _ensure_running(self) -> None:
        if not self._running.is_set() and self._last_update is None:
            self.start()

    def _get_state(self) -> dict:
        threshold = self.thresholds['tilt']
        if self._pitch > threshold:
            pitch_direction = 'up'
        elif self._pitch < -threshold:
            pitch_direction = 'down'
        else:
            pitch_direction = 'level'

        if self._roll > threshold:
            roll_direction = 'right'
        elif self._roll < -threshold:
            roll_direction = 'left'
        else:
            roll_direction = 'level'

        # Whether Arnold is going uphill depends on the way it's driving
        if pitch_direction == 'level':
            slope = 'flat'
        elif self._movement == 'backward':
            slope = 'uphill' if pitch_direction == 'down' else 'downhill'
        else:
            slope = 'uphill' if pitch_direction == 'up' else 'downhill'

        if self._turn_rate > self.thresholds['turn_rate']:
            turning = 'left'
        elif self._turn_rate < -self.thresholds['turn_rate']:
            turning = 'right'
        else:
            turning = 'straight'

        return {
            'movement': self._movement,
            'velocity': self._velocity,
            'turning': turning,
            'turn_rate': self._turn_rate,
            'heading': self._heading,
            'cardinal': CARDINALS[int((self._heading + 22.5) // 45) % 8],
            'pitch': self._pitch,
            'roll': self._roll,
            'pitch_direction': pitch_direction,
            'roll_direction': roll_direction,
            'tilted': pitch_direction != 'level' or roll_direction != 'level',
            'slope': slope,
        }

    def get_state(self) -> dict:
        """
        Get everything the IMU knows about what Arnold is doing. Starts the
        background updates if they aren't running yet.

        Returns:
            dict:
                movement: forward, backward, moving (direction unknown) or stationary
                velocity: Rough forward speed estimate in m/s
                turning: left, right or straight
                turn_rate: deg/s, positive is left
                heading: 0-360 degrees clockwise from north
                cardinal: N, NE, E, SE, S, SW, W or NW
                pitch: degrees, positive is nose up
                roll: degrees, positive is leaning right
                pitch_direction: up, down or level
                roll_direction: left, right or level
                tilted: True if pitched or rolled past the tilt threshold
                slope: uphill, downhill or flat relative to the direction of travel
        """
        self._ensure_running()
        with self._lock:
            return self._get_state()

    def get_movement(self) -> str:
        """
        Returns:
            str: forward, backward, moving (direction unknown) or stationary
        """
        return self.get_state()['movement']

    def get_turning(self) -> str:
        """
        Returns:
            str: left, right or straight
        """
        return self.get_state()['turning']

    def get_heading(self) -> float:
        """
        Returns:
            float: 0-360 degrees clockwise from north
        """
        return self.get_state()['heading']

    def get_tilt(self) -> dict:
        """
        Returns:
            dict: pitch, roll, pitch_direction, roll_direction, tilted & slope
        """
        state = self.get_state()
        return {
            key: state[key]
            for key in (
                'pitch', 'roll', 'pitch_direction', 'roll_direction', 'tilted', 'slope'
            )
        }

    def get_attitude(self) -> dict:
        """
        Get the roll, pitch and heading from the sensor fusion.

        Returns:
            dict: Roll, pitch and heading in degrees
        """
        state = self.get_state()
        return {
            'roll': state['roll'],
            'pitch': state['pitch'],
            'heading': state['heading'],
        }
