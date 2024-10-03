import logging
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI as OpenAIClient
import requests

from arnold import config

_logger = logging.getLogger(__name__)


@dataclass
class Completion:
    """
    Represents the result of a OpenAI text completion request, including the generated
    message and the total number of tokens used.

    Args:
        message (str): The generated text message.
        total_tokens (int): The total number of tokens used in the completion.

    Returns:
        str: A string representation of the completion result.
    """

    message: str
    total_tokens: int

    def __str__(self):
        return f'{self.message} ({self.total_tokens})'


class OpenAI(object):
    """
    Provides a OpenAI client interface for interacting with the OpenAI API. The
    `OpenAI` class encapsulates the configuration and client setup for making requests
    to the OpenAI API to generate text completions using the OpenAI language model.
    """

    def __init__(self) -> None:
        self.config = config.INTEGRATION['openai']
        self.client = OpenAIClient(
            api_key=self.config['api_key'],
            organization=self.config['organization_id'],
            project=self.config['project_id'],
        )

        # Setup logging
        self._logger = _logger

    def prompt(
        self,
        message: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Completion:
        """
        Generates a text completion using the OpenAI language model.

        Args:
            message (str): The input message to be used for generating the completion.

        Returns:
            Completion: A dataclass containing the generated completion message and the
            total number of tokens used.

        Raises:
            HTTPError: If there is an error during the API request.
        """

        # Set default values if not provided
        model = model or self.config['model']
        temperature = temperature or self.config['temperature']
        max_tokens = max_tokens or self.config['max_tokens']

        # Send the request to the OpenAI API
        try:
            completion = self.client.chat.completions.create(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=[
                    {
                        'role': 'user',
                        'content': message
                    },
                    {
                        'role': 'system',
                        'content': 'You are a humorous robot assistant called Arnold. Created by me, Jonathan a South African software engineer.'
                    }
                ]
            )
        except requests.exceptions.HTTPError as e:
            self._logger.error(f'Error while generating completion: {e}')
            raise

        # Return the completion result
        return Completion(
            message=completion.choices[0].message.content,
            total_tokens=completion.usage.total_tokens
        )
