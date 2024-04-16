import sys

import loguru

from ats.globals import FN_OUT_LOG_FILE, DIR_OUT

# Constants
LOG_FORMAT = ('<green>{time:YYYY-MM-DD HH:mm:ss.SSS zz}</green> | '
              '<level>{level: <8}</level> | '
              '<yellow>Line {line: >4} ({file}):</yellow> '
              '<b>{message}</b>')
LOG_LEVEL = 'DEBUG'
LOG_ROTATION = '00:00'


class Logger:
    """
    Singleton to configure a loguru logger instance across the application.
    """
    _instance = None
    logger = None

    def __init__(self):
        """
        WARNING: Do not directly instantiate this class. Use the instance().
        """
        raise RuntimeError()

    @classmethod
    def instance(cls):
        """
        Provides a singleton instance of the Logger.
        :return: A loguru logger object configured as per the specified settings.
        """
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.initialize()
        # TODO: do not return the logger itself; instead, return the instance
        #  and route calls through this class
        return cls._instance.logger

    def initialize(self):
        """
        Initializes loguru, setting up the logging format, level, and file handling.
        Known improvement: Consider adding retention parameter for log files. Keeping logs for a specified time period.
        """
        self.logger = loguru.logger
        # Remove default handlers
        self.logger.remove()
        # Standard output logging
        self.logger.add(sys.stderr,
                        level=LOG_LEVEL,
                        format=LOG_FORMAT,
                        colorize=True,
                        backtrace=True,
                        diagnose=True)
        # TODO: add retention parameter when client has specified length
        self.logger.add(DIR_OUT + FN_OUT_LOG_FILE,
                        rotation=LOG_ROTATION,
                        level=LOG_LEVEL,
                        format=LOG_FORMAT,
                        colorize=False,
                        backtrace=True,
                        diagnose=True)
