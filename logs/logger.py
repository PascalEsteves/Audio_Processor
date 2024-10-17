
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from enum import Enum

class LogLevel(Enum):
    """
    Enumerate to represent log levels
    """

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class NullLogger(logging.Logger):
    """
    Null logger to produce no visible output logging statements,
    but still fullfill logging.Logger interface.
    """

    def __init__(self):
        super().__init__("nulldummy")
        self.addHandler(logging.NullHandler())


class DualLogger(logging.Logger):
    """
    Logger to Audio Processor events to console and file
    """

    __default_log_dir = "Logs_audio_processor"

    def __init__(
        self,
        name: str = None,
        directory: str = None,
        console_log_level: LogLevel = LogLevel.INFO,
        file_log_level: LogLevel = LogLevel.INFO,
    ):
        """
        Initialize logger to log to specified log directory
        using a rotating daily file, and to print to stdout/stderr
        """
        self._name = name if name else "audio_processor"
        super().__init__(self._name)

        if directory:
            assert os.path.exists(directory)

            self._directory = directory
        else:
            logdir = os.path.join(os.getcwd(), DualLogger.__default_log_dir)
            if not os.path.exists(logdir):
                os.makedirs(logdir, exist_ok=True)

            self._directory = logdir

        logfile_name = os.path.join(self._directory, self._name) + ".log"
        file_log_handler = TimedRotatingFileHandler(
            logfile_name, when="midnight", interval=1, encoding="utf8"
        )
        file_log_handler.suffix = "%Y-%m-%d.log"
        file_log_handler.setLevel(file_log_level.value)
        self.addHandler(file_log_handler)


        console_log_handler = logging.StreamHandler()
        console_log_handler.setLevel(console_log_level.value)
        self.addHandler(console_log_handler)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_log_handler.setFormatter(formatter)
        console_log_handler.setFormatter(formatter)

    def shutdown(self):
        """
        Shutdown logger
        """
        logging.shutdown()
