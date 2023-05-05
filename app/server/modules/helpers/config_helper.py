import yaml 
import glob

from app.server.modules.file.malware import Malware

        
def read_list_from_file(path) -> list:
    """
    Reads data from a .txt file and returns it as a list
    """
    with open(path, "r") as file:
        lines = file.readlines()
    return [line.strip() for line in lines]


def read_config_from_yaml(path, config_type=None) -> dict:
    """
    Read config from file.
    Return a json representation of the yaml file 
    """
    actor_requirements_file_path = "app/static_configs/actor_validator.yaml"
    malware_requirements_file_path = "app/static_configs/malware_validator.yaml"
    company_requirements_file_path = "app/static_configs/company_validator.yaml"

    def validate_yaml(config, requirements_file_path):
        # Load the config file

        # Load the requirements file
        with open(requirements_file_path, 'r') as f:
            requirements = yaml.safe_load(f)
        
        # Check for mandatory keys
        for key in requirements['mandatory']:
            if key not in config:
                raise ValueError(f"Missing mandatory key: {key}")
        
        # Check for optional keys
        for key, required_key in requirements['optional'].items():
            if required_key in config and key not in config:
                raise ValueError(f"You must provide the key \"{key}\" if you are using the key \"{required_key}\"")
        
        # Check for keys required based on the value of other keys
        for key, required_keys in requirements.get('conditional', {}).items():
            if key not in config:
                continue
            value = config[key]
            # If the value matches one of the required values, check for the required keys
            if value in required_keys:
                for required_key in required_keys[value]:
                    if required_key not in config:
                        raise ValueError(f"Missing key '{required_key}' required by '{key}'='{value}'")


        # # Check for keys with defined formats
        # for key, format_str in requirements['format'].items():
        #     if key in config:
        #         value = config[key]
        #         if not isinstance(value, str) or not format_str.format(value):
        #             raise ValueError(f"Invalid value format for key '{key}': {value}")
        

    with open(path, 'r', encoding="utf8") as stream:
        try:
            config = yaml.safe_load(stream)
            if config_type=="Actor":
                validate_yaml(config, requirements_file_path=actor_requirements_file_path)
            elif config_type=="Malware":
                validate_yaml(config, requirements_file_path=malware_requirements_file_path)
            elif config_type=="Company":
                validate_yaml(config, requirements_file_path=company_requirements_file_path)
            return config

        except yaml.YAMLError as exc:
            raise ValueError(f"Looks like you provided invalid yaml {exc}")


def load_malware_obj_from_yaml(malware_name) -> Malware:
    """
    Given a malware name, look for a malware config yaml file with that corresponding name
    Use the malware config to build a Malware obj
    return the Malware object
    """
    malware_config = glob.glob(f"app/game_configs/malware/{malware_name}.yaml")[0]
    # Read all malware configs from YAML config files
    malware_config_as_json = read_config_from_yaml(malware_config, config_type="Malware")
    if malware_config_as_json:
        return Malware(
                    **malware_config_as_json
                )
    else:
        return None

def load_malware_obj_from_yaml_by_file(yaml_file) -> Malware:
    """
    Given a malware name, look for a malware config yaml file with that corresponding name
    Use the malware config to build a Malware obj
    return the Malware object
    """
    # Read all malware configs from YAML config files
    malware_config_as_json = read_config_from_yaml(yaml_file, config_type="Malware")
    if malware_config_as_json:
        return Malware(
                    **malware_config_as_json
                )
    else:
        return None