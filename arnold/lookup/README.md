# Lookups

Arnold is able to do lookups from external APIs as follows:

## Weather

### Config

Update in `arnold/config.py`.

```python
INTEGRATION = {
    'weather': {
        'url': 'https://api.openweathermap.org/data/2.5/onecall',
        'api_key': '<your-openweather-api-key>',
    },
    ...
}
```

### Usage

```python
from arnold.lookup import weather

location = weather.Location(latitude=-26.15, longitude=28.30)
weather = weather.Weather(location=self.location)

# Get the current weather conditions
weather.current

# Get the forecasted weather conditions
weather.forecast
```
