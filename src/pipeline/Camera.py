import cv2
import cv2.typing
import numpy
import time
from typing import Optional, Tuple

from config.NTConfig import NTConfig

class Camera:
    _camera: Optional[cv2.VideoCapture] = None
    _config: Optional[NTConfig] = None

    def read(self, nt_config: NTConfig) -> Tuple[bool, cv2.typing.MatLike]:
        self._update_config(nt_config)

        if self._camera != None:
            success, frame = self._camera.read()
            if not success:
                print("Unable to capture camera frame, restarting camera...")
                self._camera.release()
                self._camera = None
                time.sleep(1)
            return success, frame
        else:
            return False, cv2.Mat(numpy.ndarray([]))

    def _update_config(self, new_config: NTConfig) -> None:        
        if self._camera != None:
            if self._config == None or new_config.device_path != self._config.device_path or new_config.height != self._config.height or new_config.width != self._config.width or new_config.auto_exposure != self._config.auto_exposure or new_config.gain != self._config.gain:
                print("Camera config changed, restarting camera...")
                self._camera.release()
                self._camera = None
                time.sleep(1)

        self._config = new_config

        if self._camera == None:
            print("Starting camera...")
            self._camera = cv2.VideoCapture(
                "v4l2src device="
                    + str(self._config.device_path)
                    + " ! video/x-raw, format=BGR, width="
                    + str(self._config.width)
                    + ", height="
                    + str(self._config.height)
                    + ", pixel-aspect-ratio=1/1, extra_controls=\"c, exposure_auto="
                    + str(self._config.auto_exposure)
                    + ", exposure_absolute="
                    + str(self._config.absolute_exposure)
                    + ", gain="
                    + str(self._config.gain)
                    + ", sharpness=0, brightness=0\" ! videoconvert ! appsink drop=1",
                cv2.CAP_GSTREAMER
            )
            print("Camera Started")
