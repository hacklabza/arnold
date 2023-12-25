import logging
import time
from typing import Optional

import cv2

from arnold import config


_logger = logging.getLogger(__name__)


class Camera(object):
    """A sensor class which initialises the camera component and adds image capture,
    video streaming and object recognition to Arnold.

    Args:
        camera_number (int, optional): The camera device number.
    """
    def __init__(
        self,
        camera_number: Optional[int] = None,

    ) -> None:
        self.config = config.SENSOR['camera']

        # RPi camera config
        self.camera_number = self.config['camera_number'] if camera_number is None else camera_number

        # Setup logging
        self._logger = _logger

    def capture_image(
            self,
            file_path: str,
            width: Optional[int],
            height: Optional[int]
        ) -> None:
        """Capture an image to file from the camera with optional width and height.

        Args:
            file_path (str): The file path to save the image to.
            width (str, optional): The wigth of the captured image.
            height (str, optional): The height of the captured image.
        """
        width = width or self.config['width']
        height = height or self.config['height']

        self._logger.info(f'Capturing image to {file_path}.')

        # Capture and save the image
        camera = cv2.VideoCapture(self.camera_number)
        camera.set(3, width)
        camera.set(4, height)

        _, image = camera.read()
        camera.release()

        if image is not None:
            cv2.imwrite(file_path, image)
            self._logger.info(f'Image captured to {file_path}.')
        else:
            self._logger.error(f'Failed to capture image.')

    def capture_video(
        self,
        file_path: str,
        width: Optional[int],
        height: Optional[int],
        frame_rate: Optional[int],
        duration: Optional[float]
    ) -> None:
        """
        Capture a video from the camera with option width and height.

        Args:
            file_path (str): The file path to save the video to.
            width (str, optional): The wigth of the captured video.
            height (str, optional): The height of the captured video.
            duration (str, optional): The duration of the captured video.
        """
        width = width or self.config['width']
        height = height or self.config['height']
        frame_rate = frame_rate or self.config['frame_rate']
        duration = duration or self.config['duration']

        self._logger.info(f'Capturing video to {file_path}.')

        # Capture and save the video
        camera = cv2.VideoCapture(self.camera_number)
        camera.set(3, width)
        camera.set(4, height)

        video = cv2.VideoWriter(
            filename=file_path,
            fourcc=cv2.VideoWriter_fourcc(*'XVID'),
            fps=frame_rate,
            frameSize=(width, height)
        )

        start_time = time.time()
        while (time.time() - start_time) < duration:
            _, image = camera.read()
            video.write(image)

        camera.release()
        video.release()

        self._logger.info(f'Video captured to {file_path}.')
