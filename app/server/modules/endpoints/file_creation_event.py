import random
import os
from app.server.modules.clock.Clock import Clock

class File:
    def __init__(self, filename:str, path:str, sha256:str=None, size:int=None):
        #TODO: autoparse the filename from the path
        self.filename = filename
        # path does not include filname
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
        elif self.path and self.path[-1] == "\\":
            self.path = self.path+self.filename
            


class FileCreationEvent(File):

    def __init__(self, hostname: str, timestamp: float, filename:str, path: str, username: str, sha256: str=None, process_name: str=None, size:int=None):
        super().__init__(filename, path, sha256, size)
        self.hostname = hostname
        self.timestamp = timestamp
        self.process_name = process_name or self.get_process_name()
        self.username = username
        

    def get_process_name(self) -> None:
        if ".doc" in self.path:
            process_name = "winword.exe"
        elif ".ppt" in self.path:
            process_name = "ppt.exe"
        elif ".xls" in self.path:
            process_name = "excel.exe"
        elif ".zip" in self.path:
           process_name = "7zip.exe"
        elif ".rar" in self.path:
            process_name = "winrar.exe"
        else:
            process_name = "explorer.exe"

        return process_name


    def stringify(self) -> dict:
        return {
            "timestamp": Clock.from_timestamp_to_string(self.timestamp),
            "hostname": self.hostname,
            "username": self.username,
            "sha256": self.sha256,
            "path": self.path.replace("/","\\"),
            "filename": self.filename,
            "process_name": self.process_name
        }

    @staticmethod
    def get_kql_repr() -> tuple:
        """Returns table:str, columns:dict"""
        return (
            'FileCreationEvents',  # table name in KQL
            {                     # dict representation of column names:types
                'timestamp': 'datetime',
                'hostname': 'string',
                'username':'string',
                'sha256': 'string',
                'path': 'string',
                'filename': 'string',
                "process_name": 'string'
            }
        )
