import logging
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
        """Capture an image from the camera with option width and height.

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
