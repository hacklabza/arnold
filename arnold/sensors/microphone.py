import logging

import speech_recognition

from arnold.sensors import _config

CONFIG = _config['microphone']

_logger = logging.getLogger(__name__)

class Microphone(object):
    """
    A sensor class which initialises the microphone component and add speech
    recognition and command parsing to Arnold.
    """
    def __init__(self, *args, **kwargs):

        # USB microphone adapter config
        self.card_number = kwargs.pop('card_number', CONFIG.get('card_number', 1))
        self.device_number = kwargs.pop('device_number', CONFIG.get('device_number', 0))

        # Setup logging
        self._logger = _logger

        # Speech recognition
        self.speech = speech_recognition.speech()
        try:
            self.google_api_key = CONFIG['google_cloud']['api_key']
        except KeyError:
            self.google_api_key = None

    def listen(self):
        """
        Records the voice command from the microphone and returns the audio bite.
        """
        with speech_recognition.Microphone() as source:
            voice_command = self.speech.listen(source)
        return voice_command

    def recognise_command(self, voice_command):
        """
        Takes a voice command as input and calls the google voice to text service to
        determine the text command which can be parsed.
        """
        if self.google_api_key:
            return self.speech.recognize_google_cloud(
                voice_command, self.google_api_key
            )
        else:
            self._logger.error('Can\'t proceed. Google Cloud API key not found.')
