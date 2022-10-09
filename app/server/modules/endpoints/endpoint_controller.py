# Import external modules
from enum import Enum
from multiprocessing import parent_process
import random
from faker import Faker
from faker.providers import internet, lorem
import re

# Import internal modules
from flask import current_app
from app.server.models import *
from app.server.modules.endpoints.file_creation_event import FileCreationEvent, File
from app.server.modules.endpoints.processes import ProcessEvent, Process
from app.server.modules.logging.uploadLogs import LogUploader
from app.server.modules.clock.Clock import Clock
from app.server.utils import *
from app.server.modules.constants.legit_files import *
from app.server.modules.constants.constants import COMMON_USER_FILE_LOCATIONS, LEGIT_COMMANDLINES, LEGIT_PARENT_PROCESSES

# instantiate faker
fake = Faker()
fake.add_provider(internet)
fake.add_provider(lorem)
fake.add_provider(file)

def gen_system_files_on_host(count_of_events:int=10) -> None:
    """
    Generates FileCreationEvents for system files generated on a host
    {
            "timestamp": 2022-10-03 12:30:00
            "hostname": GXDR-4310,
            "sha256": 269eb0728413654856f4b2ee1fa7838cd69672ebc11baed4caa63f58c2df5823,
            "path": C:/Windows/System32/xcopy.exe,
            "filename": xcopy.exe,
            "size": 4510
    }
    """
    hash_path_pairs = random.choices(list(LEGIT_WINDOWS_FILES.items()), k=count_of_events)
    for hash, path in hash_path_pairs:
        file_creation_event = FileCreationEvent(
            hostname=get_random_employee().hostname, #Pick a random employee to generate system files
            timestamp=get_time(),
            filename=path.split("/")[-1], # Get the filename from the path 
            path="C:/"+path, # Add a drive letter
            sha256=hash
        )
        upload_file_creation_event_to_azure(file_creation_event)    

def gen_system_processes_on_host(count_of_events:int=10) -> None:
    """
    Generates ProcessEvents for system files
    """
    for _ in range(count_of_events):
        employee = get_random_employee()
        process = get_legit_process(
            username=employee.username, 
            filename=fake.file_name(category='office')
        )
        parent_name, parent_hash = random.choice(list(LEGIT_PARENT_PROCESSES.items()))

        process_event=ProcessEvent(
            timestamp=get_time(),
            parent_process_name=parent_name,
            parent_process_hash=parent_hash,
            process_commandline=process.process_commandline,
            process_name=process.process_name,
            hostname=employee.hostname
        )
        upload_process_creation_event_to_azure(process_event)

def get_legit_process(username: str = None, filename: str = None) -> Process:
    """
    Build a legitimate process and return it
    """
    process_commandline = random.choice(LEGIT_COMMANDLINES)
    print(process_commandline)
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

def gen_user_files_on_host(count_of_events:int=10) -> None:
    """
    Generates FileCreationEvents for user files generated on a host
    TODO: Example here
    """
    for _ in range(count_of_events):
        employee = get_random_employee()
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
            timestamp=get_time(),
            file=File(
                filename=fake.file_name(category=category),
                path=path
            )
        )


def upload_file_creation_event_to_azure(event: FileCreationEvent, table_name: str = "FileCreationEvents") -> None:

    """
    A function to upload a FileCreationEvent to ADX
    References global LOG_UPLOADER to queue log rows for uploading
    """

    from app.server.game_functions import LOG_UPLOADER
    LOG_UPLOADER.send_request(
        data=[event.stringify()],
        table_name=table_name)

def upload_process_creation_event_to_azure(event: ProcessEvent, table_name: str = "ProcessEvents") -> None:

    """
    A function to upload a ProcessCreationEvent to ADX
    References global log_uploader to queue log rows for uploading
    """

    from app.server.game_functions import LOG_UPLOADER
    LOG_UPLOADER.send_request(
        data=[event.stringify()],
        table_name=table_name)

def write_file_to_host(hostname: str, timestamp: float, file: File) -> None:
    """
    Uploads a FileCreationEvent for a given host, time, and File
    """
    upload_file_creation_event_to_azure(
        FileCreationEvent(
            hostname=hostname,
            timestamp=timestamp,
            filename=file.filename,
            path=file.path,
            sha256=file.sha256,
            size=file.size
        )
    )

def create_process_on_host(hostname: str, timestamp: float, parent_process_name: str, parent_process_hash: str, process: Process):
    """
    Uploads a ProcessEvent for a given host, time, parent process, and process
    """
    upload_process_creation_event_to_azure(
        ProcessEvent(
            timestamp=timestamp,
            hostname=hostname,
            parent_process_name=parent_process_name,
            parent_process_hash=parent_process_hash,
            process_name=process.process_name,
            process_commandline=process.process_commandline,
            process_hash=process.process_hash
        )
    )