class Process:
    """
    A class that represents the basic data model for a process

    This class is time and host agnostic
    """

    def __init__(self, process_name: str, process_arguments: str):
        self.process_name = process_name
        self.process_arguments = process_arguments

class ProcessEvent:
    """
    A class that represents the data model for Processes

    Processes will simulate the execution of legitimate and malicious processes on an endpoint.

    This functionality is not yet implemented
    """

    def __init__(self, timestamp: float, parent_process_name: str, parent_process_hash: str, process_arguments: str):

        self.timestamp = timestamp
        self.parent_process_name = parent_process_name
        self.parent_process_hash = parent_process_hash
        self.process_arguments = process_arguments

    def stringify(self):
        return {
            "timestamp": self.timestamp,
            "parent_process_name": self.parent_process_name,
            "parent_process_hash": self.parent_process_hash,
            "process_arguments": self.process_arguments
        }
