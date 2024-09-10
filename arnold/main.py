import logging
import random
from typing import Optional

from arnold import api, utils
from arnold.motion import drivetrain
from arnold.output import speaker
from arnold.sensors import imu, lidar, microphone


_logger = logging.getLogger(__name__)


class Arnold(object):
    """The main class which runs Arnold in different modes. By default manual
    mode is selected, which is controlled via the app and api.

    Args:
        mode (str, optional): The mode to run Arnold in. Options are `autonomous`,
            `voicecommand`, and `manual`
    """

    def __init__(self, mode: Optional[str] = None) -> None:
        self.mode = mode or 'manual'

        # Setup required classes
        self.imu = imu.IMU()
        self.lidar = lidar.Lidar()
        self.drivetrain = drivetrain.DriveTrain()
        self.microphone = microphone.Microphone()
        self.speaker = speaker.Speaker()

        # Setup logging
        self._logger = _logger

    def _run_autonomous(self) -> None:
        """Run Arnold in autonomous mode.
        """
        try:
            while True:
                distance = self.lidar.get_mean_distance(10)
                if distance < 40:
                    self.drivetrain.turn(
                        random.choice(['right', 'left']),
                        duration=10
                    )
                    while True:
                        distance = self.lidar.get_mean_distance(10)
                        if distance > 80:
                            self.drivetrain.stop()
                            break

                if not self.drivetrain.is_active:
                    self.drivetrain.forward(duration=60)

        except KeyboardInterrupt:
            self.drivetrain.stop()

    def _run_manual(self):
        """Run Arnold in manual mode over the API.
        """
        api.runserver()

    def _run_voicecommand(self):
        """Run Arnold in voice command mode.
        """

        # Release the drivertrain
        self.drivetrain.release()

        # Capture the audio and parse the command
        while True:
            audio = self.microphone.listen()
            command = self.microphone.recognise_command(audio)
            log_message = f'Voice command recieved: "{command}"'
            self._logger.info(log_message)
            self.speaker.say(log_message)
            command_parser = utils.CommandParser(command)
            command_parser.parse()

    def run(self):
        """Run Arnold in a selected mode. Maps the mode to a 'private' method.
        """
        mode_map = {
            'autonomous': self._run_autonomous,
            'voicecommand': self._run_voicecommand,
            'manual': self._run_manual,
        }
        mode_map[self.mode]()
