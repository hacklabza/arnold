import time

from arnold.motion import drivetrain


class TestDrivetrain:

    def setup_method(self, method):
        self.drive = drivetrain.DriveTrain(enable_pwm=False)

    def teardown_method(self, method):
        self.drive.stop()
        self.drive.release()

    def test_drivetrain_delay(self):

        # Ensure that the drive is activate for the correct duration
        self.drive.forward(0.5)
        assert self.drive.delay.is_active()
        time.sleep(1)
        assert not self.drive.delay.is_active()

        # Ensure that the drive switches even when already performing an maneuver
        self.drive.forward(1)
        time.sleep(0.2)
        self.drive.back(1)
        time.sleep(0.2)
        assert self.drive.status['right']['direction'] == 'back'
        assert self.drive.delay.is_active()
        time.sleep(1)
        assert not self.drive.delay.is_active()


    def test_drivetrain_forward(self):

        self.drive.forward(15)

        # Allow for a short sleep before testing if the motors are still activated
        # in a thread
        time.sleep(0.2)

        assert self.drive.status['right']['direction'] == 'forward'
        assert self.drive.status['right']['is_active']
        assert self.drive.status['left']['direction'] == 'forward'
        assert self.drive.status['left']['is_active']
        assert self.drive.delay.is_active()

    def test_drivetrain_back(self):

        self.drive.back(15)

        # Allow for a short sleep before testing if the motors are still activated
        # in a thread
        time.sleep(0.2)

        assert self.drive.status['right']['direction'] == 'back'
        assert self.drive.status['right']['is_active']
        assert self.drive.status['left']['direction'] == 'back'
        assert self.drive.status['left']['is_active']
        assert self.drive.delay.is_active()

    def test_drivetrain_turn(self):

        self.drive.turn('right', 15)

        # Allow for a short sleep before testing if the motors are still activated
        # in a thread
        time.sleep(0.2)

        assert self.drive.status['right']['direction'] == 'back'
        assert self.drive.status['right']['is_active']
        assert self.drive.status['left']['direction'] == 'forward'
        assert self.drive.status['left']['is_active']
        assert self.drive.delay.is_active()

        self.drive.turn('left', 15)

        # Allow for a short sleep before testing if the motors are still activated
        # in a thread
        time.sleep(0.2)

        assert self.drive.status['right']['direction'] == 'forward'
        assert self.drive.status['right']['is_active']
        assert self.drive.status['left']['direction'] == 'back'
        assert self.drive.status['left']['is_active']
        assert self.drive.delay.is_active()

    def test_drivetrain_stop(self):

        self.drive.forward(3)

        # Allow for a short sleep before testing if the motors are still activated
        # in a thread
        time.sleep(0.2)

        self.drive.stop()

        # Allow for a short sleep before testing if stop has worked and the process
        # is terminated
        time.sleep(0.2)

        assert self.drive.status['right']['direction'] == 'stopped'
        assert not self.drive.status['right']['is_active']
        assert self.drive.status['left']['direction'] == 'stopped'
        assert not self.drive.status['left']['is_active']
        assert not self.drive.delay.is_active()

