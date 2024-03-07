import json
import errno
import os
import sys

from dev_tools import loguru_init

# Loguru init
logger = loguru_init.initialize()

def json_load_config(config_path: str):
    """
    Attempts to load the config file specified.
    Exits with -1001 if config path is invalid.
    Exits with -1002 if config json is invalid structure
    :param config_path: A string containing the filename and path for the configuration file
    :return: config json from using json.load
    """
    try:
        config_file = open(config_path, "r")
        config = json.load(config_file)
        config_file.close()
        return config
    except IOError:
        logger.critical(f"IOError while query config at path: {config_path}")
        exit(-1001)  # Exit program with code -1001 (Invalid config path)
    except json.JSONDecodeError as e:
        logger.critical(f"JSON decoding encountered an error while decoding {config_path}:\n{e}")
        exit(-1002)  # Exit program with code -1002 (Invalid config structure)


def json_write_files(json_data, output_folder: str, filename: str):
    """
    Attempts to write the json_data to the output_folder using filename.
    :param json_data: Json Data, either list, dict etc.
    :param output_folder: The folder path for output. ie "../output"
    :param filename: The file name to be written
    """
    output_dir = output_folder
    if not os.path.exists(os.path.dirname(output_dir)):
        try:
            os.makedirs(os.path.dirname(output_dir))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(output_folder + "/" + filename, "w") as outfile:
        json.dump(json_data, outfile, indent=2)
