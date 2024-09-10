import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import requests

from arnold import config

_logger = logging.getLogger(__name__)


@dataclass
class Location:
    """Location dataclass"""

    latitude: float
    longitude: float

    def __str__(self):
        return f'{self.latitude},{self.longitude}'


class Weather(object):
    """Weather integration class which gets, caches and provides current and
    forecast weather for a specific location.

    Args:
        object (Location): The location (latitude & longitude) to get weather
        data for.
    """

    def __init__(self, location: Location) -> None:
        self.location = location
        self.config = config.INTEGRATION['weather']

        # Setup logging
        self._logger = _logger

    def _build_url(self) -> str:
        base_url, api_key = self.config['url'], self.config['api_key']
        return f'{base_url}?lat={self.location.latitude}&lon={self.location.longitude}&exclude=minutely,hourly&units=metric&appid={api_key}'

    def _get_weather_data(self) -> dict:
        url = self._build_url()
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    @property
    def current(self) -> Optional[dict]:
        weather_data = self._get_weather_data()
        if weather_data is not None:
            current_weather_data = weather_data['current']
            try:
                return {
                    'humidity': current_weather_data['humidity'],
                    'rain': current_weather_data['weather'][0]['main'] == 'Rain',
                    'temperature': current_weather_data['temp'],
                }
            except (KeyError, IndexError):
                self._logger.warning(f'No weather data returned for {self.location}')
                return None

    @property
    def forecast(self) -> Optional[list]:
        weather_data = self._get_weather_data()
        if weather_data is not None:
            forecast_weather_data = weather_data['daily']
            parsed_forecast_weather_data = []
            for forecast in forecast_weather_data:
                try:
                    parsed_forecast_weather_data.append(
                        {
                            'date': datetime.fromtimestamp(forecast['dt']).strftime(
                                '%Y-%m-%d'
                            ),
                            'humidity': forecast.get('humidity', None),
                            'rain': forecast.get('rain', 0) > 0.2,
                            'temperature': {
                                'maximum': forecast['temp']['max'],
                                'minimum': forecast['temp']['min'],
                            },
                            'summary': forecast.get('summary', None)
                        }
                    )
                except (KeyError, IndexError):
                    self._logger.warning(f'No weather data returned for {self.location}')
                    return None
            return parsed_forecast_weather_data
