import cv2
import cv2.typing
from dataclasses import dataclass
import math
import numpy
import numpy.typing
from typing import List, Optional
from wpimath.geometry import Pose3d, Rotation3d, Transform3d, Translation3d

from config.CalibrationConfig import CalibrationConfig;
from config.NTConfig import NTConfig
from pipeline.ApriltagDetector import ApriltagDetection

@dataclass
class PoseEstimation:
    ids: List[int]
    pose: Pose3d
    distance: float

class PoseEstimator:
    def get_estimated_pose(self, detections: List[ApriltagDetection], calibration_config: CalibrationConfig, nt_config: NTConfig) -> Optional[PoseEstimation]:
        if len(detections) == 0 or len(calibration_config.distortion_coefficients) == 0 or len(calibration_config.distortion_matrix) == 0 or len(nt_config.tag_layout) == 0:
            return None

        tags: List[int] = []
        tag_poses: List[Pose3d] = []
        points: List[List[float]] = []
        image_points: List[List[float]] = []
        for detection in detections:
            tag_pose: Optional[Pose3d] = None

            for config_tag_pose in nt_config.tag_layout:
                if config_tag_pose.id == detection.id:
                    tag_pose = Pose3d(
                        Translation3d(config_tag_pose.x, config_tag_pose.y, config_tag_pose.z),
                        Rotation3d(config_tag_pose.rx, config_tag_pose.ry, config_tag_pose.rz)
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

            error0 = errors[0][0]
            error1 = errors[1][0]
            field_to_tag_pose = tag_poses[0]

            if (error0 < (error1 * nt_config.error_ambiguity)):
                camera_to_tag_pose = self._to_wpilib(tvecs[0], rvecs[0])
                distance = camera_to_tag_pose.translation().norm() # type: ignore
                final_pose = self._to_robot_pose(field_to_tag_pose.transformBy(Transform3d(camera_to_tag_pose.translation(), camera_to_tag_pose.rotation())), nt_config)

                if self._is_outside_field(final_pose, nt_config):
                    return None
                else:
                    return PoseEstimation(tags, final_pose, distance) # type: ignore
            elif (error1 < (error0 * nt_config.error_ambiguity)):
                camera_to_tag_pose = self._to_wpilib(tvecs[1], rvecs[1])
                distance = camera_to_tag_pose.translation().norm() # type: ignore
                final_pose = self._to_robot_pose(field_to_tag_pose.transformBy(Transform3d(camera_to_tag_pose.translation(), camera_to_tag_pose.rotation()).inverse()), nt_config)

                if self._is_outside_field(final_pose, nt_config):
                    return None
                else:
                    return PoseEstimation(tags, final_pose, distance) # type: ignore
            else:
                return None
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
            field_to_camera = Transform3d(camera_to_field_pose.translation(), camera_to_field_pose.rotation()).inverse()
            final_pose = self._to_robot_pose(Pose3d(field_to_camera.translation(), field_to_camera.rotation()), nt_config)

            totalDistance = 0.0
            for tag_pose in tag_poses:
                totalDistance += final_pose.relativeTo(tag_pose).translation().norm() # type: ignore

            if self._is_outside_field(final_pose, nt_config):
                    return None
            else:
                return PoseEstimation(tags, final_pose, totalDistance / len(tag_poses)) # type: ignore

    def get_estimated_debug_pose(self, detections: List[ApriltagDetection], calibration_config: CalibrationConfig, nt_config: NTConfig) -> Optional[PoseEstimation]:
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

                error0 = errors[0][0]
                error1 = errors[1][0]

                if (error0 < (error1 * nt_config.error_ambiguity)):
                    camera_to_tag_pose = self._to_wpilib(tvecs[0], rvecs[0])
                    distance = camera_to_tag_pose.translation().norm() # type: ignore
                    return PoseEstimation([detection.id], self._to_robot_pose(camera_to_tag_pose, nt_config), distance) # type: ignore
                elif (error1 < (error0 * nt_config.error_ambiguity)):
                    camera_to_tag_pose = self._to_wpilib(tvecs[1], rvecs[1])
                    distance = camera_to_tag_pose.translation().norm() # type: ignore
                    return PoseEstimation([detection.id], self._to_robot_pose(camera_to_tag_pose, nt_config), distance) # type: ignore
                else:
                    return None

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

    def _is_outside_field(self, pose: Pose3d, nt_config: NTConfig) -> bool:
        if pose.X() < -nt_config.field_margin[0] or pose.Y() < -nt_config.field_margin[1] or pose.Z() < -nt_config.field_margin[2] or pose.X() > nt_config.field_size[0] + nt_config.field_margin[0]  or pose.Y() > nt_config.field_size[1] + nt_config.field_margin[1] or pose.Z() > nt_config.field_size[2] + nt_config.field_margin[2]: # type: ignore
            return True
        else:
            return False

    def _to_robot_pose(self, pose: Pose3d, nt_config: NTConfig) -> Pose3d:
        return pose.transformBy(Transform3d(Translation3d(nt_config.camera_position[0], nt_config.camera_position[1], nt_config.camera_position[2]), Rotation3d(nt_config.camera_position[3], nt_config.camera_position[4], nt_config.camera_position[5])).inverse())
