from arnold.motion.drive import Drive

def test_drive():
    drive = Drive()
    drive.go('forward', 3)
    drive.go('back', 3)
    drive.go('left', 3)
    drive.go('right', 3)
