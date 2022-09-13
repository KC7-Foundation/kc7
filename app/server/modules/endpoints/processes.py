class Processes:
    """
    A class that represents the data model for Processes

    Processes will simulate the execution of legitimate and malicious processes on an endpoint.

    This functionality is not yet implemented
    """

    def __init__(self, creation_time: float, parent_process_name: str, parent_process_hash: str, process_arguments: str):

        self.creation_time = creation_time
        self.parent_process_name = parent_process_name
        self.parent_process_hash = parent_process_hash
        self.process_arguments = process_arguments

    def stringify(self):
        return {
            "creation_time": self.creation_time,
            "parent_process_name": self.parent_process_name,
            "parent_process_hash": self.parent_process_hash,
            "process_arguments": self.process_arguments
        }
