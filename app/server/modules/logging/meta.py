class DebugLogger:
    def __init__(self, log_directory="testlogs/"):
        self.log_file_path = log_directory + "/ishouldnotbehere.txt"
        self.file_handler = open(self.log_file_path, "a")

    def log_debug(self, message, log_file_path=None):
        if log_file_path:
            self.log_file_path = log_file_path
            self.file_handler.close()
            self.file_handler = open(self.log_file_path, "a")
        self.file_handler.write(message + "\n")