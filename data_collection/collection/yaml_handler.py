import yaml
import errno
import os
import sys

from dev_tools import loguru_init

# Loguru init
logger = loguru_init.initialize()

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
def yaml_write_config(yaml_data, output_folder: str, filename: str):
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
