class PauseDurationError(Exception):
    raise Exception(
        'The pause duration must be greater than 0.1 to prevent seg fault'
    )
