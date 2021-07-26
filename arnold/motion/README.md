# Motion

Arnold is equiped with two motors controlled by an L298M over PWM.

## Drive

### Config

Update in `arnold/config.py`. Pins are config left and than right.

```python
MOTION_CONFIG = {
    'gpio': {
        'left': {
            'pins': [24, 23]
        },
        'right': {
            'pins': [22, 17]
        }
    },
    'pause_duration': 0.2
}
```

### Usage

```python
from arnold.motion import Drive

drive = Drive()

# Drive arnold forward for 2 seconds, left for 1, right for 1 and than back for 2.
drive.go('forward', 2)
drive.go('left', 1)
drive.go('right', 1)
drive.go('back', 1)

# Get the status of the left and right motors
drive.status
```
