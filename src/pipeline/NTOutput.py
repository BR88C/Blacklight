import math
import ntcore
from typing import List, Optional

from config.ConnectionConfig import ConnectionConfig
from pipeline.PoseEstimator import PoseEstimation

class NTOutput:
    _connection_config: ConnectionConfig
    _published: bool = False
    _fps: ntcore.IntegerPublisher
    _pose_estimation: ntcore.DoubleArrayPublisher
    _debug_pose_estimation: ntcore.DoubleArrayPublisher

    def __init__(self, connection_config: ConnectionConfig) -> None:
        self._connection_config = connection_config

    def update(self, timestamp: float, fps: int, pose_estimation: Optional[PoseEstimation], debug_pose_estimation: Optional[PoseEstimation]) -> None:
        if not self._published:
            table = ntcore.NetworkTableInstance.getDefault().getTable("/Blacklight-" + self._connection_config.name + "/output")
            self._fps = table.getIntegerTopic("fps").publish()
            self._pose_estimation = table.getDoubleArrayTopic("poseEstimation").publish()
            self._debug_pose_estimation = table.getDoubleArrayTopic("debugPoseEstimation").publish()
            self._published = True

        self._fps.set(fps)

        if pose_estimation != None:
            array: List[float] = [
                pose_estimation.pose.translation().X(), # type: ignore
                pose_estimation.pose.translation().Y(), # type: ignore
                pose_estimation.pose.translation().Z(), # type: ignore
                pose_estimation.pose.rotation().X(), # type: ignore
                pose_estimation.pose.rotation().Y(), # type: ignore
                pose_estimation.pose.rotation().Z() # type: ignore
            ]

            for id in pose_estimation.ids:
                array.append(id)

            self._pose_estimation.set(array, math.floor(timestamp * 1000000))
        else:
            self._pose_estimation.set([0], math.floor(timestamp * 1000000))

        if debug_pose_estimation != None:
            self._debug_pose_estimation.set([
                debug_pose_estimation.pose.translation().X(), # type: ignore
                debug_pose_estimation.pose.translation().Y(), # type: ignore
                debug_pose_estimation.pose.translation().Z(), # type: ignore
                debug_pose_estimation.pose.rotation().X(), # type: ignore
                debug_pose_estimation.pose.rotation().Y(), # type: ignore
                debug_pose_estimation.pose.rotation().Z() # type: ignore
            ], math.floor(timestamp * 1000000))
        else:
            self._debug_pose_estimation.set([], math.floor(timestamp * 1000000))
