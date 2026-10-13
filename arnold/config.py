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
    'title': 'Arnold API',
    'version': '0..0',
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
            'height': 600,
            'width': 800,
        },
        'video': {
            'duration': 10,
            'file_path': os.path.join(ROOT_DIR, 'video.avi'),
            'height': 600,
            'width': 800,
            'frame_rate': 30,
        }
    },
    'imu': {
        'bus': 1,
        'address': {
            'accelerometer': '53',
            'gyroscope': '68',
            # None auto-detects HMC5883L (1e), QMC5883 (0d) or VCM5883L (0c)
            'magnetometer': None
        },
        'sample_size': 5,
        # Magnetic declination in degrees (east positive) to turn magnetic north
        # into true north. Look it up at https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml
        'declination': float(os.environ.get('ARNOLD_SENSOR_IMU_DECLINATION', -20.88)),
        'calibrate_gyroscope_on_start': True,
        # Maps each sensor's axes onto Arnold's body: x forward, y left, z up.
        # Prefix with `-` to invert an axis, eg. {'x': '-y', 'y': 'x', 'z': 'z'}
        'orientation': {
            'accelerometer': {'x': 'x', 'y': 'y', 'z': 'z'},
            'gyroscope': {'x': 'x', 'y': 'y', 'z': 'z'},
            'magnetometer': {'x': 'x', 'y': 'y', 'z': 'z'}
        },
        'filter': {
            'rate': 100,  # Hz
            'attitude_time_constant': 0.5,  # secs
            'attitude_moving_time_constant': 10.0,  # secs
            'heading_time_constant': 2.0,  # secs
            'velocity_time_constant': 30.0,  # secs
            'turn_rate_smoothing': 0.8,
            'stationary_window': 0.5  # secs
        },
        'thresholds': {
            'velocity': 0.05,  # m/s
            'reverse_velocity': 0.2,  # m/s
            'acceleration_deadband': 0.1,  # m/s²
            'attitude_acceleration': 0.15,  # g
            'turn_rate': 15.0,  # deg/s
            'tilt': 5.0,  # deg
            'stationary_acceleration': 0.015,  # g
            'stationary_rotation': 3.0  # deg/s
        },
        'bias': json.loads(
            os.environ.get(
                'ARNOLD_SENSOR_IMU_BIAS',
                json.dumps({
                    'accelerometer': [0, 0, 0],
                    'gyroscope': [0, 0, 0],
                    'magnetometer': {
                        'hard_iron': [0, 0, 0],
                        'soft_iron': [1, 1, 1]
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
