import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import requests

from arnold import config


_logger = logging.getLogger(__name__)


@dataclass
class Location:
    """
    Location dataclass which represents a geographic location with latitude and
    longitude coordinates.

    Args:
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.

    Returns:
        str: A string representation of the location in the format 'latitude,longitude'.
    """

    latitude: float
    longitude: float

    def __str__(self):
        return f'{self.latitude},{self.longitude}'


class Weather(object):
    """
    Weather integration class which gets, caches and provides current and forecast
    weather for a specific location.

    Args:
        object (Location): The location (latitude & longitude) to get weather data for
    """

    def __init__(self, location: Optional[Location] = None) -> None:
        self.config = config.INTEGRATION['openweather']
        self.location = location or Location(
            latitude=self.config['latitude'],
            longitude=self.config['longitude']
        )

        # Setup logging
        self._logger = _logger

    def _build_url(self) -> str:
        """
        Builds the URL for the weather API request based on the configured base URL, API
        key, and the latitude and longitude of the location.

        Returns:
            str: The constructed URL for the weather API request.
        """
        base_url, api_key = self.config['url'], self.config['api_key']
        return f'{base_url}?lat={self.location.latitude}&lon={self.location.longitude}&exclude=minutely,hourly&units=metric&appid={api_key}'

    def _get_weather_data(self) -> dict:
        """
        Retrieves the weather data from the configured weather API based on the location.

        Returns:
            dict: The weather data response from the API.
        """
        url = self._build_url()
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    @property
    def current(self) -> Optional[dict]:
        """
        Retrieves the current weather conditions for the specified location.

        Returns:
            Optional[dict]: A dictionary containing the current weather conditions,
            including humidity, rain status, and temperature. If no weather data is
            available, returns `None`.
        """
        weather_data = self._get_weather_data()
        if weather_data is not None:
            current_weather_data = weather_data['current']
            try:
                return {
                    'humidity': current_weather_data['humidity'],
                    'rain': current_weather_data['weather'][0]['main'] == 'Rain',
                    'temperature': int(current_weather_data['temp']),
                }
            except (KeyError, IndexError):
                self._logger.warning(f'No weather data returned for {self.location}')
                return None

    @property
    def forecast(self) -> Optional[list]:
        """
        Retrieves the weather forecast for the specified location over the next 7 days
        including the current day.

        Returns:
            Optional[list]: A list of dictionaries containing the weather forecast for
            each day, including the date, humidity, rain forecast, temperature
            (maximum and minimum), and a summary. If no weather data is available,
            returns `None`.
        """
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
                                'maximum': int(forecast['temp']['max']),
                                'minimum': int(forecast['temp']['min']),
                            },
                            'summary': forecast.get('summary', None)
                        }
                    )
                except (KeyError, IndexError):
                    self._logger.warning(f'No weather data returned for {self.location}')
                    return None
            return parsed_forecast_weather_data

    @property
    def tomorrow(self) -> Optional[dict]:
        """
        Returns the weather forecast for the next day.

        Returns:
            Optional[dict]: A dictionary containing the weather forecast for the next day,
            including the date, humidity, rain forecast, temperature (maximum and minimum),
            and a summary. If no weather data is available, returns `None`.
        """
        return self.forecast[1] if self.forecast else None
