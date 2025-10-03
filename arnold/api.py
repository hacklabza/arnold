from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn

from arnold import config, models


API_CONFIG = config.API


api = FastAPI(title=API_CONFIG['title'], version=API_CONFIG['version'])


@api.get('/health')
def health():
    return {'success': True}


@api.post('/motion/drivetrain/go')
def drivetrain_go(request: models.DrivetrainRequest):
    try:
        api.arnold.drivetrain.go(
            direction=request.direction,
            duration=request.duration,
            speed=request.speed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {'success': True}


@api.post('/motion/drivetrain/stop')
def drivetrain_stop():
    try:
        api.arnold.drivetrain.stop()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {'success': True}


@api.post('/output/speaker/say')
def speaker_say(request: models.SpeakerRequest):
    try:
        api.arnold.speaker.say(request.phrase)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {'success': True}


@api.get('/sensor/camera/stream')
def camera_stream(
    width: Optional[int] = None,
    height: Optional[int] = None,
    frame_rate: Optional[int] = None
):
    return StreamingResponse(
        api.arnold.camera.stream_video(
            width=width,
            height=height,
            frame_rate=frame_rate
        ),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )


def runserver(
    arnold: object,
    host: Optional[str] = None,
    port: Optional[int] = None,
    debug: Optional[bool] = None,
    reload: Optional[bool] = None
) -> None:
    """
    Run the FastAPI server with uvicorn.
    """
    host = host or API_CONFIG['host']
    port = port or API_CONFIG['port']
    debug = debug or API_CONFIG['debug']
    reload = reload or API_CONFIG['reload']

    # Set the global arnold instance for access in routes
    arnold_instance = arnold

    # Initialize the FastAPI api with an instance of arnold
    api.arnold = arnold_instance

    # Mount the routes
    api.mount("/api", api)

    server_config = uvicorn.Config(
        app=api,
        host=host,
        port=port,
        reload=reload,
        loop="asyncio",
        timeout_keep_alive=5,
        timeout_notify=5
    )
    server = uvicorn.Server(server_config)
    server.run()
