from dataclasses import dataclass
import json
import ntcore
from typing import List

from config.ConnectionConfig import ConnectionConfig

@dataclass
class NTConfigTag:
    id: int
    x: float
    y: float
    z: float
    rx: float
    ry: float
    rz: float

@dataclass
class NTConfig:
    device_path: str
    height: int
    width: int 
    auto_exposure: int
    absolute_exposure: int
    gain: int
    camera_position: List[float]
    error_ambiguity: float
    tag_size: float
    tag_family: str
    tag_layout: List[NTConfigTag]
    debug_tag: int
    field_size: List[float]
    field_margin: List[float]

def generate_default() -> NTConfig:
    return NTConfig(
        device_path = "/dev/video0",
        height = 1200,
        width = 1600,
        auto_exposure = 1,
        absolute_exposure = 10,
        gain = 25,
        camera_position = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        error_ambiguity = 0.15,
        tag_size = 0.1524,
        tag_family = "16h5",
        tag_layout = [],
        debug_tag = 9,
        field_size = [16.5417, 8.0136, 0.0],
        field_margin = [0.5, 0.5, 0.75]
    )

class NTConfigUpdater:
    _connection_config: ConnectionConfig
    _subbed: bool = False
    _device_path: ntcore.StringSubscriber
    _height: ntcore.IntegerSubscriber
    _width: ntcore.IntegerSubscriber
    _auto_exposure: ntcore.IntegerSubscriber
    _absolute_exposure: ntcore.IntegerSubscriber
    _gain: ntcore.IntegerSubscriber
    _camera_position: ntcore.DoubleArraySubscriber
    _error_ambiguity: ntcore.DoubleSubscriber
    _tag_size: ntcore.DoubleSubscriber
    _tag_family: ntcore.StringSubscriber
    _tag_layout: ntcore.StringSubscriber
    _debug_tag: ntcore.IntegerSubscriber
    _field_size: ntcore.DoubleArraySubscriber
    _field_margin: ntcore.DoubleArraySubscriber

    def __init__(self, connection_config: ConnectionConfig) -> None:
        self._connection_config = connection_config

    def update(self, nt_config: NTConfig) -> None:
        if not self._subbed:
            table = ntcore.NetworkTableInstance.getDefault().getTable("/Blacklight-" + self._connection_config.name + "/config")
            self._device_path = table.getStringTopic("devicePath").subscribe(nt_config.device_path)
            self._height = table.getIntegerTopic("height").subscribe(nt_config.height)
            self._width = table.getIntegerTopic("width").subscribe(nt_config.width)
            self._auto_exposure = table.getIntegerTopic("autoExposure").subscribe(nt_config.auto_exposure)
            self._absolute_exposure = table.getIntegerTopic("absoluteExposure").subscribe(nt_config.absolute_exposure)
            self._gain = table.getIntegerTopic("gain").subscribe(nt_config.gain)
            self._camera_position = table.getDoubleArrayTopic("cameraPosition").subscribe(nt_config.camera_position)
            self._error_ambiguity = table.getDoubleTopic("errorAmbiguity").subscribe(nt_config.error_ambiguity)
            self._tag_size = table.getDoubleTopic("tagSize").subscribe(nt_config.tag_size)
            self._tag_family = table.getStringTopic("tagFamily").subscribe(nt_config.tag_family)
            self._tag_layout = table.getStringTopic("tagLayout").subscribe(json.dumps(nt_config.tag_layout))
            self._debug_tag = table.getIntegerTopic("debugTag").subscribe(nt_config.debug_tag)
            self._field_size = table.getDoubleArrayTopic("fieldSize").subscribe(nt_config.field_size)
            self._field_margin = table.getDoubleArrayTopic("fieldMargin").subscribe(nt_config.field_margin)
            self._subbed = True

        nt_config.device_path = self._device_path.get()
        nt_config.height = self._height.get()
        nt_config.width = self._width.get()
        nt_config.auto_exposure = self._auto_exposure.get()
        nt_config.absolute_exposure = self._absolute_exposure.get()
        nt_config.gain = self._gain.get()
        nt_config.camera_position = self._camera_position.get()
        nt_config.error_ambiguity = self._error_ambiguity.get()
        nt_config.tag_size = self._tag_size.get()
        nt_config.tag_family = self._tag_family.get()
        try:
            nt_config.tag_layout = json.loads(self._tag_layout.get())
        except:
            nt_config.tag_layout = []
        nt_config.debug_tag = self._debug_tag.get()
        nt_config.field_size = self._field_size.get()
        nt_config.field_margin = self._field_margin.get()
