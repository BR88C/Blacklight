import cv2
import cv2.typing
from typing import Optional, Sequence

from filter.OverlayMarkers import OverlayMarkers
from config.CalibrationConfig import CalibrationConfigLoader

class CalibrationSession:
    _board: cv2.aruco.CharucoBoard
    _camera_size: Optional[cv2.typing.Size] = None
    _detector: cv2.aruco.CharucoDetector
    _img_points: Sequence[cv2.typing.MatLike] = []
    _obj_points: Sequence[cv2.typing.MatLike] = []
    _overlay_markers = OverlayMarkers()

    def __init__(self, squaresX: int, squaresY: int, squareLengthMeters: float, markerLengthMeters: float) -> None:
        self._board = cv2.aruco.CharucoBoard((squaresX, squaresY), squareLengthMeters, markerLengthMeters, cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_1000))

        self._detector = cv2.aruco.CharucoDetector(
            self._board,
            cv2.aruco.CharucoParameters(),
            cv2.aruco.DetectorParameters(),
            cv2.aruco.RefineParameters()
        )

    def intake_frame(self, capture: cv2.typing.MatLike, save: bool) -> None:
        if self._camera_size == None:
            self._camera_size = (capture.shape[0], capture.shape[1])

        charuco_corners, charuco_ids, marker_corners, marker_ids = self._detector.detectBoard(capture)
        self._overlay_markers.add_charuco_detection(capture, charuco_corners, charuco_ids, marker_corners, marker_ids)

        if save and len(marker_corners) > 0 and len(marker_ids) > 0:
            obj_points, image_points = self._board.matchImagePoints(charuco_corners, charuco_ids) # type: ignore
            self._obj_points.append(obj_points) # type: ignore
            self._img_points.append(image_points) # type: ignore

    def save_to_file(self, calibration_config_loader: CalibrationConfigLoader) -> None:
        if len(self._img_points) == 0 or len(self._obj_points) == 0:
            print("Unable to calibrate: no data")
            return

        calibration_config_loader.remove_config()

        if self._camera_size == None:
            print("Unable to calibrate: cannot determine camera size")
            return

        rms, distortion_matrix, distortion_coefficients, _, _ = cv2.calibrateCamera(self._obj_points, self._img_points, self._camera_size, None, None) # type: ignore

        if rms:
            calibration_config_loader.write(distortion_matrix, distortion_coefficients) # type: ignore
            print("Finished calibration")
        else:
            print("Calibration failed")
