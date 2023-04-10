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
    def validate_actor_yaml(config:dict):
        name =  config["name"]
        attacks = str(config["attacks"])
        required_keys = [
            "activity_start_date",
            "activity_end_date",
            "activity_start_hour",
            "workday_length_hours",
            "working_days"
        ]
        print(f"validating config for {config['name']}")
        # Ensure that certain pairs of keys are used together


        results = [True if key in config else False for key in required_keys]
        if not all(results):
            raise ValueError(f"For {name}: You must provide all the required keys: {str(required_keys)} ")
        if "malware" in attacks:
            if "malware" not in config.keys():
                raise ValueError(f"For {name}: You must provide a malware family is using a malware based attack")
            if "post_exploit_commands" not in config:
                print("We recommend providing post exploitation commands if you are using malware")
            if "file_names" not in config:
                raise ValueError(f"For {name}: You must provide file_names for email based attacks")
        if "email" in attacks:
            if  "sender_themes" not in config:
                raise ValueError(f"For {name}: You must provide sender_themes if using email attacks")
            if "subjects" not in config:
                raise ValueError(f"For {name}: You must provide subjects if using email attacks")
        if "recon" in attacks:
            if "recon_search_terms" not in config:
                raise ValueError(f"For {name}: You must provide recon_search_terms if you for actors that conduct recon")
        if "email" in attacks or "malware" in attacks or "phishing" in attacks:
            if "domain_themes" not in config:
                raise ValueError(f"For {name}: You must provide domain_themes for the attacks you have specified")
        if "domain_themes" in config:
            for domain in config["domain_themes"]:
                if " " in domain:
                    raise ValueError(f"For {name}: Domain themes must be singular terms. You cannot uses spaces or invalid characters, for term \"{domain}\"")
        if "watering_hole" in attacks:
            if "watering_hole_domains" not in config:
                raise ValueError(f"For {name}: You must provide watering_hole_domains to conduct a watering hole attack. This value should also be in your compnay config.")
            if "watering_hole_target_roles" not in config:
                print(f"For {name}: Consider adding watering_hole_target_roles to your actor config to refine your actor targeting")
        if "post_exploit_commands" in config:
            for command in config["post_exploit_commands"]:
                if "name" not in command.keys() or "process" not in command.keys():
                     raise ValueError(f"For {name}: Each post exploitation command must have both a name and process")
    with open(path, 'r', encoding="utf8") as stream:
        try:
            config = yaml.safe_load(stream)
            if config_type=="Actor":
                validate_actor_yaml(config)
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