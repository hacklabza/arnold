import logging
import io
import time
import tempfile
from os import path
from threading import Condition
from typing import Generator, Optional


try:
    import libcamera
except ImportError:
    raise ImportError('`libcamera` is not installed. This module is only available on the rpi.')

try:
    from picamera2 import Picamera2
    from picamera2.encoders import MJPEGEncoder
    from picamera2.outputs import FileOutput
except ImportError:
    raise ImportError('`picamera2` is not installed. This module is only available on the rpi.')

from arnold import config, lookup


_logger = logging.getLogger(__name__)


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class Camera(object):
    """
    A sensor class which initialises the camera component and adds image capture,
    video streaming and object recognition to Arnold.

    Args:
        camera_number (int, optional): The camera device number.
    """
    def __init__(self, camera_number: Optional[int] = None) -> None:
        self.config = config.SENSOR['camera']
        self.image_config = self.config['image']
        self.video_config = self.config['video']

        # RPi camera config
        self.camera_number = (
            self.config['camera_number'] if camera_number is None else camera_number
        )

        # Setup logging
        self._logger = _logger

        # Set picamera logging level to warning
        Picamera2.set_logging()

    def capture_image(
        self,
        file_path: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> None:
        """
        Capture an image to file from the camera with optional width and height.

        Args:
            file_path (str, optional): The file path to save the image to.
            width (str, optional): The width of the captured image.
            height (str, optional): The height of the captured image.
        """
        file_path = file_path or self.image_config['file_path']
        width = width or self.image_config['width']
        height = height or self.image_config['height']

        self._logger.info(f'Capturing image to {file_path}.')

        # Initialise the camera and set width and height
        camera = Picamera2(camera_num=self.camera_number)
        camera.configure(
            camera.create_still_configuration(
                main={
                    'size': (width, height),
                },
                transform=libcamera.Transform(hflip=0, vflip=1)
            )
        )
        camera.start()

        # Allow camera to warm up and then capture the image
        time.sleep(0.5)
        camera.capture_file(file_path)
        self._logger.info(f'Image captured to {file_path}.')

        # Finally close the camera
        camera.close()

    def capture_video(
        self,
        file_path: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        duration: Optional[float] = None,
    ) -> None:
        """
        Capture a video from the camera with option width, height, frame rate and
        duration.

        Args:
            file_path (str, optional): The file path to save the video to.
            width (str, optional): The wigth of the captured video.
            height (str, optional): The height of the captured video.
            duration (str, optional): The duration of the captured video.
        """
        file_path = file_path or self.video_config['file_path']
        width = width or self.video_config['width']
        height = height or self.video_config['height']
        duration = duration or self.video_config['duration']

        self._logger.info(f'Capturing video to {file_path}.')

        # Initialise the camera and set width and height
        camera = Picamera2(camera_num=self.camera_number)
        camera.configure(
            camera.create_video_configuration(
                main={
                    'size': (width, height),
                },
                transform=libcamera.Transform(hflip=0, vflip=1)
            )
        )

        # Allow camera to warm up and then start capturing the video.
        time.sleep(0.5)
        camera.start_recording(MJPEGEncoder(), file_path)

        # Sleep for the duration and then stop recording
        time.sleep(duration)
        camera.stop_recording()
        self._logger.info(f'Video captured to {file_path}.')

        # Finally close the camera
        camera.close()

    def stream_video(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        frame_rate: Optional[int] = None,
    ) -> Generator:
        """
        Stream video from the camera with optional width, height and frame rate.

        Args:
            width (str, optional): The wigth of the captured video.
            height (str, optional): The height of the captured video.
            frame_rate (str, optional): The frame rate of the captured video.
        """
        width = width or self.video_config['width']
        height = height or self.video_config['height']
        frame_rate = frame_rate or self.video_config['frame_rate']

        self._logger.info('Streaming video from camera.')

        # Stream video from the camera
        camera = Picamera2(camera_num=self.camera_number)
        camera.configure(
            camera.create_video_configuration(
                main={
                    'size': (width, height),
                },
                transform=libcamera.Transform(hflip=0, vflip=1)
            )
        )

        # Stream video frames
        video_stream = StreamingOutput()
        camera.start_recording(MJPEGEncoder(), FileOutput(video_stream))

        # Allow camera to warm up and then capture the image
        try:
            while True:
                with video_stream.condition:
                    video_stream.condition.wait()
                    frame = video_stream.frame
                yield (
                    b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
                )
        except GeneratorExit:
            self._logger.info('Stopping video stream.')

            # Finally stop recording and close the camera
            camera.stop_recording()
            camera.close()

    def recognise_image(self, file_path: Optional[str] = None) -> None:
        """
        Recognise objects in the captured image using OpenAI's vision model.

        Args:
            file_path (str, optional): The file path to save the image to. If not
            provided, a temporary file will be used.

        Returns:
            str: The description of the image.
        """

        # Use a temporary file if no file path is provided
        file_path = file_path or path.join(tempfile.gettempdir() , 'recognised_image.jpg')

        # Capture the image and get the description from OpenAI
        self.capture_image(file_path=file_path)
        openai = lookup.openai.OpenAI()
        description = openai.vision(file_path=file_path)
        return description.message.replace('Image description: ', '')
