import random
from app.server.modules.clock.Clock import Clock


class FileCreationEvent:

    def __init__(self, hostname: str, creation_time: float, md5: str, path: str, size: int):

        self.hostname = hostname
        self.creation_time = creation_time
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
            "creation_time": Clock.from_timestamp_to_string(self.creation_time),
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
                'creation_time': 'string',
                'hostname': 'string',
                'md5': 'string',
                'path': 'string',
                'filename': 'string',
                'size': 'int'
            }
        )
