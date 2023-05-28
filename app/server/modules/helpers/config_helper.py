import yaml 
import json
import glob

from app.server.modules.file.malware import Malware

        
def read_list_from_file(path) -> list:
    """
    Reads data from a .txt file and returns it as a list
    """
    with open(path, "r") as file:
        lines = file.readlines()
    return [line.strip() for line in lines]


def validate_yaml(config, config_type, show_errors=False):
    """
    Given one yaml file that defines what keys/value should appear in a given config type
    Validate a config

    Configs error are show in the view @ http://127.0.0.1:8889/config
    OR they are raised in the data generator is executed
    """
    actor_requirements_file_path = "app/static_configs/actor_validator.yaml"
    malware_requirements_file_path = "app/static_configs/malware_validator.yaml"
    company_requirements_file_path = "app/static_configs/company_validator.yaml"
    
    # Load the config file
    if config_type=="Actor":
        requirements_file_path=actor_requirements_file_path
    elif config_type=="Malware":
        requirements_file_path=malware_requirements_file_path
    elif config_type=="Company":
        requirements_file_path=company_requirements_file_path

    # Load the requirements file
    with open(requirements_file_path, 'r') as f:
        validator = yaml.safe_load(f)

    errors = []
    new_line = '\n\t\t-'

    # Check mandatory keys
    mandatory_keys = validator.get('mandatory', [])
    missing_keys = [key for key in mandatory_keys if key not in get_all_keys(config)]
    # print(json.dumps(flatten_dict(config), indent=4))
    if missing_keys:
        errors.append(f"Error: The following mandatory keys are missing in the config: {new_line} {new_line.join(missing_keys)}")

    # Check conditional keys
    conditional_keys = validator.get('conditional', {})
    for parent_key, child_keys in conditional_keys.items():
        parent_keys = parent_key.split(':')
        parent_exists = nested_key_exists(config, parent_keys)
        if parent_exists:
            for child_key in child_keys:
                child_keys = child_key.split(':')
                child_exists = nested_key_exists(config, parent_keys + child_keys)
                if not child_exists:
                    errors.append(f"Error: The key '{':'.join(parent_keys + child_keys)}' is missing in the config "
                          f"given that '{':'.join(parent_keys)}' is present.")

    if errors:
        error_message= f"Found the following config errors for config: \n" + "\n\t-> " + "\n\t-> ".join(errors)
        if show_errors:
            return error_message
        else:
            raise ValueError(error_message)
    else:
        return "No errors to report"



def get_all_keys(dictionary):
    keys = set()

    def extract_keys(d):
        if isinstance(d, dict):
            for key, value in d.items():
                keys.add(key)
                extract_keys(value)
        elif isinstance(d, list):
            for item in d:
                extract_keys(item)

    extract_keys(dictionary)
    return keys


def nested_key_exists(dictionary, keys):
    for key in keys:
        if key not in dictionary:
            return False
        dictionary = dictionary[key]
    return True



def abstract_outer_keys(data):
    new_dictionary = {}
    for key, value in data.items():
        if isinstance(value, dict):
            new_dictionary.update(value)
        else:
            new_dictionary[key] = value
    return new_dictionary


def read_config_from_yaml(path, config_type=None, load_actor_class=False) -> dict:
    """
    Read config from file.
    Return a json representation of the yaml file 

    load_actor_class -> Removes the outtermost keys so we can use the config to loads a SQlAlchemy class
    """
    with open(path, 'r', encoding="utf8") as stream:
        try:
            config = yaml.safe_load(stream)
            if config_type:
                validate_yaml(config, config_type=config_type)
            if "metadata" in config.keys() and load_actor_class:
                # remove the outer most keys
                # these keys are just used to help orgnize the data
                config = abstract_outer_keys(config)
                # print(config)
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