import cv2
import cv2.typing
from typing import Sequence

class OverlayMarkers:
    def add_detections(self, capture: cv2.typing.MatLike, corners: Sequence[cv2.typing.MatLike], ids: cv2.typing.MatLike) -> None:
        cv2.aruco.drawDetectedMarkers(capture, corners, ids)

    def add_charuco_detection(self, capture: cv2.typing.MatLike, charuco_corners: cv2.typing.MatLike, charuco_ids: cv2.typing.MatLike, marker_corners: Sequence[cv2.typing.MatLike], marker_ids: cv2.typing.MatLike) -> None:
        if len(charuco_ids) > 0 and len(charuco_corners) > 0:
            cv2.aruco.drawDetectedCornersCharuco(capture, charuco_corners, charuco_ids)
        if len(marker_ids) > 0 and len(marker_corners) > 0:
            cv2.aruco.drawDetectedMarkers(capture, marker_corners, marker_ids)
