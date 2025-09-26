from typing import Optional

from bottle import Bottle, request, response, run

from arnold import config
from arnold.motion.drivetrain import DriveTrain
from arnold.output.speaker import Speaker
from arnold.sensors.camera import Camera


API_CONFIG = config.API


api = Bottle()


@api.route('/health')
def health():
    return {'success': True}


@api.route('/motion/drivetrain/go', method='POST')
def drivetrain_go():
    drivetrain = DriveTrain()
    direction = request.json.get('direction', 'forward')
    duration = request.json.get('duration')
    drivetrain.go(direction=direction, duration=duration)
    return {'success': True}


@api.route('/output/speaker/say', method='POST')
def speaker_say():
    speaker = Speaker()
    phrase = request.json.get('phrase', 'No input')
    speaker.say(phrase)
    return {'success': True}


@api.route('/sensor/camera/stream', method='GET')
def camera_stream():
    response.content_type = 'multipart/x-mixed-replace; boundary=--frame'
    camera = Camera()
    return camera.stream_video()


def runserver(
    host: Optional[str] = None,
    port: Optional[int] = None,
    debug: Optional[bool] = None,
    reload: Optional[bool] = None
) -> None:
    host = host or API_CONFIG['host']
    port = port or API_CONFIG['port']
    debug = debug or API_CONFIG['debug']
    reload = reload or API_CONFIG['reload']

    # Mount the API with prefix
    api.mount('/api', api)

    # Start the server
    run(api, host=host, port=port, debug=debug, reloader=reload)
