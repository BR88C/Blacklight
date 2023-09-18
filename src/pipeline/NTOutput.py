import math
import ntcore
from typing import List, Union

from config.ConnectionConfig import ConnectionConfig
from pipeline.PoseEstimator import PoseEstimation

class NTOutput:
    _connection_config: ConnectionConfig
    _published: bool = False
    _fps: ntcore.IntegerPublisher
    _camera_pose_estimation: ntcore.DoubleArrayPublisher
    _debug_pose_estimation: ntcore.DoubleArrayPublisher

    def __init__(self, connection_config: ConnectionConfig) -> None:
        self._connection_config = connection_config

    def update(self, timestamp: float, fps: Union[int, None], camera_pose_estimation: Union[PoseEstimation, None], debug_pose_estimation: Union[PoseEstimation, None]) -> None:
        if not self._published:
            table = ntcore.NetworkTableInstance.getDefault().getTable("/" + self._connection_config.name + "/config")
            self._fps = table.getIntegerTopic("fps").publish()
            self._camera_pose_estimation = table.getDoubleArrayTopic("cameraPoseEstimation").publish()
            self._debug_pose_estimation = table.getDoubleArrayTopic("debugTagEstimation").publish()
            self._published = True

        if fps != None:
            self._fps.set(fps)
        else:
            self._fps.set(0)

        if camera_pose_estimation != None:
            array: List[float] = []

            array[0] = 1
            array.append(camera_pose_estimation.error_0)
            array.append(camera_pose_estimation.pose_0.translation().X()) # type: ignore
            array.append(camera_pose_estimation.pose_0.translation().Y()) # type: ignore
            array.append(camera_pose_estimation.pose_0.translation().Z()) # type: ignore
            array.append(camera_pose_estimation.pose_0.rotation().getQuaternion().W())
            array.append(camera_pose_estimation.pose_0.rotation().getQuaternion().X())
            array.append(camera_pose_estimation.pose_0.rotation().getQuaternion().Y())
            array.append(camera_pose_estimation.pose_0.rotation().getQuaternion().Z())

            if camera_pose_estimation.error_1 != None and camera_pose_estimation.pose_1 != None:
                array[0] = 2
                array.append(camera_pose_estimation.error_1)
                array.append(camera_pose_estimation.pose_1.translation().X()) # type: ignore
                array.append(camera_pose_estimation.pose_1.translation().Y()) # type: ignore
                array.append(camera_pose_estimation.pose_1.translation().Z()) # type: ignore
                array.append(camera_pose_estimation.pose_1.rotation().getQuaternion().W())
                array.append(camera_pose_estimation.pose_1.rotation().getQuaternion().X())
                array.append(camera_pose_estimation.pose_1.rotation().getQuaternion().Y())
                array.append(camera_pose_estimation.pose_1.rotation().getQuaternion().Z())

            for id in camera_pose_estimation.ids:
                array.append(id)

            self._camera_pose_estimation.set(array, math.floor(timestamp * 1000000))
        else:
            self._camera_pose_estimation.set([0], math.floor(timestamp * 1000000))

        if debug_pose_estimation != None:
            array: List[float] = [
                debug_pose_estimation.error_0,
                debug_pose_estimation.pose_0.translation().X(), # type: ignore
                debug_pose_estimation.pose_0.translation().Y(), # type: ignore
                debug_pose_estimation.pose_0.translation().Z(), # type: ignore
                debug_pose_estimation.pose_0.rotation().getQuaternion().W(),
                debug_pose_estimation.pose_0.rotation().getQuaternion().X(),
                debug_pose_estimation.pose_0.rotation().getQuaternion().Y(),
                debug_pose_estimation.pose_0.rotation().getQuaternion().Z(),
            ]

            if debug_pose_estimation.error_1 != None and debug_pose_estimation.pose_1 != None:
                array.append(debug_pose_estimation.error_1)
                array.append(debug_pose_estimation.pose_1.translation().X()) # type: ignore
                array.append(debug_pose_estimation.pose_1.translation().Y()) # type: ignore
                array.append(debug_pose_estimation.pose_1.translation().Z()) # type: ignore
                array.append(debug_pose_estimation.pose_1.rotation().getQuaternion().W())
                array.append(debug_pose_estimation.pose_1.rotation().getQuaternion().X())
                array.append(debug_pose_estimation.pose_1.rotation().getQuaternion().Y())
                array.append(debug_pose_estimation.pose_1.rotation().getQuaternion().Z())

            self._debug_pose_estimation.set(array, math.floor(timestamp * 1000000))
        else:
            self._debug_pose_estimation.set([], math.floor(timestamp * 1000000))
