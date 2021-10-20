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

    def _run_autonomous(self, is_active: bool = False) -> None:
        if not is_active:
            self.drivetrain.forward(duration=10)

        while True:
            distance = self.lidar.get_distance()
            if distance < 30:
                self.drivetrain.stop()
                self.drivetrain.turn(
                    random.choice(['right', 'left']),
                    duration=5
                )
                while True:
                    distance = self.lidar.get_distance()
                    if distance > 50:
                        self.drivetrain.stop()
                        time.sleep(0.5)
                        self._run_autonomous(is_active=False)
            else:
                self._run_autonomous(is_active=self.drivetrain.is_active)


    def _run_manual(self):
        pass

    def _run_voicecommand(self):
        pass

    def run(self):
        mode_map = {
            'autonomous': self._run_autonomous,
            'voicecommand': self._run_voicecommand,
            'manual': self._run_manual,
        }
        mode_map[self.mode]()
