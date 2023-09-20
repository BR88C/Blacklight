from dataclasses import dataclass, fields, MISSING
import json

@dataclass
class ConnectionConfig:
    name: str = ""
    nt_uri: str = ""
    video_port: int = 0

    def __post_init__(self):
        for field in fields(self):
            v = getattr(self, field.name)
            if v is None and not field.default_factory is MISSING:
                setattr(self, field.name, field.default_factory())

class ConnectionConfigLoader:
    FILENAME = "connection_config.json"

    def load(self) -> ConnectionConfig:
        config = ConnectionConfig()
        with open(self.FILENAME) as file:
            parsed_file = json.loads(file.read())
            config.name = parsed_file["name"]
            config.nt_uri = parsed_file["nt_uri"]
            config.video_port = parsed_file["video_port"]
        return config
