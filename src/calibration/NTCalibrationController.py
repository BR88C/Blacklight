import ntcore
from typing import Optional

from config.ConnectionConfig import ConnectionConfig

class NTCalibrationController:
    _connection_config: ConnectionConfig
    _table: ntcore.NetworkTable
    _calibrating: Optional[ntcore.BooleanSubscriber] = None
    _snap: Optional[ntcore.BooleanSubscriber] = None
    _last_snap = False

    def __init__(self, connection_config: ConnectionConfig) -> None:
        self._connection_config = connection_config
        self._table = ntcore.NetworkTableInstance.getDefault().getTable("/" + self._connection_config.name + "/calibration")

    def is_calibrating (self) -> bool:
        if self._calibrating == None:
            self._calibrating = self._table.getBooleanTopic("calibrating").subscribe(False)

        return self._calibrating.get()

    def should_snap (self) -> bool:
        if self._snap == None:
            self._snap = self._table.getBooleanTopic("snap").subscribe(False)

        snap = self._snap.get()
        if self._last_snap and snap:
            return False
        elif self._last_snap and not snap:
            self._last_snap = False
            return False
        elif not self._last_snap and snap:
            self._last_snap = True
            return True
        else:
            return False
