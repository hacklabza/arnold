import logging
import os
from typing import Optional

import speech_recognition

from arnold import config


_logger = logging.getLogger(__name__)


class Microphone(object):
    """A sensor class which initialises the microphone component and add speech
    recognition and command parsing to Arnold.

    Args:
        card_number (int, optional): The microphone device card number.
        device_index (int, optional): The microphone device index.
        sample_rate (int, optional): The microphone sample rate.
        phrase_time_limit (int, optional): How long to listen for a phrase.
        energy_threshold (int, optional): The microphones energy threshold.
        google_api_key_path (str, optional): The file path to the json api key.

    """
    def __init__(
        self,
        card_number: Optional[int] = None,
        device_index: Optional[int] = None,
        sample_rate: Optional[int] = None,
        phrase_time_limit: Optional[int] = None,
        energy_threshold: Optional[int] = None,
        google_api_key_path: Optional[int] = None

    ) -> None:
        self.config = config.SENSOR['microphone']

        # USB microphone adapter config
        self.card_number = self.config['card_number'] if card_number is None else card_number
        self.device_index = self.config['device_index'] if device_index is None else device_index
        self.sample_rate = sample_rate or self.config['sample_rate']

        # Setup logging
        self._logger = _logger

        # Speech recognition
        self.phrase_time_limit = phrase_time_limit or self.config['phrase_time_limit']
        self.speech_recogniser = speech_recognition.Recognizer()
        self.speech_recogniser.energy_threshold = (
            energy_threshold or self.config['energy_threshold']
        )

        # Google Cloud API integration
        try:
            self.google_api_key_path = (
                google_api_key_path or config.INTEGRATION['googlecloud']['key_path']
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
        """Takes a voice command audio bite as input and calls the google voice
        to text service to determine the text command which can be parsed.

        Args:
            voice_command (speech_recognition.AudioData): Recorded voice command

        Returns:
            Optional[str]: the text command as processed by google speech
                recognision engine.
        """
        if self.google_api_key_path:
            return self.speech_recogniser.recognize_google_cloud(
                voice_command,
                credentials_json=os.path.join(config.ROOT_DIR, self.google_api_key_path),
                language='en-ZA'
            )
        else:
            self._logger.error(
                'Can\'t proceed. Google Cloud API key not found.'
            )
