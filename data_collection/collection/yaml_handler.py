import yaml
import errno
import os


class YamlHandler:
    # Load yaml configuration file
    @staticmethod
    def load_config(config_path: str):
        try:
            config_file = open(config_path, "r")
            config = yaml.safe_load(config_file)
            config_file.close()
            return config
        except IOError:  # TODO Implement logging system
            print(f"IOError while querying config at path: {config_path}")
            exit(-1001)  # Exit program with code -1001 (Invalid config path)
        except yaml.YAMLError:
            print(yaml.YAMLError)
            exit(-1003)  # Exit program with code -1003 (YAML error)

    # Write yaml configuration file
    @staticmethod
    def write_files(yaml_data, output_folder: str, filename: str):
        output_dir = output_folder
        # Create output directory if not found
        if not os.path.exists(os.path.dirname(output_dir)):
            try:
                os.makedirs(os.path.dirname(output_dir))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise

        with open(output_folder + "/" + filename, "w") as outfile:
            yaml.dump_all(yaml_data, outfile, indent=2)
