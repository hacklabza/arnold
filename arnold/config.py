import os

from dotenv import load_dotenv

# Load the environmental variables
load_dotenv()


GPIO_MAP = {
    'motion': {
        'left': {
            'pins': [23, 24]
        },
        'right': {
            'pins': [17, 22]
        }
    }
}

# Integration config
INTEGRATION_CONFIG = {
    'google_cloud': {
        'key_path': os.environ.get('ARNOLD_GOOGLE_CLOUD_KEY_PATH')
    }
}

# Component config
SENSOR_CONFIG = {
    'microphone': {
        'card_number': 1,
        'device_index': 0,
        'sample_rate': 48000,
        'phrase_time_limit': 10,
        'energy_threshold': 700
    }
}
