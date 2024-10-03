import logging
import random
from typing import Optional

from speech_recognition import UnknownValueError

from arnold import api, utils
from arnold.lookup import openai
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
        self.drivetrain = drivetrain.DriveTrain()
        self.imu = imu.IMU()
        self.lidar = lidar.Lidar()
        self.microphone = microphone.Microphone()
        self.openai = openai.OpenAI()
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

        # Capture the audio and parse the command or fall back to an OpenAI
        # response
        while True:
            audio = self.microphone.listen()
            try:
                command = self.microphone.recognise_command(audio)
            except UnknownValueError:
                continue

            command = self.microphone.recognise_command(audio)
            self._logger.info(f'Voice command recieved: "{command}"')

            # Break if the command contains the word 'exit'
            if 'exit' in command:
                break

            command_parser = utils.CommandParser(command)
            try:
                command_result = command_parser.parse()
                if command_result is not None:
                    self.speaker.say(command_result)
            except NotImplementedError:
                response = self.openai.prompt(command)
                self.speaker.say(response.message)

    def run(self):
        """Run Arnold in a selected mode. Maps the mode to a 'private' method.
        """
        mode_map = {
            'autonomous': self._run_autonomous,
            'voicecommand': self._run_voicecommand,
            'manual': self._run_manual,
        }
        mode_map[self.mode]()
