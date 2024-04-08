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
    _instance = None
    logger = None

    def __init__(self):
        raise RuntimeError()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.initialize()
        # TODO: do not return the logger itself; instead, return the instance
        #  and route calls through this class
        return cls._instance.logger

    def initialize(self):
        self.logger = loguru.logger
        self.logger.remove()
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
