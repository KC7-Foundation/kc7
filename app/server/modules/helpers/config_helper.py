import yaml 
import glob

from app.server.modules.file.malware import Malware

def read_config_from_yaml(path) -> dict:
    """
    Read config from file.
    Return a json representation of the yaml file 
    """
    with open(path, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            return None
            print(exc)

def load_malware_obj_from_yaml(malware_name) -> Malware:
    """
    Given a malware name, look for a malware config yaml file with that corresponding name
    Use the malware config to build a Malware obj
    return the Malware object
    """
    malware_config = glob.glob(f"app/game_configs/malware/{malware_name}.yaml")[0]
    # Read all malware configs from YAML config files
    malware_config_as_json = read_config_from_yaml(malware_config)
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
    malware_config_as_json = read_config_from_yaml(yaml_file)
    if malware_config_as_json:
        return Malware(
                    **malware_config_as_json
                )
    else:
        return None