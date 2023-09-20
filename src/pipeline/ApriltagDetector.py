import cv2
import cv2.typing
from dataclasses import dataclass
from typing import List, Optional

from config.NTConfig import NTConfig
from filter.OverlayMarkers import OverlayMarkers

@dataclass
class ApriltagDetection:
    id: int
    corners: cv2.typing.MatLike

class ApriltagDetector:
    _config: Optional[NTConfig] = None
    _detector = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_ARUCO_ORIGINAL), cv2.aruco.DetectorParameters(), cv2.aruco.RefineParameters())
    _dictionary: Optional[cv2.aruco.Dictionary] = None
    _overlay_markers = OverlayMarkers()

    def search(self, capture: cv2.typing.MatLike, nt_config: NTConfig) -> List[ApriltagDetection]:
        self._update_config(nt_config)

        if (self._dictionary != None):
            corners, ids, _ = self._detector.detectMarkers(capture)
            self._overlay_markers.add_detections(capture, corners, ids)
            if (len(corners) == 0):
                return []
            else:
                return [ApriltagDetection(id[0], corner) for id, corner in zip(ids, corners)]
        else:
            return []

    def _update_config(self, new_config: NTConfig) -> None:
        if self._config == None or new_config.tag_family != self._config.tag_family:
            lookup = self._dictionary_lookup(new_config.tag_family)
            if lookup != None:
                print("Apriltag Detector dictionary changed")
                self._dictionary = cv2.aruco.getPredefinedDictionary(lookup)
                self._detector.setDictionary(self._dictionary)
            else:
                print("Apriltag Detector dictionary removed")
                self._dictionary = None
                self._detector.setDictionary(cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_ARUCO_ORIGINAL))

        self._config = new_config

    def _dictionary_lookup(self, dict: str) -> Optional[int]:
        if dict == "16h5":
            return cv2.aruco.DICT_APRILTAG_16h5
        elif dict == "25h9":
            return cv2.aruco.DICT_APRILTAG_25h9
        elif dict == "36h10":
            return cv2.aruco.DICT_APRILTAG_36h10
        elif dict == "36h11":
            return cv2.aruco.DICT_APRILTAG_36h11
        else:
            return None
