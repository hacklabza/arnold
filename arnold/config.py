import json
import os

from dotenv import load_dotenv

# Load the environmental variables
load_dotenv()

# Get the root directory
ROOT_DIR = os.environ.get(
    'ARNOLD_ROOT_DIR',
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

# Integration config
INTEGRATION = {
    'googlecloud': {
        'key_path': os.environ.get('ARNOLD_GOOGLECLOUD_KEY_PATH'),
    },
    'openweather': {
        'url': 'https://api.openweathermap.org/data/3.0/onecall',
        'api_key': os.environ.get('ARNOLD_OPENWEATHER_APIKEY', 'openweather-key'),
        'latitude': os.environ.get('ARNOLD_OPENWEATHER_LATITUDE', -26.15),
        'longitude': os.environ.get('ARNOLD_OPENWEATHER_LONGITUDE', 28.30),
    },
    'openai': {
        'api_key': os.environ.get('ARNOLD_OPENAI_APIKEY', 'openai-key'),
        'organization_id': os.environ.get(
            'ARNOLD_OPENAI_ORGANIZATIONID', 'openai-organizationid'
        ),
        'project_id': os.environ.get('ARNOLD_OPENAI_PROJECTID', 'openai-projectid'),
        'model': os.environ.get('ARNOLD_OPENAI_MODEL', 'gpt-4o-mini'),
        'temperature': 0.2,
        'max_tokens': 100,
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
        'enable_pwm': False,
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

OUTPUT = {
    'speaker': {
        'rate': 150,
        'volume': 1.0
    }
}

SENSOR = {
    'camera': {
        'camera_number': 0,
        'image': {
            'file_path': os.path.join(ROOT_DIR, 'image.jpg'),
            'height': 480,
            'width': 640,
        },
        'video': {
            'duration': 10,
            'file_path': os.path.join(ROOT_DIR, 'video.avi'),
            'frame_rate': 15,
            'height': 480,
            'width': 640,
        }
    },
    'imu': {
        'address': '68',
        'orientation': {
            'x': 'x',
            'y': 'y',
            'z': 'z'
        },
        'bias': json.loads(
            os.environ.get(
                'ARNOLD_SENSOR_IMU_BIAS',
                json.dumps({
                    'accelerometer': [0, 0, 0],
                    'gyroscope': [0, 0, 0],
                    'magnetometer': [0, 0, 0]
                })
            )
        )
    },
    'lidar': {
        'serial_port': '/dev/ttyS0',
        'baudrate': 115200
    },
    'microphone': {
        'card_number': 1,
        'device_index': 0,
        'sample_rate': 48000,
        'phrase_time_limit': 30,
        'energy_threshold': 700
    }
}
