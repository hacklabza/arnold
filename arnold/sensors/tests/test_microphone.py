from arnold.sensors import microphone

def test_listen():
    mic = microphone.Microphone()
    voice_command = mic.listen()
    text_command = mic.recognise_command(voice_command)
