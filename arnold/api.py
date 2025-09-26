from typing import Optional

from bottle import Bottle, request, response, run

from arnold import config


API_CONFIG = config.API


api = Bottle()


@api.route('/health')
def health():
    return {'success': True}


@api.route('/motion/drivetrain/go', method='POST')
def drivetrain_go():
    direction = request.json.get('direction', 'forward')
    duration = request.json.get('duration', 5)
    speed = request.json.get('speed', 1.0)
    api.arnold.drivetrain.go(direction=direction, duration=duration, speed=speed)
    return {'success': True}


@api.route('/output/speaker/say', method='POST')
def speaker_say():
    phrase = request.json.get('phrase', 'No input')
    api.arnold.speaker.say(phrase)
    return {'success': True}


@api.route('/sensor/camera/stream', method='GET')
def camera_stream():
    response.content_type = 'multipart/x-mixed-replace; boundary=--frame'
    return api.arnold.camera.stream_video()


def runserver(
    arnold: object,
    host: Optional[str] = None,
    port: Optional[int] = None,
    debug: Optional[bool] = None,
    reload: Optional[bool] = None
) -> None:
    host = host or API_CONFIG['host']
    port = port or API_CONFIG['port']
    debug = debug or API_CONFIG['debug']
    reload = reload or API_CONFIG['reload']

    # Attached the instance of Arnold to the API for access in routes
    api.arnold = arnold

    # Mount the API with prefix
    api.mount('/api', api)

    # Start the server
    run(api, host=host, port=port, debug=debug, reloader=reload)
