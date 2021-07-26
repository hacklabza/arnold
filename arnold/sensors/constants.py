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
                                'param': 'duration',
                                'param_value': 'suffix'
                            }
                        ]
                    },
                    {
                        'tokens': ['back', 'rear', 'backward', 'backwards', 'reverse'],
                        'method': 'back',
                        'params': [
                            {
                                'tokens': ['seconds', 'steps'],
                                'param': 'duration',
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
                                'param': 'direction',
                                'param_value': 'right'
                            },
                            {
                                'tokens': ['left', 'leftward', 'leftwards'],
                                'param': 'direction',
                                'param_value': 'left'
                            },
                            {
                                'tokens': ['seconds', 'steps'],
                                'param': 'duration',
                                'param_value': 'suffix'
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
