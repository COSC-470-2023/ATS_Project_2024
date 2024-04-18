import errno
import json
import os

import yaml

from ats import globals
from ats.logger import Logger

logger = Logger.instance()


def read_json(filename: str) -> list[dict]:
    """
    Reads a JSON file and returns it as a list of dictionaries.
    :param filename: Name of the file to be read.
    :return: List of dictionaries containing the data from the JSON file.
    :raises SystemExit: Exits if the file cannot be read or if the JSON decoding fails.
    """
    path = globals.DIR_OUT + filename
    try:
        with open(path, 'r') as file:
            data = json.load(file)
        return data
    except IOError:
        logger.critical(f"IOError while query config at path: {path}")
        exit(-1001)  # Exit program with code -1001 (Invalid config path)
    except json.JSONDecodeError as e:
        logger.critical(f"JSON decoding encountered an error while decoding {path}:\n{e}")
        exit(-1002)  # Exit program with code -1002 (Invalid config structure)


def read_yaml(filename: str) -> dict:
    """
    Reads a YAML file and returns it as a dictionary.
    :param filename: Name of the file to be read.
    :return: Dictionary containing the data from the YAML file.
    :raises SystemExit: Exits if the file cannot be read or if there is a YAML parsing error.
    """
    path = globals.DIR_CFG + filename
    try:
        with open(path, 'r') as file:
            data = yaml.safe_load(file)
        return data
    except IOError:
        logger.critical(f"IOError while querying config at path: {path}")
        exit(-1001)  # Exit program with code -1001 (Invalid config path)
    except yaml.YAMLError:
        logger.critical(yaml.YAMLError)
        exit(-1003)  # Exit program with code -1003 (YAML error)


def write_json(data: list[dict], filename: str):
    """
    Writes a list of dictionaries to a JSON file.
    :param data: The data to write.
    :param filename: The name of the target file.
    """
    if not os.path.exists(os.path.dirname(globals.DIR_OUT)):
        try:
            os.makedirs(os.path.dirname(globals.DIR_OUT))
        except OSError as e:  # Guard against race condition
            if e.errno != errno.EEXIST:
                raise
    path = globals.DIR_OUT + filename
    with open(path, 'w') as file:
        json.dump(data, file, indent=2)


def write_yaml(data: dict, filename: str):
    """
    Writes a list of dictionaries to a YAML file.
    :param data: The data to write.
    :param filename: The name of the target file.
    """
    if not os.path.exists(os.path.dirname(globals.DIR_CFG)):
        try:
            os.makedirs(os.path.dirname(globals.DIR_CFG))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    path = globals.DIR_CFG + filename
    with open(path, 'w') as file:
        yaml.dump(data, file, indent=2)
