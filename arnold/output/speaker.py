import logging

import pyttsx3


_logger = logging.getLogger(__name__)


class Speaker(object):
    def __init__(self):
        self.speech_engine = pyttsx3.init()

        # Setup logging
        self._logger = _logger

        # Log interactions
        self.speech_engine.connect('started-utterance', self._on_start)
        self.speech_engine.connect('finished-utterance', self._on_finish)

    def _on_start(self, name: str) -> None:
        _logger.info(f'Starting speech output')

    def _on_finish(self, name: str, completed: bool) -> None:
        if completed:
            _logger.info(f'Completed speech output')
        else:
            _logger.info(f'Phase not completed')

    def say(self, text: str) -> None:
        self.speech_engine.say(text)
        self.speech_engine.runAndWait()
