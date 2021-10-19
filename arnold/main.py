import random
import time
from typing import Optional

from arnold.motion import drivetrain
from arnold.sensors import lidar


class Arnold(object):
    """The main class which runs Arnold in different modes. By default manual
    mode is selected, which is controlled via the app and api.

    Args:
        mode (str, optional): The mode to run Arnold in. Options are `autonomous`,
            `voicecommand`, and `manual`
    """

    def __init__(self, mode: Optional[str] = None) -> None:
        self.mode = mode or 'manual'

        self.lidar = lidar.Lidar()
        self.drivetrain = drivetrain.DriveTrain()

    def _run_autonomous(self):

        # Scan enviroment for possible path
        self.drivetrain.forward()
        while True:
            distance = self.lidar.get_distance()
            time.sleep(0.1)
            if distance < 30:
                self.drivetrain.turn(
                    random.choices['right', 'left'],
                    duration=2
                )
                break

        self._run_autonomous()

    def _run_manual(self):
        pass

    def _run_voicecommand(self):
        pass

    def run(self):
        pass
