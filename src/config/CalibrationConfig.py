import cv2
import cv2.typing
from dataclasses import dataclass, field
import datetime
import numpy
import os

@dataclass
class CalibrationConfig:
    distortion_matrix: cv2.typing.MatLike = field(default_factory = lambda: numpy.array([]))
    distortion_coefficients: cv2.typing.MatLike = field(default_factory = lambda: numpy.array([]))

class CalibrationConfigLoader:
    FILENAME = "calibration_config.json"

    def load(self) -> CalibrationConfig:
        config = CalibrationConfig()
        file = cv2.FileStorage(self.FILENAME, cv2.FILE_STORAGE_READ)
        config.distortion_matrix = file.getNode("distortion_matrix").mat()
        config.distortion_coefficients = file.getNode("distortion_coefficients").mat()
        return config
    
    def write(self, distortion_matrix: cv2.typing.MatLike, distortion_coefficients: cv2.typing.MatLike) -> None:
        file = cv2.FileStorage(self.FILENAME, cv2.FILE_STORAGE_WRITE)
        file.write("date", str(datetime.datetime.now()))
        file.write("distortion_matrix", distortion_matrix)
        file.write("distortion_coefficients", distortion_coefficients)
        file.release()

    def remove_config (self) -> None:
        if os.path.exists(self.FILENAME):
            os.remove(self.FILENAME)
