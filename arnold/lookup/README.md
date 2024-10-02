# Lookups

Arnold is able to do lookups from external APIs as follows:

## OpenAI

### Config

Update in `arnold/config.py` or via env vars.

```python
INTEGRATION = {
    'openai': {
        'api_key': '<your-openai-api-key>',
        'organization_id': '<your-openai-organizationid>',
        'project_id': '<your-openai-projectid>',
        'model': 'gpt-4o-mini',
        'temperature': 0.2,
        'max_tokens': 100,
    },
    ...
}
```

### Usage

```python
from arnold.lookup import openai

message = 'Hi Arnold, how you doing today?'
openai = openai.OpenAI()
response = openai.prompt(message=message)

# Get the response
response.message

# Get the total tokens used
response.total_tokens
```

## Weather

### Config

Update in `arnold/config.py`.

```python
INTEGRATION = {
    'openweather': {
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
weather = weather.Weather(location=location)

# Get the current weather conditions
weather.current

# Get the forecasted weather conditions
weather.forecast
```
