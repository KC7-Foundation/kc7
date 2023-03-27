# Import external modules
from enum import Enum
from multiprocessing import parent_process
import random
from faker import Faker
from faker.providers import internet, lorem
import re
from datetime import date

# Import internal modules
from flask import current_app
from app.server.models import *
from app.server.modules.endpoints.file_creation_event import FileCreationEvent, File
from app.server.modules.endpoints.processes import ProcessEvent, Process
from app.server.modules.logging.uploadLogs import LogUploader
from app.server.modules.clock.Clock import Clock
from app.server.utils import *
from app.server.modules.constants.legit_files import *
from app.server.modules.constants.constants import COMMON_USER_FILE_LOCATIONS, LEGIT_USER_COMMANDLINES, LEGIT_SYSTEM_COMMANDLINES, LEGIT_PARENT_PROCESSES, LEGIT_SYSTEM_PARENT_PROCESSES, FILE_CREATING_PROCESSES, LEGIT_EXECUTABLES_TO_INSTALL

# instantiate faker
fake = Faker()
fake.add_provider(internet)
fake.add_provider(lorem)
fake.add_provider(file)

@timing
def gen_system_files_on_host(start_date: date, start_hour: int, workday_length_hours: int, percent_employees_to_generate: float, count_of_events_per_user:int=2) -> None:
    """
    Generates FileCreationEvents for system files generated on a host
    {
            "timestamp": 2022-10-03 12:30:00
            "hostname": GXDR-4310,
            "username": grschloe,
            "sha256": 269eb0728413654856f4b2ee1fa7838cd69672ebc11baed4caa63f58c2df5823,
            "path": C:/Windows/System32/xcopy.exe,
            "filename": xcopy.exe,
            "size": 4510,
            "process_name": "svchost.exe"
    }
    """
    from app.server.modules.alerts.alerts_controller import generate_host_alert

    total_num_employees = get_company().count_employees
    employees = get_employees(count=int(total_num_employees*percent_employees_to_generate))

    for employee in employees:
        hash_path_pairs = random.choices(list(LEGIT_WINDOWS_FILES.items()), k=count_of_events_per_user)
        
        for hash, path in hash_path_pairs:
            filename = path.split("/")[-1]
            time = Clock.generate_bimodal_timestamp(start_date, start_hour, workday_length_hours).timestamp()
            
            file_creation_event = FileCreationEvent(
                hostname=employee.hostname, #Pick a random employee to generate system files
                username=employee.username, # Get this from the random employee
                timestamp=time,
                filename=filename, # Get the filename from the path 
                path="C:/"+path, # Add a drive letter
                sha256=hash,
                process_name=random.choice(['svchost.exe','wuauclt.exe']) #TODO: Add more of these!
            )

            if random.random() < .0001 and ".exe" in filename: #FP: Use reports legit system file
                generate_host_alert(
                    time=Clock.delay_time_by(time, factor="minutes"),
                    hostname=employee.hostname,
                    filename=filename,
                    sha256=hash
                )

            upload_endpoint_event_to_azure(file_creation_event, table_name="FileCreationEvents")      


@timing
def gen_system_processes_on_host(start_date: date, start_hour: int, workday_length_hours: int, percent_employees_to_generate: float, count_of_events_per_user:int=2) -> None:
    """
    Generates ProcessEvents for users
    """
    total_num_employees = get_company().count_employees
    employees = get_employees(count=int(total_num_employees*percent_employees_to_generate))
    process_events = []
    
    for employee in employees:
        for i in range(count_of_events_per_user):
            # Half the time, make a user event too
            # This is an attempted performance improvement (instead of 2 loops)
            if (i%2 == 0):
                process = get_legit_user_process(
                    username=employee.username, 
                    filename=fake.file_name(category='office')
                )
                parent_name, parent_hash = random.choice(list(LEGIT_PARENT_PROCESSES.items()))

                process_event=ProcessEvent(
                    timestamp=Clock.generate_bimodal_timestamp(start_date, start_hour, workday_length_hours).timestamp(),
                    parent_process_name=parent_name,
                    parent_process_hash=parent_hash,
                    process_commandline=process.process_commandline,
                    process_name=process.process_name,
                    hostname=employee.hostname,
                    username=employee.username,
                )
                upload_endpoint_event_to_azure(process_event, table_name="ProcessEvents")
                #process_events.append(process_event)
            
            # Generates ProcessEvents for system
            # Always generate a system event
                process = get_legit_system_process(
                    username=employee.username, 
                    filename=fake.file_name(category='office')
                )
                parent_name, parent_hash = random.choice(list(LEGIT_SYSTEM_PARENT_PROCESSES.items()))

                process_event=ProcessEvent(
                    timestamp=Clock.generate_bimodal_timestamp(start_date, start_hour, workday_length_hours).timestamp(),         
                    parent_process_name=parent_name,
                    parent_process_hash=parent_hash,
                    process_commandline=process.process_commandline,
                    process_name=process.process_name,
                    hostname=employee.hostname,
                    username="System"
                )
                upload_endpoint_event_to_azure(process_event, table_name="ProcessEvents")
                #process_events.append(process_event)

    # print(f"uploading {len(process_events)}  events to ADX")
    #upload_endpoint_event_to_azure(process_events, table_name="ProcessEvents")
    
    

