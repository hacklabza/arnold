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
text = microphone.microphone.recognise_command(audio)
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

## Accelerometer

### Setup

Enable I2C on the raspberrypi:

```bash
ssh pi@raspberrypi.local
sudo raspi-config
```

Select option 3: Interface Options then;
I5: I2C and enable it.
Finally reboot for the changes to take effect.

### Config

Update in `arnold/config.py`. Use comand `i2cdetect -y 1` to get the coorect address. You may need to install first with `sudo apt install i2c-tools`

```python
SENSOR = {
    'accelerometer': {
        'address': '68',
        'orientation': {
            'x': 'x',
            'y': 'z',
            'z': 'y'
        }
    },
    ...
}
```

### Testing

```bash
arnold test accelerometer -a 53
```

### Usage

```python
from arnold.sensors.accelerometer import Accelerometer

accelerometer = Accelerometer()
axes = accelerometer.get_axes()
print(axes)
```

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
            'frame_rate': 15,
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
```
