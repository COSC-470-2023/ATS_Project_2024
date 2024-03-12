import sys

from loguru import logger


# Loguru initialization
def initialize():
    logger.remove()
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS zz}</green> | <level>{level: <8}</level> | <yellow>Line {line: >4} "
        "({file}):</yellow> <b>{message}</b>")
    logger.add(sys.stderr, level="DEBUG", format=log_format, colorize=True, backtrace=True, diagnose=True)
    # TODO add retention parameter to loggers when client has specified length
    logger.add("log_file.log", rotation='00:00', level="DEBUG", format=log_format, colorize=False, backtrace=True,
               diagnose=True)
    return logger
