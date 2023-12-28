from typing import Optional

from bottle import request, route, run, Response
import uvicorn

from arnold import config
from arnold.output.speaker import Speaker
from arnold.sensors.camera import Camera


API_CONFIG = config.API

# Module class instances, rather than init everytime
speaker = Speaker()
camera = Camera()


# TODO (qoda): Make this super generic


@route('/health')
def health():
    return {'success': True}


@route('/output/speaker/say', method='POST')
def say():
    phrase = request.json.get('phrase', 'No input')
    speaker.say(phrase)
    return {'success': True}


@route('/sensor/camera/stream', method='GET')
def video_stream():
    stream = camera.stream_video()
    return Response(stream, mimetype='multipart/x-mixed-replace; boundary=frame')


def runserver(host: Optional[str] = None, port: Optional[int] = None):
    host = host or API_CONFIG['host']
    port = port or API_CONFIG['port']
    run(host=host, port=port)
