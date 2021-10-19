from typing import Optional

from arnold.motion.drivetrain import DriveTrain
from arnold.sensors.lidar import Lidar


class Arnold(object):
    """The main class which runs Arnold in different modes. By default manual
    mode is selected, which is controlled via the app and api.

    Args:
        mode (str, optional): The mode to run Arnold in. Options are `autonomous`,
            `voicecommand`, and `manual`
    """

    def __init__(self, mode: Optional[str] = None) -> None:
        self.mode = mode or 'manual'

    def _run_autonomous(self):
        lidar = Lidar()
        drivetrain = DriveTrain()

        # Scan enviroment for possible path
        drivetrain.turn('right', 5)
        point_cloud = []
        while True:
            point_cloud.append(lidar.get_distance())

    def _run_manual(self):
        pass

    def _run_voicecommand(self):
        pass

    def run(self):
        pass
