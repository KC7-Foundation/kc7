import os
from app.server.modules.clock.Clock import Clock

class Actions:
    """
    Run functions based on key value paird from configs
    """

    @staticmethod
    def load_mitre_technique(mitre_technique, env_vars) -> None:
        """
        Given a mitre technique e.g. T1560
        Load the corresponding technique yaml
        Then randomly select an available subtechnique and method of running that subtechnique 
        """
        from app.server.modules.helpers.config_helper import read_config_from_yaml

        def find_yaml_file(folder_path, file_name):
            for root, dirs, files in os.walk(folder_path):
                if file_name in files:
                    return os.path.join(root, file_name)
            return None

        # use the mitre technique id to find the corresponding file
        # e.g. T1560 -> app/static_configs/mitre_configs/10-exfiltration/T1560.yaml
        folder_path = f"app/static_configs/mitre_configs/"
        filename = mitre_technique + ".yaml"
        file_path = find_yaml_file(folder_path, filename)

        # read in the file
        if file_path:
            technique_config = read_config_from_yaml(file_path)

        # a method is a bundle of actions
        # get the action
        actions = Actions.get_actions(technique_config)
        for action in actions:
            for action_name, args  in action.items():
                Actions.execute_action(action_name, args, env_vars)


    @staticmethod
    def get_actions(dict_config) -> list:
        """
        Give a mitre static configuration
        Choose and subtechnique and method
        Return the actions under that method
        """
        import random 
        #TODO: Make this more dependent
        subtechniques = dict_config["Subtechniques"]
        # choose ad technique e.g. T1560.001
        subtechnique = random.choice(subtechniques)
        methods = subtechnique["Methods"]
        # a method is a way of running a technique
        # it is a bag of actions
        method = random.choice(methods)
        # return one method from available methods
        # TODO: Give user ability to specify the exact method to be used
        return method["Actions"]

    @staticmethod
    def execute_action(action_name, args, env_vars) -> None:
        """
        Takes a list of function names, and a args as input
        runs the corresponsing functions against the input
        """
        functions = {
            'load_mitre_technique': Actions.load_mitre_technique,
            'run_process_commands': Actions.run_process_commands,
            'write_files': Actions.write_files,
            'encrypt_files': Actions.encrypt_files,
            'create_users': Actions.create_users
        }
        print(f"Trying to run a fucntion called {action_name}")
        if action_name in functions:
            # all functions should accept env_vars
            # these are the gametime variables to be used. e.g. time, actor
            functions[action_name](args, env_vars)
        else:
            print("Function {} not found!".format(action_name))


    
    @staticmethod
    def run_process_commands(processes, env_vars):
        """
        Given a list of command arguments
        Create process event for every event
        Results are written to ProcessEvent logs

        
        Yaml Schema:

            process: required
            name: optional
            time_delay: optional -> defaults to minutes

        Example: 

            - run_process_commands:
                - name: bitsadmin.exe
                  process: bitsadmin /transfer myDownloadJob /download /priority normal "https://download.winzip.com/gl/nkln/winzip24-home.exe"
                  time_delay; minutes
                - name: winzip24-home.exe
                  process: winzip24-home.exe
                  time_delay: seconds
                - name: winzip.exe
                  process: winzip64.exe -min -a -s"hello" archive.zip *
        """
        from app.server.modules.endpoints.processes import Process
        from app.server.modules.endpoints.endpoint_controller import create_process_on_host

        original_time = env_vars["time"]
        user = env_vars["user"]
        actor = env_vars["actor"]
        # TODO: Figure out how to handle time
        for process in processes:
            # create the process object 
            time_delay = process.get("time_delay", "minutes")
            timestamp = Clock.delay_time_in_working_hours(start_time=original_time, factor=time_delay, workday_start_hour=actor.activity_start_hour,
                                                           workday_length_hours=actor.workday_length_hours, working_days_of_week=actor.working_days_list)

            process_obj = Process(
                process_name = process.get("name", None),
                process_commandline=process["process"],
            )

            # user process  obj to generate process log
            create_process_on_host(
                hostname="SOMEHOSTNAME",  #figure out how to get this across
                timestamp=timestamp,
                parent_process_name="cmd.exe",
                parent_process_hash="614ca7b627533e22aa3e5c3594605dc6fe6f000b0cc2b845ece47ca60673ec7f",
                process=process_obj,
                username=user.username
            )
        

    @staticmethod
    def write_files(args, env_vars):
        print(f"Write files {args}")


    @staticmethod
    def encrypt_files(args, env_vars):
        print(f"Envript files {args}")

    @staticmethod
    def create_users(args, env_vars):
        print("Create users sh*t")

    @staticmethod
    def download_from_url(args, env_vars):
        print(f"downloading from user {args}")