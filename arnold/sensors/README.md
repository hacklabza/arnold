# Sensors

## Microphone

```bash
# Test that the USB mini microphone is working with a short sample
arecord --device=hw:1,0 --format S16_LE --rate 44100 -V mono -c1 voice.wav

# Test the file on another machine with sound if the speaker is not yet hooked up
scp pi@192.168.1.115:~/voice.wav .
```

## Lidar

## Camera

## GPS


