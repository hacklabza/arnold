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

## Lidar

## Camera

## GPS
