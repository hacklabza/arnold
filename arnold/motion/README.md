# Motion

Arnold is equiped with two motors controlled by an L298M over PWM.

## Drive

### Config

Update in `arnold/config.py`. Pins are config left and than right.

```python
MOTION_CONFIG = {
    'drivetrain': {
        'gpio': {
            'left': {
                'pins': [24, 23]
            },
            'right': {
                'pins': [22, 17]
            }
        },
        'pause_duration': 0.2
    },
    ...
}
```

### Usage

```python
from arnold.motion import drivetrain

drive = drivetrain.DriveTrain()

# Drive arnold forward for 2 seconds, left for 1, right for 1 and than back for 2.
drive.go('forward', 2)
drive.go('left', 1)
drive.go('right', 1)
drive.go('back', 1)

# Some shortcuts have been provided which are used internally by voice command
drive.forward(2)
drive.back(2)
drive.turn('left', 2)
drive.turn('right', 2)

# Get the status of the left and right motors
drive.status
```
