# Lookups

Arnold is able to do lookups from external APIs as follows:

## ChatGPT

### Config

Update in `arnold/config.py` or via env vars.

```python
INTEGRATION = {
    'chatgpt': {
        'api_key': '<your-chatgpt-api-key>',
        'organization_id': '<your-chatgpt-organizationid>',
        'project_id': '<your-chatgpt-projectid>',
        'model': 'gpt-4o-mini',
        'temperature': 0.2,
        'max_tokens': 100,
    },
    ...
}
```

### Usage

```python
from arnold.lookup import chatgpt

message = 'Hi Arnold, how you doing today?'
chatgpt = chatgpt.ChaptGPT()
response = chatgpt.prompt(message=message)

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
