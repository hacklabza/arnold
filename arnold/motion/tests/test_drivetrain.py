import time

from gpiozero import Motor

from arnold.motion import drivetrain


def test_drivetrain():
    drive = drivetrain.DriveTrain(enable_pwm=False)

    # Ensure that the drive is activate for the correct duration
    drive.forward(1)
    assert drive.delay.is_active()
    time.sleep(1.5)
    assert not drive.delay.is_active()

    drive.forward(15)

    # Allow for a short sleep before testing if the motors are still activated
    # in a thread
    time.sleep(2)

    assert drive.status['right']
    assert drive.status['left']
    assert drive.delay.is_active()

    drive.stop()

    # Allow for a short sleep before testing if stop has worked and the process
    # is terminated
    time.sleep(0.5)

    assert not drive.status['right']
    assert not drive.status['left']
    assert not drive.delay.is_active()

    # drive.go('forward', 1)
    # drive.go('back', 1)
    # drive.go('left', 1)
    # drive.go('right', 1)
