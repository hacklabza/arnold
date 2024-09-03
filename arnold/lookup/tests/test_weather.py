from datetime import datetime
import logging

from arnold.lookup import weather


logging.disable(logging.ERROR)


class TestDrivetrain:

    def setup_method(self, method):
        self.location = weather.Location(latitude=-26.15, longitude=28.30)
        self.weather = weather.Weather(location=self.location)
        self.config = self.weather.config
        self.api_response = {
            'current': {
                'dt': 1684929490,
                'sunrise': 1684926645,
                'sunset': 1684977332,
                'temp': 292.55,
                'feels_like': 292.87,
                'pressure': 1014,
                'humidity': 89,
                'dew_point': 290.69,
                'uvi': 0.16,
                'clouds': 53,
                'visibility': 10000,
                'wind_speed': 3.13,
                'wind_deg': 93,
                'wind_gust': 6.71,
                'weather': [
                    {
                        'id': 803,
                        'main': 'Clouds',
                        'description': 'broken clouds',
                        'icon': '04d'
                    }
                ]
            },
            'daily': [
                {
                    'dt': 1684951200,
                    'sunrise': 1684926645,
                    'sunset': 1684977332,
                    'moonrise': 1684941060,
                    'moonset': 1684905480,
                    'moon_phase': 0.16,
                    'summary': 'Expect a day of partly cloudy with rain',
                    'temp': {
                        'day': 299.03,
                        'min': 290.69,
                        'max': 300.35,
                        'night': 291.45,
                        'eve': 297.51,
                        'morn': 292.55
                    },
                    'feels_like': {
                        'day': 299.21,
                        'night': 291.37,
                        'eve': 297.86,
                        'morn': 292.87
                    },
                    'pressure': 1016,
                    'humidity': 59,
                    'dew_point': 290.48,
                    'wind_speed': 3.98,
                    'wind_deg': 76,
                    'wind_gust': 8.92,
                    'weather': [
                        {
                            'id': 500,
                            'main': 'Rain',
                            'description': 'light rain',
                            'icon': '10d'
                        }
                    ],
                    'clouds': 92,
                    'pop': 0.47,
                    'rain': 0.15,
                    'uvi': 9.23
                }
            ]
        }

    def test_build_url(self):
        url = self.weather._build_url()

        # Ensure that the url is built correctly based on the config
        assert self.config['url'] in url
        assert f'?lat={self.location.latitude}&lon={self.location.longitude}' in url
        assert self.config['api_key'] in url

    def test_get_weather_data(self, requests_mock):
        url = self.weather._build_url()
        requests_mock.get(url, json=self.api_response)
        weather_data = self.weather._get_weather_data()

        # Ensure that a dict is returned with the correct top level keys
        assert isinstance(weather_data, dict)
        for forcast_type in ['current', 'daily']:
            assert forcast_type in weather_data

    def test_current(self, requests_mock):
        url = self.weather._build_url()
        requests_mock.get(url, json=self.api_response)
        current_weather_data = self.weather.current

        # Ensure that the current weather is returned correctly
        assert current_weather_data == {
            'humidity': self.api_response['current']['humidity'],
            'rain': self.api_response['current']['weather'][0]['main'] == 'Rain',
            'temperature': self.api_response['current']['temp'],
        }

    def test_forecast(self, requests_mock):
        url = self.weather._build_url()
        requests_mock.get(url, json=self.api_response)
        forecast_weather_data = self.weather.forecast
        forecast_response_data = self.api_response['daily'][0]

        # Ensure that the current weather is returned correctly
        assert forecast_weather_data[0] == {
            'date': datetime.fromtimestamp(forecast_response_data['dt']).strftime(
                '%Y-%m-%d'
            ),
            'humidity': forecast_response_data.get('humidity', None),
            'rain': forecast_response_data['rain'] > 0.2,
            'temperature': {
                'maximum': forecast_response_data['temp']['max'],
                'minimum': forecast_response_data['temp']['min'],
            },
            'summary': forecast_response_data['summary']
        }
