from fastapi import FastAPI
from pydantic import BaseModel

from arnold.output.speaker import Speaker


app = FastAPI()


# TODO (qoda): Make this super generic

class Phrase(BaseModel):
    text: str


@app.get('/health')
def health():
    return {'status': 'up'}


@app.post('/output/speaker')
def speak(phrase: Phrase):
    speaker = Speaker()
    speaker.say(phrase.text)
    return {'success': True}
