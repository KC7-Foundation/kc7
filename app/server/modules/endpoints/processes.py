import re
from app.server.modules.clock.Clock import Clock
from app.server.modules.endpoints.file_creation_event import File

class Process:
    """
    A class that represents the basic data model for a process

    This class is time and host agnostic
    """

    def __init__(self, process_commandline: str, process_name: str=None, process_hash: str = None):
        self.process_commandline = process_commandline
        self.process_name = process_name or self.parse_process_name()   #parse out the process name if not given
        self.process_hash = process_hash or File.get_random_sha256()

    def parse_process_name(self):
        """Parse out the processname from the command"""
        # Split the command line into individual arguments
        args = self.process_commandline.split()

        # Check if the command line starts with a process name
        if len(args) > 0:
            process_name = args[0]

            # Remove any path and extract the process name
            process_name = process_name.split("/")[-1]
            process_name = process_name.split("\\")[-1]

            # Remove any quotes around the process name
            process_name = re.sub(r'^"|"$', '', process_name)

            # Check if the process name ends with '.exe' and add it if not
            if not process_name.endswith('.exe'):
                process_name += '.exe'

            return process_name

        return ""

class ProcessEvent(Process):
    """
    A class that represents the data model for Processes
    timestamp is the in-game time when the process is created
    parent_process_name is the name of the initiating process or file
    parent_process_hash is the hash of the initiating process or file
    process_commandline is the commandline parameters associated with the created process
    process_name is the name of the created process
    process_hash is the hash of the created process
    hostname is the name of the machine on which these processes occur

    Processes will simulate the execution of legitimate and malicious processes on an endpoint.

    This functionality is not yet implemented
    """

    def __init__(self,
                timestamp: float,
                parent_process_name: str,
                parent_process_hash: str,
                process_commandline: str,
                process_name: str,
                hostname: str,
                username: str,
                process_hash: str = None):

        self.timestamp = timestamp
        self.parent_process_name = parent_process_name 
        self.parent_process_hash = parent_process_hash 
        self.hostname = hostname
        self.username = username
        super().__init__(process_name, process_commandline, process_hash)

    def stringify(self):
        return {
            "timestamp": Clock.from_timestamp_to_string(self.timestamp),
            "parent_process_name": self.parent_process_name,
            "parent_process_hash": self.parent_process_hash,
            "process_commandline": self.process_commandline,
            "process_name": self.process_name,
            "process_hash": self.process_hash,
            "hostname": self.hostname,
            "username": self.username
        }

    def get_kql_repr():
        return (
            "ProcessEvents",
            {
                "timestamp":"datetime",
                "parent_process_name":"string",
                "parent_process_hash":"string",
                "process_commandline":"string",
                "process_name":"string",
                "process_hash":"string",
                "hostname":"string",
                "username":"string"
            }
        )
