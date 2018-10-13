from signal import pause

from gpiozero import Motor


motor_left = Motor(23, 24)
motor_right = Motor(17, 22)
motor_left.forward()
motor_right.forward()

pause()
