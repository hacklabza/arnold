import pyttsx3


class Speaker(object):
    def __init__(self):
        self.speech_engine = pyttsx3.init()

    def say(self, text: str) -> None:
        self.speech_engine.say(text)
        self.speech_engine.runAndWait()
