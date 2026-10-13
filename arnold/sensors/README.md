# Sensors

Arnold is equipped with a number of sensors each of which is split into it's own module and main class.

## Microphone

### Setup

```bash
# Test that the USB mini microphone is working with a short sample
arecord --device=hw:1,0 --format S16_LE --rate 44000 -V mono -c1 voice.wav

# Test the file on another machine with sound if the speaker is not yet hooked up
scp pi@raspberrypi.local:~/voice.wav .
```

### Config

Update in `arnold/config.py`. Use command `arecord --list-devices` to find the correct config.

```python
SENSOR = {
    'microphone': {
        'card_number': 1,
        'device_index': 0,
        'sample_rate': 48000,
        'phrase_time_limit': 10,
        'energy_threshold': 700
    },
    ...
}
```

### Testing

```bash
arnold test microphone -c 1 -i 0
```

### Usage

```python
from arnold.sensors.microphone import Microphone

microphone = Microphone()
audio = microphone.listen()
text = microphone.recognise_command(audio)
print(text)
```

## Lidar

### Setup

Enable UART on the raspberrypi:

```bash
ssh pi@raspberrypi.local
sudo raspi-config
```

Select option 3: Interface Options then;
I6: Serial Port and enable it.
Finally reboot for the changes to take effect.

### Config

Update in `arnold/config.py`.

```python
SENSOR = {
    'lidar': {
        'serial_port': '/dev/ttyS0',
        'baudrate': 115200
    },
    ...
}
```

### Testing

```bash
arnold test lidar -p /dev/ttyS0 -b 115200 -c 5
```

### Usage

```python
from arnold.sensors.lidar import Lidar

lidar = Lidar()
distance = lidar.get_distance()
print(distance)
```

## IMU

DFRobot Fermion 10 DOF IMU V2 (SEN0140): ADXL345 accelerometer, ITG3205 gyroscope and a HMC5883L/QMC5883/VCM5883L compass. The drivers are a Python port of DFRobot's [FreeSixIMU](https://github.com/DFRobot/FreeSixIMU) and [DFRobot_QMC5883](https://github.com/DFRobot/DFRobot_QMC5883) libraries and only need `smbus2`.

### Setup

Enable I2C on the raspberrypi:

```bash
ssh pi@raspberrypi.local
sudo raspi-config
```

Select option 3: Interface Options then;
I5: I2C and enable it.
Finally reboot for the changes to take effect.

Check the module is found with `i2cdetect -y 1` (install with `sudo apt install i2c-tools`). You should see `53` (accelerometer), `68` (gyroscope), one of `1e`, `0d` or `0c` (compass) and `77` (barometer, unused).

### Config

Update in `arnold/config.py`.

```python
SENSOR = {
    'imu': {
        'bus': 1,
        'address': {
            'accelerometer': '53',
            'gyroscope': '68',
            'magnetometer': None  # auto-detect
        },
        'declination': 0.0,
        'orientation': {
            'accelerometer': {'x': 'x', 'y': 'y', 'z': 'z'},
            'gyroscope': {'x': 'x', 'y': 'y', 'z': 'z'},
            'magnetometer': {'x': 'x', 'y': 'y', 'z': 'z'}
        },
        ...
    },
    ...
}
```

#### Orientation

Everything is worked out in Arnold's body frame: **x forward, y left, z up**. Map each sensor's axes onto that frame, prefixing with `-` to invert an axis. Run `arnold test imu --raw` and check:

| Action                         | Expected                               |
| ------------------------------ | -------------------------------------- |
| Sitting flat                   | accelerometer z ≈ +1, x ≈ 0, y ≈ 0     |
| Nose lifted up                 | accelerometer x goes positive          |
| Left side lifted up            | accelerometer y goes positive          |
| Turned left (anti-clockwise)   | gyroscope z goes positive              |
| Nose lifted up quickly         | gyroscope y goes negative              |
| Left side lifted up quickly    | gyroscope x goes positive              |
| Level, facing magnetic north   | magnetometer x at its max, y ≈ 0       |
| Level, facing magnetic east    | magnetometer y at its max, x ≈ 0       |

Set the orientation before calibrating as the calibration is saved in the body frame.

#### Calibration

```bash
arnold calibrate imu
```

Save the output to the `ARNOLD_SENSOR_IMU_BIAS` env var, and set `ARNOLD_SENSOR_IMU_DECLINATION` for true north. The gyroscope is re-zeroed every time the IMU starts, so keep Arnold still for a second on startup.

### Testing

```bash
arnold test imu
arnold test imu --raw
```

### Usage

```python
from arnold.sensors.imu import IMU

imu = IMU()
imu.start()  # Runs the sensor fusion in a background thread

state = imu.get_state()
print('Movement:', state['movement'])  # forward, backward, moving or stationary
print('Turning:', state['turning'])  # left, right or straight
print('Heading:', state['heading'], state['cardinal'])  # 0-360 clockwise from north
print('Pitch:', state['pitch'], state['pitch_direction'])  # up, down or level
print('Roll:', state['roll'], state['roll_direction'])  # left, right or level
print('Slope:', state['slope'])  # uphill, downhill or flat

imu.close()
```

Forward/backward detection integrates the accelerometer, so it is an estimate: it picks up starting off, and holds the direction until Arnold stops. The drivetrain command should be treated as the source of truth with the IMU as confirmation.

## Camera

### Setup

Mounting and enabling the camera: https://raspberry-valley.azurewebsites.net/Mount-PiCamera/

### Config

```python
SENSOR = {
    'camera': {
        'camera_number': 0,
        'image': {
            'file_path': os.path.join(ROOT_DIR, 'image.jpg'),
            'height': 480,
            'width': 640,
        },
        'video': {
            'duration': 10.0,
            'file_path': os.path.join(ROOT_DIR, 'video.avi'),
            'height': 480,
            'width': 640,
        }
    },
    ...
}
```

### Testing

```bash
arnold test camera -f test.jpg
```

### Usage

```python
from arnold.sensors.camera import Camera

camera = Camera()
camera.capture_image()
camera.capture_video()
camera.stream_video()
camera.recognise_image()
```
