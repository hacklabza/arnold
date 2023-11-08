COMMAND_MAP = {
    'motion': {
        'tokens': ['go', 'proceed', 'move', 'travel', 'walk', 'drive', 'turn', 'stop', 'halt', 'pause'],
        'map': {
            'class': 'motion.drivetrain.DriveTrain',
            'post_hook': 'release',
            'methods': [
                {
                    'tokens': ['forward', 'forth', 'frontwards', 'front'],
                    'method': 'forward',
                    'params': [
                        {
                            'tokens': ['seconds', 'steps', 'paces', 'second', 'step', 'pace'],
                            'param': 'duration',
                            'param_value': 'prefix'
                        }
                    ]
                },
                {
                    'tokens': ['back', 'rear', 'backward', 'backwards', 'reverse'],
                    'method': 'back',
                    'params': [
                        {
                            'tokens': ['seconds', 'steps', 'paces', 'second', 'step', 'pace'],
                            'param': 'duration',
                            'param_value': 'prefix'
                        }
                    ]
                },
                {
                    'tokens': ['stop', 'halt', 'pause'],
                    'method': 'stop',
                    'params': []
                },
                {
                    'tokens': ['turn', 'twist', 'swing'],
                    'method': 'turn',
                    'params': [
                        {
                            'tokens': ['right', 'rightward', 'rightwards'],
                            'param': 'direction',
                            'param_value': 'right'
                        },
                        {
                            'tokens': ['left', 'leftward', 'leftwards'],
                            'param': 'direction',
                            'param_value': 'left'
                        },
                        {
                            'tokens': ['seconds', 'steps', 'paces', 'second', 'step', 'pace'],
                            'param': 'duration',
                            'param_value': 'prefix'
                        }
                    ]
                }
            ]
        }
    },
    'lookup': {
        'tokens': ['weather'],
        'map': {
            'class': 'lookup.weather.Weather',
            'post_hook': None,
            'methods': [
                {
                    'tokens': ['today', 'now'],
                    'method': 'current',
                    'params': [],
                    'formatter': 'The humidity is {humidity}% and the current temperature is {temperature} C'
                },
                {
                    'tokens': ['tomorrow'],
                    'method': 'tomorrow',
                    'params': [],
                    'formatter': 'The humidity is {humidity}% and the current temperature is {temperature}'
                }
            ]
        }
    }
}

INT_MAP = {
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
}
