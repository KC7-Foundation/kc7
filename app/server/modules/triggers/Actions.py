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
            'create_files': Actions.create_files,
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

        TODO: Add ability to inject actor ip or domain

        Yaml Schema:

            process:    required; this is the process commandline; 
            name:       optional; the is the name of the process
            time_delay: optional; defaults to minutes

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
                hostname=user.hostname,  #theorically we can inject here
                timestamp=timestamp,
                parent_process_name="cmd.exe",
                parent_process_hash="614ca7b627533e22aa3e5c3594605dc6fe6f000b0cc2b845ece47ca60673ec7f",
                process=process_obj,
                username=user.username
            )
        

    @staticmethod
    def create_files(files, env_vars):
        """
        Given a list of file  arguments
        Create the corresponding files in logs
        Results are written to FileCreationEvent logs

        Yaml Schema:

            path:    required; this is the process commandline; 
            sha256:  optional;  but highly recommended. defaults default to a random hash
            size: optional
            time_delay: optional; defaults to minutes

        Example: 

            - create_files:
                - path:  C:\\ProgramData\\BluePhoenix\\mimikatz.exe
                  sha256: 614ca7b627533e22aa3e5c3594605dc6fe6f000b0cc2b845ece47ca60673ec7f
                  size: 9999
                  time_delay; minutes
                - path: C:\\Users\Admin\\modifiedplink.exe
                  sha256: d2626aab4a95836b17c9abae2e7fdca20f052fcc0e599a8ad16ea6deabcc0b22
                - path: E:\\Exfil\\qdata.zip
        """
        from app.server.modules.endpoints.file_creation_event import File
        from app.server.modules.endpoints.endpoint_controller import write_file_to_host

        original_time = env_vars["time"]
        user = env_vars["user"]
        actor = env_vars["actor"]

        for file in files:
            time_delay = file.get("time_delay", "minutes")
            timestamp = Clock.delay_time_in_working_hours(start_time=original_time, factor=time_delay, workday_start_hour=actor.activity_start_hour,
                                                           workday_length_hours=actor.workday_length_hours, working_days_of_week=actor.working_days_list)

            filename = file.get("path", "").split("\\")[-1]     
            path = file.get("path", "")                                
            #create the file object
            file_obj = File(
                filename=filename,
                path=path,
                sha256=file.get("sha256", None),
                size=file.get("size", None)
            )
            #use the file obj to make file creation obj
            write_file_to_host(
                hostname=user.hostname,
                username=user.username,
                process_name=None,
                timestamp=timestamp,
                file=file_obj
            )

            print(f"=============> Creating a file..... {file_obj.path}{file_obj.filename}")




    @staticmethod
    def encrypt_files(args, env_vars):
        print(f"Envript files {args}")

    @staticmethod
    def create_users(args, env_vars):
        print("Create users sh*t")

    @staticmethod
    def download_from_url(args, env_vars):
        print(f"downloading from user {args}")