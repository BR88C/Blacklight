"""
An AprilTag detection pipeline using OpenCV's ArUco module.
Copyright (C) 2023 Team 340

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

Portions of this work are derived from Team 6328's "Northstar",
which is licensed under the GNU General Public License, version 3.
Source for the original work can be found at the following URL:
<https://github.com/Mechanical-Advantage/AdvantageKit/tree/ns-dev/akit/py/northstar>

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import ntcore
import time

from config.CalibrationConfig import CalibrationConfigLoader
from config.ConnectionConfig import ConnectionConfigLoader
from config.NTConfig import NTConfig, NTConfigUpdater
from pipeline.ApriltagDetector import ApriltagDetector
from pipeline.Camera import Camera
from pipeline.NTOutput import NTOutput
from pipeline.PoseEstimator import PoseEstimator
from pipeline.StreamOutput import StreamOutput

if __name__ == "__main__":
    calibration_config_loader = CalibrationConfigLoader()

    connection_config = ConnectionConfigLoader().load()
    print("Loaded connection config")
    calibration_config = calibration_config_loader.load()
    print("Loaded calibration config")
    nt_config = NTConfig()
    print("Generated NT config")

    nt_config_updater = NTConfigUpdater(connection_config)
    camera = Camera()
    apriltag_detector = ApriltagDetector()
    pose_estimator = PoseEstimator()
    nt_output = NTOutput(connection_config)
    stream_output = StreamOutput()

    ntcore.NetworkTableInstance.getDefault().setServer(connection_config.nt_uri)
    ntcore.NetworkTableInstance.getDefault().startClient4(connection_config.name)
    print("Started NT Client")

    stream_output.start_server(connection_config)
    print("Started stream server")

    fps = 0
    frames = 0
    last_frame_print = 0
    while True:
        nt_config_updater.update(nt_config)

        timestamp = time.time()
        cam_success, capture = camera.read(nt_config)

        if not cam_success:
            print("Unable to capture frame")
            time.sleep(0.5)
            continue

        frames += 1
        if timestamp - last_frame_print > 1:
            fps = frames
            frames = 0
            print("Pipeline running at " + str(fps) + " fps")
            last_frame_print = timestamp

        if len(calibration_config.distortion_coefficients) > 0 and len(calibration_config.distortion_matrix) > 0:
            detections = apriltag_detector.search(capture, nt_config)
            pose_estimation = pose_estimator.get_estimated_pose(detections, calibration_config, nt_config)
            debug_pose_estimation = pose_estimator.get_estimated_debug_pose(detections, calibration_config, nt_config)
            nt_output.update(timestamp, fps, pose_estimation, debug_pose_estimation)
        else:
            print("No calibration found")
            time.sleep(0.5)

        stream_output.update(capture)
