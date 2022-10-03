import yaml 

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