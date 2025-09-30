from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn

from arnold import config, models


API_CONFIG = config.API


app = FastAPI(title='Arnold API', version='1.0.0')


# Global arnold instance
arnold_instance = None


@app.get('/health')
def health():
    return {'success': True}


@app.post('/motion/drivetrain/go')
def drivetrain_go(request: models.DrivetrainRequest):
    try:
        arnold_instance.drivetrain.go(
            direction=request.direction,
            duration=request.duration,
            speed=request.speed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {'success': True}


@app.post('/motion/drivetrain/stop')
def drivetrain_stop():
    try:
        arnold_instance.drivetrain.stop()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {'success': True}


@app.post('/output/speaker/say')
def speaker_say(request: models.SpeakerRequest):
    try:
        arnold_instance.speaker.say(request.phrase)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {'success': True}


@app.get('/sensor/camera/stream')
def camera_stream():
    return StreamingResponse(
        arnold_instance.camera.stream_video(),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )


def runserver(
    arnold: object,
    host: Optional[str] = None,
    port: Optional[int] = None,
    debug: Optional[bool] = None,
    reload: Optional[bool] = None
) -> None:
    global arnold_instance

    host = host or API_CONFIG['host']
    port = port or API_CONFIG['port']
    debug = debug or API_CONFIG['debug']
    reload = reload or API_CONFIG['reload']

    # Set the global arnold instance for access in routes
    arnold_instance = arnold

    # Start the FastAPI server with uvicorn
    uvicorn.run(app, host=host, port=port, reload=reload)
