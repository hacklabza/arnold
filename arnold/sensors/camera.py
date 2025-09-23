import logging
import time
import tempfile
from os import path
from typing import Generator, Optional

try:
    import libcamera
except ImportError:
    raise ImportError('`libcamera` is not installed. This module is only available on the rpi.')

try:
    from picamera2 import Picamera2
except ImportError:
    raise ImportError('`picamera2` is not installed. This module is only available on the rpi.')

from arnold import config, lookup


_logger = logging.getLogger(__name__)


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
                transform=libcamera.Transform(hflip=1, vflip=0)
            )
        )
        camera.start()

        # Allow camera to warm up and then capture the image
        time.sleep(0.5)
        camera.capture_file(file_path)
        self._logger.info(f'Image captured to {file_path}.')

    def capture_video(
        self,
        file_path: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        frame_rate: Optional[int] = None,
        duration: Optional[float] = None,
    ) -> None:
        """
        Capture a video from the camera with option width, height, frame rate and
        duration.

        Args:
            file_path (str, optional): The file path to save the video to.
            width (str, optional): The wigth of the captured video.
            height (str, optional): The height of the captured video.
            frame_rate (str, optional): The frame rate of the captured video.
            duration (str, optional): The duration of the captured video.
        """
        file_path = file_path or self.video_config['file_path']
        width = width or self.video_config['width']
        height = height or self.video_config['height']
        frame_rate = frame_rate or self.video_config['frame_rate']
        duration = duration or self.video_config['duration']

        # TODO: Implement video capture
        self._logger.warning('Video capture not yet implemented.')

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

        # TODO: Implement video streaming
        self._logger.warning('Video streaming not yet implemented.')

    def recognise_image(self, file_path: Optional[str] = None) -> None:
        """
        Recognise objects in the captured image using OpenAI's vision model.
        """
        openai = lookup.openai.OpenAI()
        file_path = file_path or path.join(tempfile.gettempdir() , 'recognised_image.jpg')
        self.capture_image(file_path=file_path)
        description = openai.vision(file_path=file_path)
        return description.message
