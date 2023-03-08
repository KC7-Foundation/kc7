import random
from app.server.modules.clock.Clock import Clock

class File:
    def __init__(self, filename:str, path:str, sha256:str=None, size:int=None):
        self.filename = filename
        self.path = path
        self.sha256 = sha256 or File.get_random_sha256()
        self.size = size or File.get_random_filesize()

        self.set_filepath()

    @staticmethod
    def get_random_sha256() -> str:
        """
        Helper function to get a random file hash (SHA256) when one is not provided
        """
        hash = random.getrandbits(256)
        return "%032x" % hash

    @staticmethod
    def get_random_filesize() -> int:
        """
        Helper function to get a random file size when one is not provided
        Returns an int in the range (1000, 9999)
        """
        return random.randint(1000, 9999)

    def set_filepath(self) -> None:
        if "." in self.path.split("\\")[-1]:
            return
        elif self.path[-1] == "\\":
            self.path = self.path+self.filename
            


class FileCreationEvent(File):

    def __init__(self, hostname: str, timestamp: float, filename: str, path: str, sha256: str=None, size:int=None):

        self.hostname = hostname
        self.timestamp = timestamp
        super().__init__(filename, path, sha256, size)

    def stringify(self) -> dict:
        return {
            "timestamp": Clock.from_timestamp_to_string(self.timestamp),
            "hostname": self.hostname,
            "sha256": self.sha256,
            "path": self.path.replace("/","\\"),
            "filename": self.filename
        }

    @staticmethod
    def get_kql_repr() -> tuple:
        """Returns table:str, columns:dict"""
        return (
            'FileCreationEvents',  # table name in KQL
            {                     # dict representation of column names:types
                'timestamp': 'datetime',
                'hostname': 'string',
                'sha256': 'string',
                'path': 'string',
                'filename': 'string'
            }
        )
