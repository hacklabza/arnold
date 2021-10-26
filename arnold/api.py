from typing import Optional

from bottle import request, route, run
import uvicorn

from arnold import config
from arnold.output.speaker import Speaker


API_CONFIG = config.API

# Module class instances, rather than init everytime
speaker = Speaker()


# TODO (qoda): Make this super generic


@route('/health')
def health():
    return {'success': True}


@route('/output/speaker', method='POST')
def speak():
    phrase = request.json.get('phrase', 'No input')
    speaker.say(phrase)
    return {'success': True}


def runserver(host: Optional[str] = None, port: Optional[int] = None):
    host = host or API_CONFIG['host']
    port = port or API_CONFIG['port']
    run(host=host, port=port)
