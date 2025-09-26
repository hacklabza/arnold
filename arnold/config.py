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
        'model': os.environ.get('ARNOLD_OPENAI_MODEL', 'gpt-5-nano'),
        'temperature': 1.0,
        'max_tokens': 5000,
        'instructions': os.environ.get(
            'ARNOLD_OPENAI_INSTRUCTIONS',
            'You are a humorous robot assistant by the name of Arnold that gives concise responses.'
        )
    }
}

# API config
API = {
    'host': '0.0.0.0',
    'port': 8000,
    'debug': os.environ.get('ARNOLD_API_DEBUG', 'True').lower() in ('true', '1'),
    'reload': os.environ.get('ARNOLD_API_RELOAD', 'True').lower() in ('true', '1')
}

# Component config
MOTION = {
    'drivetrain': {
        'pwm': {
            'enable': True,
            'gpio': {
                'left': 12,
                'right': 13
            }
        },
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
        'camera_handler': os.environ.get('ARNOLD_CAMERA_HANDLER', 'picamera2'),
        'image': {
            'file_path': os.path.join(ROOT_DIR, 'image.jpg'),
            'height': 480,
            'width': 640,
        },
        'video': {
            'duration': 10,
            'file_path': os.path.join(ROOT_DIR, 'video.avi'),
            'height': 480,
            'width': 640,
        }
    },
    'imu': {
        'address': '68',
        'sample_size': 5,
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
                    'magnetometer': {
                        'hard_iron': [0, 0, 0],
                        'soft_iron': [0, 0, 0]
                    }
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
        'phrase_time_limit': 15,
        'energy_threshold': 900
    }
}
