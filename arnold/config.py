import os

GPIO_MAP = {
    "motion": {
        "left": {
            "pins": [23, 24]
        },
        "right": {
            "pins": [17, 22]
        }
    }
}

# Component config
SENSOR_CONFIG = {
    'microphone': {
        'card_number': 1,
        'device_number': 0
    },
    'google_cloud': {
        "api_key": os.environ.get('ARNOLD_GOOGLE_CLOUD_APIKEY', '')
    }
}
