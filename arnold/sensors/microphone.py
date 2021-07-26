import logging
import os
from typing import Optional

import speech_recognition

from arnold import config

ROOT_DIR = config.ROOT_DIR
CONFIG = config.SENSOR_CONFIG['microphone']

_logger = logging.getLogger(__name__)

class Microphone(object):
    """A sensor class which initialises the microphone component and add speech
    recognition and command parsing to Arnold.

    Kwargs:
        card_number (int, optional): The microphone device card number.
            Defaults to 1.
        device_index (int, optional): The microphone device index.
            Defaults to 0.
        sample_rate (int, optional): The microphone sample rate.
            Defaults to 48000.
        sample_rate (int, optional): The microphone sample rate.
            Defaults to 48000.
        phrase_time_limit (int, optional): How long to listen for a phrase.
            Defaults to 10 seconds.
        energy_threshold (int, optional): The microphones energy threshold.
            Defaults to 700.
        google_api_key_path (str, optional): The file path to the json api key.

    """
    def __init__(self, *args, **kwargs):

        # USB microphone adapter config
        self.card_number = kwargs.pop(
            'card_number', CONFIG.get('card_number', 1)
        )
        self.device_index = kwargs.pop(
            'device_index', CONFIG.get('device_index', 0)
        )
        self.sample_rate = kwargs.pop(
            'sample_rate', CONFIG.get('sample_rate', 48000)
        )

        # Setup logging
        self._logger = _logger

        # Speech recognition
        self.phrase_time_limit = kwargs.pop(
            'phrase_time_limit', CONFIG.get('phrase_time_limit', 10)
        )
        self.speech_recogniser = speech_recognition.Recognizer()
        self.speech_recogniser.energy_threshold = kwargs.pop(
            'energy_threshold', CONFIG.get('energy_threshold', 700)
        )

        # Google Cloud API integration
        try:
            self.google_api_key_path = kwargs.pop(
                'google_api_key_path',
                config.INTEGRATION_CONFIG['google_cloud']['key_path']
            )
        except KeyError:
            self.google_api_key = None

    def listen(self) -> speech_recognition.AudioData:
        """Records the voice command from the microphone and returns the audio
        bite.

        Returns:
            AudioData: an audio data object of the voice command recorded.
        """
        with speech_recognition.Microphone(sample_rate=self.sample_rate) as source:
            self.speech_recogniser.adjust_for_ambient_noise(source)
            self._logger.info('Ready to receive voice commands.')
            voice_command = self.speech_recogniser.listen(
                source, phrase_time_limit=self.phrase_time_limit
            )
            return voice_command

    def recognise_command(self, voice_command: speech_recognition.AudioData) -> Optional[str]:
        """Takes a voice command as input and calls the google voice to text
        service to determine the text command which can be parsed.

        Args:
            voice_command (speech_recognition.AudioData): Recorded voice command

        Returns:
            Optional[str]: the text command as processed by google speech
                recognision engine.
        """
        if self.google_api_key_path:
            google_cloud_credentials = ''
            with open(os.path.join(config.ROOT_DIR, self.google_api_key_path), 'r') as file:
                google_cloud_credentials = file.read()
            return self.speech_recogniser.recognize_google_cloud(
                voice_command,
                credentials_json=google_cloud_credentials,
                language="en-ZA"
            )
        else:
            self._logger.error(
                'Can\'t proceed. Google Cloud API key not found.'
            )

        return ''



