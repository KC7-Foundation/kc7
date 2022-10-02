import random
from app.server.modules.clock.Clock import Clock


class FileCreationEvent:

    def __init__(self, hostname: str, timestamp: float, md5: str, path: str, size: int):

        self.hostname = hostname
        self.timestamp = timestamp
        self.md5 = md5
        self.path = path
        self.filename = self.path.split("\\")[-1] or ""
        self.size = size

    @staticmethod
    def get_random_hash() -> str:
        hash = random.getrandbits(128)
        return "%032x" % hash

    def stringify(self) -> dict:
        return {
            "timestamp": Clock.from_timestamp_to_string(self.timestamp),
            "hostname": self.hostname,
            "md5": self.md5,
            "path": self.path,
            "filename": self.filename,
            "size": self.size
        }

    @staticmethod
    def get_kql_repr() -> tuple:
        """Returns table:str, columns:dict"""
        return (
            'FileCreationEvents',  # table name in KQL
            {                     # dict representation of column names:types
                'timestamp': 'string',
                'hostname': 'string',
                'md5': 'string',
                'path': 'string',
                'filename': 'string',
                'size': 'int'
            }
        )
