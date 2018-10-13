from time import sleep


class Motion(object):
    def __init__(self, left_motor, right_motor):
        self.left_motor = left_motor
        self.right_motor = right_motor

    def stop(self):
        self.left_motor.stop()
        self.right_motor.stop()
        sleep(0.2)

    def forward(self, speed=1, duration=1):
        self.stop()
        self.left_motor.forward(speed=speed)
        self.right_motor.forward(speed=speed)
        sleep(duration)

    def backward(self, speed=1, duration=1):
        self.stop()
        self.left_motor.backward(speed=speed)
        self.right_motor.backward(speed=speed)
        sleep(duration)

    def right(self, speed=1, duration=1):
        self.stop()
        self.left_motor.backward(speed=speed)
        self.right_motor.forward(speed=speed)
        sleep(duration)

    def left(self, speed=1, duration=1):
        self.stop()
        self.left_motor.forward(speed=speed)
        self.right_motor.backward(speed=speed)
        sleep(duration)
