import logging
from typing import Optional

from arnold import api
from arnold.lookup import openai, weather
from arnold.motion import drivetrain
from arnold.output import speaker
from arnold.sensors import camera, imu, lidar, microphone


_logger = logging.getLogger(__name__)


class Arnold(object):
    """
    The main class which runs Arnold in different modes. By default manual
    mode is selected, which is controlled via the app and api.

    Args:
        mode (str, optional): The mode to run Arnold in. Options are `autonomous`,
        `voicecommand`, and `manual`
    """

    def __init__(self, mode: Optional[str] = None) -> None:
        self.set_mode(mode or 'manual')

        # Setup logging
        self._logger = _logger

    def _setup_classes(self, classes: list = None) -> None:
        """
        Setup the required classes.
        """
        class_map = {
            'camera': camera.Camera,
            'drivetrain': drivetrain.DriveTrain,
            'imu': imu.IMU,
            'lidar': lidar.Lidar,
            'microphone': microphone.Microphone,
            'openai': openai.OpenAI,
            'speaker': speaker.Speaker,
            'weather': weather.Weather,
        }
        classes = classes or []
        for required_class in classes:
            if required_class not in class_map:
                raise ValueError(f'{required_class} is not a valid class.')
            if not hasattr(self, required_class):
                setattr(self, required_class, class_map[required_class]())

    def set_mode(self, mode: str) -> None:
        """
        Set the mode to run Arnold in.

        Args:
            mode (str): The mode to run Arnold in. Options are `autonomous`,
            `voicecommand`, and `manual`
        """
        valid_modes = ['autonomous', 'voicecommand', 'manual']
        if mode not in valid_modes:
            raise ValueError(f'{mode} is not a valid mode: {valid_modes}.')
        self.mode = mode

    def _run_autonomous(self) -> None:
        """
        Run Arnold in autonomous mode.
        """
        self._setup_classes(['drivetrain', 'lidar'])
        self.drivetrain.autonomous(arnold=self)

    def _run_manual(self) -> None:
        """
        Run Arnold in manual mode over the API.
        """
        self._setup_classes(
            ['camera', 'drivetrain', 'speaker']
        )
        api.runserver(arnold=self)

    def _run_voicecommand(self) -> None:
        """
        Run Arnold in voice command mode.
        """
        self._setup_classes(
            ['camera', 'drivetrain', 'microphone', 'openai', 'speaker', 'weather']
        )
        self.microphone.voice_command(arnold=self)

    def run(self) -> None:
        """
        Run Arnold in a selected mode. Maps the mode to a 'private' method.
        """
        mode_map = {
            'autonomous': self._run_autonomous,
            'voicecommand': self._run_voicecommand,
            'manual': self._run_manual,
        }
        mode_map[self.mode]()
