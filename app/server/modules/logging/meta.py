import logging

class DebugLogger:
    def __init__(self, log_file_path):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.file_handler = logging.FileHandler(log_file_path)
        self.file_handler.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(message)s')
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def log_debug(self, message):
        self.logger.debug(message)

# debug_logger = DebugLogger('/path/to/logfile.log')
# debug_logger.log_debug('This is a debug message.')