def get_legit_system_process(username: str = None, filename: str = None) -> Process:
    """
    Build a legitimate process and return it
    """
    process_commandline = random.choice(LEGIT_SYSTEM_COMMANDLINES)
    if username:
        process_commandline = process_commandline.replace("{username}","System")
    if filename:
        process_commandline = process_commandline.replace("{filename}","System") # Need to add Network Service and other non-user accounts

    try:
        process_name = re.search('([^\\\\]+\\.exe)',process_commandline.lower()).group(1)
    except:
        process_name = "PARSE_ERROR.exe"

    return Process(
        process_name=process_name,
        process_commandline=process_commandline
    )

def get_legit_user_process(username: str = None, filename: str = None) -> Process:
    """
    Build a legitimate process and return it
    """
    process_commandline = random.choice(LEGIT_USER_COMMANDLINES)
    if username:
        process_commandline = process_commandline.replace("{username}",username)
    if filename:
        process_commandline = process_commandline.replace("{filename}",filename)

    try:
        process_name = re.search('([^\\\\]+\\.exe)',process_commandline.lower()).group(1)
    except:
        process_name = "PARSE_ERROR.exe"

    return Process(
        process_name=process_name,
        process_commandline=process_commandline
    )

@timing
def gen_user_files_on_host(start_date: date, start_hour: int, workday_length_hours: int, percent_employees_to_generate:float, count_of_events_per_user:int=5) -> None:
    """
    Generates FileCreationEvents for user files generated on a host
    TODO: Example here
    """
    employees = get_employees()

    # This will make files related to normal productivity stuff
    for employee in random.choices(employees, k=int(len(employees)*percent_employees_to_generate)):
        for _ in range(count_of_events_per_user):
            path = random.choice(COMMON_USER_FILE_LOCATIONS).replace("{username}",employee.username)
            if "Pictures" in path:
                category='image'
            elif "Videos" in path:
                category='video'
            elif "Music" in path:
                category='audio'
            else:
                category='office'
                
            write_file_to_host(
                hostname=employee.hostname,
                username=employee.username,
                process_name=random.choice(FILE_CREATING_PROCESSES),
                timestamp=Clock.generate_bimodal_timestamp(start_date, start_hour, workday_length_hours).timestamp(),
                file=File(
                    filename=fake.file_name(category=category),
                    path=path
                )
            )
    # This will create legit executables/applications
    for employee in random.choices(employees, k=10): #FIX THIS LATER

        file = random.choice(LEGIT_EXECUTABLES_TO_INSTALL)
        time=Clock.delay_time_by(start_time=get_time(), factor="month", is_random=True)
        write_file_to_host(
            hostname=employee.hostname,
            username=employee.username,
            process_name=random.choice(FILE_CREATING_PROCESSES),
            timestamp=Clock.generate_bimodal_timestamp(start_date, start_hour, workday_length_hours).timestamp(),
            file=file
        )
    
def upload_endpoint_event_to_azure(events, table_name: str) -> None:

    """
    A function to upload a ProcessCreationEvent to ADX
    take either one event or a list of events 
    References global log_uploader to queue log rows for uploading
    """
    from app.server.game_functions import LOG_UPLOADER
        
    if isinstance(events, list):
        events = [event.stringify() for event in events ]
        # print(data)
    else:
        # it should just be an event obj
        events = [events.stringify()]


    for event in events:
        # print(f"submitting {len(chunk)} events to ADX")
        LOG_UPLOADER.send_request(
            data=[event],
            table_name=table_name)


def write_file_to_host(hostname: str, username: str, process_name: str, timestamp: float, file: File) -> None:
    """
    Uploads a FileCreationEvent for a given host, time, and File
    """
    if "{username}" in file.path:
        modified_path = file.path.replace("{username}", username)
    else:
        modified_path = file.path

    upload_endpoint_event_to_azure(
        FileCreationEvent(
            hostname=hostname,
            username=username,
            timestamp=timestamp,
            filename=file.filename,
            path=modified_path,
            sha256=file.sha256,
            size=file.size,
            process_name=process_name
        ),
        table_name="FileCreationEvents"
    )

def create_process_on_host(hostname: str, timestamp: float, parent_process_name: str, parent_process_hash: str, process: Process, username:str):
    """
    Uploads a ProcessEvent for a given host, time, parent process, and process
    """
    upload_endpoint_event_to_azure(
        ProcessEvent(
            timestamp=timestamp,
            hostname=hostname,
            parent_process_name=parent_process_name,
            parent_process_hash=parent_process_hash,
            process_name=process.process_name,
            process_commandline=process.process_commandline,
            process_hash=process.process_hash,
            username=username
        ),
        table_name="ProcessEvents"
    )