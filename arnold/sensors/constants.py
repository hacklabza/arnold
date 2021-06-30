SPEECH_COMMAND_MAP = {
    'actions': {
        'motion': {
            'tokens': ['go', 'proceed', 'move', 'travel', 'walk', 'drive'],
            'map': {
                'class': 'motion.drive.Drive',
                'methods': [
                    {
                        'tokens': ['forward', 'forth', 'frontwards', 'front'],
                        'method': 'forward',
                        'params': [
                            {
                                'tokens': ['seconds', 'steps'],
                                'param': 'seconds',
                                'param_value': 'suffix'
                            }
                        ]
                    },
                    {
                        'tokens': ['back', 'rear', 'backward', 'backwards', 'reverse'],
                        'method': 'reverse',
                        'params': [
                            {
                                'tokens': ['seconds', 'steps'],
                                'param': 'seconds',
                                'param_value': 'suffix'
                            }
                        ]
                    },
                    {
                        'tokens': ['turn', 'twist', 'swing'],
                        'method': 'turn',
                        'params': [
                            {
                                'tokens': ['right', 'rightward', 'rightwards'],
                                'param': 'right',
                                'param_value': 'isset'
                            },
                            {
                                'tokens': ['left', 'leftward', 'leftwards'],
                                'param': 'left',
                                'param_value': 'isset'
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
                'methods': [
                    {
                        'tokens': ['today', 'now'],
                        'method': 'today',
                        'params': []
                    },
                    {
                        'tokens': ['tomorrow'],
                        'method': 'tomorrow',
                        'params': []
                    }
                ]
            }
        }
    }
}
