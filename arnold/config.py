import os

from dotenv import load_dotenv

# Load the environmental variables
load_dotenv()

# Get the root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Integration config
INTEGRATION = {
    'google_cloud': {
        'key_path': os.environ.get('ARNOLD_GOOGLE_CLOUD_KEY_PATH')
    },
    'weather': {
        'url': 'https://api.openweathermap.org/data/2.5/onecall',
        'api_key': os.environ.get('ARNOLD_OPENWEATHER_APIKEY', 'openweather-key'),
    }
}

# API config
API = {
    'host': '0.0.0.0',
    'port': 8000
}

# Component config
MOTION = {
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

SENSOR = {
    'accelerometer': {
        'address': '59'
    },
    'lidar': {
        'serial_port': '/dev/ttyS0',
        'baudrate': 115200
    },
    'microphone': {
        'card_number': 1,
        'device_index': 0,
        'sample_rate': 48000,
        'phrase_time_limit': 10,
        'energy_threshold': 700
    }
}
