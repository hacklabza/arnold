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
        self.image_config = self.config['image']
        self.video_config = self.config['video']

        # RPi camera config
        self.camera_number = self.config['camera_number'] if camera_number is None else camera_number

        # Setup logging
        self._logger = _logger

    def capture_image(
            self,
            file_path: str,
            width: Optional[int] = None,
            height: Optional[int] = None,
        ) -> None:
        """Capture an image to file from the camera with optional width and height.

        Args:
            file_path (str): The file path to save the image to.
            width (str, optional): The wigth of the captured image.
            height (str, optional): The height of the captured image.
        """
        width = width or self.image_config['width']
        height = height or self.image_config['height']

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
        width: Optional[int] = None,
        height: Optional[int] = None,
        frame_rate: Optional[int] = None,
        duration: Optional[float] = None,
    ) -> None:
        """
        Capture a video from the camera with option width, height, frame rate and
        duration.

        Args:
            file_path (str): The file path to save the video to.
            width (str, optional): The wigth of the captured video.
            height (str, optional): The height of the captured video.
            frame_rate (str, optional): The frame rate of the captured video.
            duration (str, optional): The duration of the captured video.
        """
        width = width or self.video_config['width']
        height = height or self.video_config['height']
        frame_rate = frame_rate or self.video_config['frame_rate']
        duration = duration or self.video_config['duration']

        self._logger.info(f'Capturing video to {file_path}.')

        # Capture and save the video
        camera = cv2.VideoCapture(self.camera_number)

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

    def stream_video(
            self,
            width: Optional[int] = None,
            height: Optional[int] = None,
            frame_rate: Optional[int] = None,
        ) -> None:
        """Stream video from the camera with optional width, height and frame rate.

        Args:
            width (str, optional): The wigth of the captured video.
            height (str, optional): The height of the captured video.
            frame_rate (str, optional): The frame rate of the captured video.
        """
        width = width or self.video_config['width']
        height = height or self.video_config['height']
        frame_rate = frame_rate or self.video_config['frame_rate']

        self._logger.info(f'Streaming video from camera.')

        # Stream video from the camera
        camera = cv2.VideoCapture(self.camera_number)
        camera.set(3, width)
        camera.set(4, height)

        while True:
            _, frame = camera.read()
            _, jpeg = cv2.imencode('.jpg', frame)
            jpeg_frame = jpeg.tobytes()

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + jpeg_frame + b'\r\n\r\n'
            )

            if cv2.waitKey(1) == 27:
                break

        camera.release()
        cv2.destroyAllWindows()
