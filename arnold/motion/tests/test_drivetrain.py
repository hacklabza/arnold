from arnold.motion import motor

def test_drivetrain_go():
    drive = motor.Drive()
    drive.go('forward', 3)
    drive.go('back', 3)
    drive.go('left', 3)
    drive.go('right', 3)
