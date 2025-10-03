from __future__ import annotations

import logging
import io
from typing import Optional

import sounddevice  # noqa: F401
import speech_recognition

from arnold import config, utils
from arnold.lookup import openai


_logger = logging.getLogger(__name__)


class Microphone(object):
    """
    A sensor class which initialises the microphone component and add speech
    recognition and command parsing to Arnold.

    Args:
        card_number (int, optional): The microphone device card number.
        device_index (int, optional): The microphone device index.
        sample_rate (int, optional): The microphone sample rate.
        phrase_time_limit (int, optional): How long to listen for a phrase.
        energy_threshold (int, optional): The microphones energy threshold.

    """
    def __init__(
        self,
        card_number: Optional[int] = None,
        device_index: Optional[int] = None,
        sample_rate: Optional[int] = None,
        phrase_time_limit: Optional[int] = None,
        energy_threshold: Optional[int] = None,

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

        # Setup OpenAI client for transcription
        self.openai = openai.OpenAI()


    def listen(self) -> speech_recognition.AudioData:
        """
        Records the voice command from the microphone and returns the audio
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

    def recognise_command(self, voice_command: speech_recognition.AudioData) -> str:
        """
        Takes a voice command audio bite as input and calls the openai audio
        transcribe service to determine the text command which can be parsed.

        Args:
            voice_command (speech_recognition.AudioData): Recorded voice command

        Returns:
            str: the text command as processed by openai transcribe service.
        """
        with io.BytesIO() as audio_file:
            audio_file.write(voice_command.get_wav_data())
            audio_file.seek(0)
            audio_file.name = "audio.wav"
            return self.openai.transcribe(audio_file)

    def voice_command(self, arnold: 'Arnold') -> None:
        """
        Listens for a voice command and returns the text command.

        Args:
            arnold (Arnold): An Arnold instance

        Raises:
            UnknownValueError: Raised if the speech recognition could not
            understand the audio.
        """
        while True:
            audio = self.listen()
            try:
                command = self.recognise_command(audio)
            except speech_recognition.UnknownValueError:
                continue

            # Sanitise the command input
            command = utils.sanitise_input(command)

            self._logger.info(f'Voice command received: "{command}"')

            # Break if the command contains the exit or quit tokens
            termination_tokens = ['quit', 'exit', 'goodbye']
            if set(termination_tokens).intersection(set(command.split())):
                arnold.speaker.say("Goodbye!")
                break

            # Parse the command and call the relevant method
            command_parser = utils.CommandParser(arnold=arnold, command=command)
            try:
                command_result = command_parser.parse()
                if command_result is not None:
                    arnold.speaker.say(command_result)
            except NotImplementedError:
                if command:
                    response = arnold.openai.prompt(command)
                    arnold.speaker.say(response.message)
