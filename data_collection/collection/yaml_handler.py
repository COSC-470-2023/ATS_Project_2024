import yaml
import errno
import os
import sys

from loguru import logger

# Loguru init
logger.remove()
log_format = ("<green>{time:YYYY-MM-DD HH:mm:ss.SSS zz}</green> | <level>{level: <8}</level> | <yellow>Line {line: >4} "
              "({file}):</yellow> <b>{message}</b>")
logger.add(sys.stderr, level="DEBUG", format=log_format, colorize=True, backtrace=True, diagnose=True)
# TODO add retention parameter to loggers when client has specified length
logger.add("log_file.log", rotation='00:00', level="CRITICAL", format=log_format, colorize=False, backtrace=True,
           diagnose=True, backup=5)


# Load yaml configuration file
def yaml_load_config(config_path: str):
    try:
        config_file = open(config_path, "r")
        config = yaml.safe_load(config_file)
        config_file.close()
        return config
    except IOError:
        logger.critical(f"IOError while querying config at path: {config_path}")
        exit(-1001)  # Exit program with code -1001 (Invalid config path)
    except yaml.YAMLError:
        logger.critical(yaml.YAMLError)
        exit(-1003)  # Exit program with code -1003 (YAML error)


# Write yaml configuration file
def yaml_write_files(yaml_data, output_folder: str, filename: str):
    output_dir = output_folder
    # Create output directory if not found
    if not os.path.exists(os.path.dirname(output_dir)):
        try:
            os.makedirs(os.path.dirname(output_dir))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    with open(output_folder + "/" + filename, "w") as outfile:
        yaml.dump(yaml_data, outfile, indent=2)