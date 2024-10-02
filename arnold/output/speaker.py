import logging
from typing import Optional

import pyttsx3

from arnold import config


_logger = logging.getLogger(__name__)


class Speaker(object):
    """
    Provides a speaker interface for generating speech output using the pyttsx3 library.
    The `Speaker` class is responsible for initializing and configuring the speech
    engine, as well as providing methods for generating speech output via the speaker
    device.

    Args:
        rate (int, optional): The speech rate in words per minute. Defaults to the
        configured rate in the configuration file.
        volume (float, optional): The speech volume as a percentage. Defaults to the
        configured volume in the configuration file.
    """
    def __init__(
        self,
        rate: Optional[int] = None,
        volume: Optional[float] = None
    ) -> None:
        self.config = config.INTEGRATION['speaker']
        self.speech_engine = pyttsx3.init()

        # Setup logging
        self._logger = _logger

        # Log interactions
        self.speech_engine.connect('started-utterance', self._on_start)
        self.speech_engine.connect('finished-utterance', self._on_finish)

        # Setup speech engine parameters
        self.rate = rate or self.config['rate']
        self.volume = volume or self.config['volume']
        self.speech_engine.setProperty('rate', self.rate)
        self.speech_engine.setProperty('volume', self.volume)

    def _on_start(self, name: str) -> None:
        """
        Called when the speech output has started.

        Args:
            name (str): The name of the speech output.
        """
        _logger.info(f'Starting speech output')

    def _on_finish(self, name: str, completed: bool) -> None:
        """
        Called when the speech output has finished.

        Args:
            name (str): The name of the speech output.
            completed (bool): Whether the speech output was completed successfully.
        """
        if completed:
            _logger.info(f'Completed speech output')
        else:
            _logger.info(f'Phase not completed')

    def say(self, text: str) -> None:
        """
        Speaks the provided text using the configured speech engine and speaker output
        device.

        Args:
            text (str): The text to be spoken.
        """
        self.speech_engine.say(text)
        self.speech_engine.runAndWait()
