import os

from dotenv import load_dotenv

# Load the environmental variables
load_dotenv()

# Get the root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Integration config
INTEGRATION_CONFIG = {
    'google_cloud': {
        'key_path': os.environ.get('ARNOLD_GOOGLE_CLOUD_KEY_PATH')
    }
}

# Component config
MOTION_CONFIG = {
    'drivetrain': {
        'enable_pwm': True,
        'gpio': {
            'left': {
                'pins': [24, 23]
            },
            'right': {
                'pins': [22, 17]
            }
        },
        'pause_duration': 0.1
    }
}

SENSOR_CONFIG = {
    'microphone': {
        'card_number': 1,
        'device_index': 0,
        'sample_rate': 48000,
        'phrase_time_limit': 10,
        'energy_threshold': 700
    }
}
