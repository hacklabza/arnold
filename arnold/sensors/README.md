# Sensors

Arnold is equiped with a number of sensors each of which is split into it's own module and main class.

## Microphone

### Setup

```bash
# Test that the USB mini microphone is working with a short sample
arecord --device=hw:1,0 --format S16_LE --rate 44000 -V mono -c1 voice.wav

# Test the file on another machine with sound if the speaker is not yet hooked up
scp pi@192.168.1.115:~/voice.wav .
```

### Config

Update in `arnold/config.py`. Use command `arecord --list-devices` to find the correct config.

```python
SENSOR_CONFIG = {
    'microphone': {
        'card_number': 1,
        'device_index': 0,
        'sample_rate': 48000,
        'phrase_time_limit': 10,
        'energy_threshold': 700
    }
}
```

## Lidar

## Camera

## GPS
