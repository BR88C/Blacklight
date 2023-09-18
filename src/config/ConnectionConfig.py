from dataclasses import dataclass
import json

@dataclass
class ConnectionConfig:
    name: str = ""
    nt_uri: str = ""
    video_port: int = 0

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
