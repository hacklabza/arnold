from arnold import config, motion

from gpiozero import Motor


class Arnold(object):
    def __init__(self, gpio_map, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gpio_map = gpio_map

    def motion(self, direction, speed=1, duration=1):
        left_motor_pins = self.gpio_map["motion"]["left"]["pins"]
        right_motor_pins = self.gpio_map["motion"]["right"]["pins"]
        arnold_motion = motion.Motion(
            left_motor=Motor(*left_motor_pins),
            right_motor=Motor(*right_motor_pins)
        )
        command = getattr(arnold_motion, direction)
        command(speed, duration)


def run():
    arnold = Arnold(gpio_map=config.GPIO_MAP)
    arnold.motion("forward", duration=5)
    arnold.motion("right", duration=2)
    arnold.motion("left", duration=2)
    arnold.motion("backward", duration=5)

run()
