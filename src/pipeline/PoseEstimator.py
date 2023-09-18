import cv2
import cv2.typing
from dataclasses import dataclass
import math
import numpy
import numpy.typing
from typing import List, Union
from wpimath.geometry import Quaternion, Pose3d, Rotation3d, Transform3d, Translation3d

from config.CalibrationConfig import CalibrationConfig;
from config.NTConfig import NTConfig
from pipeline.ApriltagDetector import ApriltagDetection

@dataclass
class PoseEstimation:
    ids: List[int]
    pose_0: Pose3d
    error_0: float
    pose_1: Union[Pose3d, None]
    error_1: Union[float, None]

class PoseEstimator:
    def get_estimated_camera_pose(self, detections: List[ApriltagDetection], calibration_config: CalibrationConfig, nt_config: NTConfig) -> Union[PoseEstimation, None]:
        if len(detections) == 0 or len(calibration_config.distortion_coefficients) == 0 or len(calibration_config.distortion_matrix) == 0 or len(nt_config.tag_layout) == 0:
            return None

        tags: List[int] = []
        tag_poses: List[Pose3d] = []
        points: List[List[float]] = []
        image_points: List[List[float]] = []
        for detection in detections:
            tag_pose: Union[Pose3d, None] = None

            for config_tag_pose in nt_config.tag_layout:
                if config_tag_pose.id == detection.id:
                    tag_pose = Pose3d(
                        Translation3d(config_tag_pose.x, config_tag_pose.y, config_tag_pose.z),
                        Rotation3d(Quaternion(config_tag_pose.qw, config_tag_pose.qx, config_tag_pose.qy, config_tag_pose.qz))
                    )

            if tag_pose != None:
                corner_0 = tag_pose + Transform3d(Translation3d(0, nt_config.tag_size / 2.0, -nt_config.tag_size / 2.0), Rotation3d())
                corner_1 = tag_pose + Transform3d(Translation3d(0, -nt_config.tag_size / 2.0, -nt_config.tag_size / 2.0), Rotation3d())
                corner_2 = tag_pose + Transform3d(Translation3d(0, -nt_config.tag_size / 2.0, nt_config.tag_size / 2.0), Rotation3d())
                corner_3 = tag_pose + Transform3d(Translation3d(0, nt_config.tag_size / 2.0, nt_config.tag_size / 2.0), Rotation3d())

                points += [
                    self._to_opencv(corner_0.translation()),
                    self._to_opencv(corner_1.translation()),
                    self._to_opencv(corner_2.translation()),
                    self._to_opencv(corner_3.translation())
                ]

                image_points += [
                    [detection.corners[0][0][0], detection.corners[0][0][1]],
                    [detection.corners[0][1][0], detection.corners[0][1][1]],
                    [detection.corners[0][2][0], detection.corners[0][2][1]],
                    [detection.corners[0][3][0], detection.corners[0][3][1]]
                ]

                tags.append(detection.id)
                tag_poses.append(tag_pose)

        if len(tags) == 0:
            return None
        elif len(tags) == 1:
            try:
                _, rvecs, tvecs, errors = cv2.solvePnPGeneric(
                    numpy.array([
                        [-nt_config.tag_size / 2.0, nt_config.tag_size / 2.0, 0.0],
                        [nt_config.tag_size / 2.0, nt_config.tag_size / 2.0, 0.0],
                        [nt_config.tag_size / 2.0, -nt_config.tag_size / 2.0, 0.0],
                        [-nt_config.tag_size / 2.0, -nt_config.tag_size / 2.0, 0.0]
                    ]),
                    numpy.array(image_points),
                    calibration_config.distortion_matrix,
                    calibration_config.distortion_coefficients,
                    flags = cv2.SOLVEPNP_IPPE_SQUARE
                )
            except:
                return None

            field_to_tag_pose = tag_poses[0]
            camera_to_tag_pose_0 = self._to_wpilib(tvecs[0], rvecs[0])
            camera_to_tag_pose_1 = self._to_wpilib(tvecs[1], rvecs[1])
            camera_to_tag_0 = Transform3d(camera_to_tag_pose_0.translation(), camera_to_tag_pose_0.rotation())
            camera_to_tag_1 = Transform3d(camera_to_tag_pose_1.translation(), camera_to_tag_pose_1.rotation())
            field_to_camera_0 = field_to_tag_pose.transformBy(camera_to_tag_0.inverse())
            field_to_camera_1 = field_to_tag_pose.transformBy(camera_to_tag_1.inverse())
            field_to_camera_pose_0 = Pose3d(field_to_camera_0.translation(), field_to_camera_0.rotation())
            field_to_camera_pose_1 = Pose3d(field_to_camera_1.translation(), field_to_camera_1.rotation())
            return PoseEstimation(tags, field_to_camera_pose_0, errors[0][0], field_to_camera_pose_1, errors[1][0])
        else:
            try:
                _, rvecs, tvecs, errors = cv2.solvePnPGeneric(
                    numpy.array(points),
                    numpy.array(image_points),
                    calibration_config.distortion_matrix,
                    calibration_config.distortion_coefficients,
                    flags = cv2.SOLVEPNP_SQPNP
                )
            except:
                return None

            camera_to_field_pose = self._to_wpilib(tvecs[0], rvecs[0])
            camera_to_field = Transform3d(camera_to_field_pose.translation(), camera_to_field_pose.rotation())
            field_to_camera = camera_to_field.inverse()
            field_to_camera_pose = Pose3d(field_to_camera.translation(), field_to_camera.rotation())
            return PoseEstimation(tags, field_to_camera_pose, errors[0][0], None, None)

    def get_estimated_debug_pose(self, detections: List[ApriltagDetection], calibration_config: CalibrationConfig, nt_config: NTConfig) -> Union[PoseEstimation, None]:
        for detection in detections:
            if detection.id == nt_config.debug_tag:
                try:
                    _, rvecs, tvecs, errors = cv2.solvePnPGeneric(
                        numpy.array([
                            [-nt_config.tag_size / 2.0, nt_config.tag_size / 2.0, 0.0],
                            [nt_config.tag_size / 2.0, nt_config.tag_size / 2.0, 0.0],
                            [nt_config.tag_size / 2.0, -nt_config.tag_size / 2.0, 0.0],
                            [-nt_config.tag_size / 2.0, -nt_config.tag_size / 2.0, 0.0]
                        ]),
                        detection.corners,
                        calibration_config.distortion_matrix,
                        calibration_config.distortion_coefficients,
                        flags = cv2.SOLVEPNP_IPPE_SQUARE
                    )
                except:
                    return None

                return PoseEstimation([detection.id], self._to_wpilib(tvecs[0], rvecs[0]), errors[0][0], self._to_wpilib(tvecs[1], rvecs[1]), errors[1][0])

    def _to_opencv(self, translation: Translation3d) -> List[float]:
        return [-translation.Y(), -translation.Z(), translation.X()] # type: ignore

    def _to_wpilib(self, tvec: cv2.typing.MatLike, rvec: cv2.typing.MatLike) -> Pose3d:
        return Pose3d(
            Translation3d(tvec[2][0], -tvec[0][0], -tvec[1][0]),
            Rotation3d(
                numpy.array([rvec[2][0], -rvec[0][0], -rvec[1][0]]),
                math.sqrt(math.pow(rvec[0][0], 2) + math.pow(rvec[1][0], 2) + math.pow(rvec[2][0], 2))
            )
        )
