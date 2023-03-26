# Import external modules
from asyncore import write
from re import S
from faker import Faker
from faker.providers import user_agent
import uuid

# Import internal modules
from code import interact
from flask import current_app
from app.server.models import *
from app.server.modules.email.email import Email
from app.server.modules.outbound_browsing.browsing_controller import browse_website
from app.server.modules.logging.uploadLogs import LogUploader
from app.server.modules.clock.Clock import Clock
from app.server.modules.endpoints.file_creation_event import FileCreationEvent, File
from app.server.modules.endpoints.processes import Process, ProcessEvent
from app.server.modules.endpoints.endpoint_alerts import EndpointAlert
from app.server.modules.endpoints.endpoint_controller import (
    upload_endpoint_event_to_azure, 
    write_file_to_host,
    create_process_on_host )
from app.server.modules.infrastructure.DNSRecord import DNSRecord
from app.server.modules.authentication.auth_controller import auth_to_mail_server, upload_auth_event_to_azure
from app.server.modules.file.malware_controller import get_malware_by_name
from app.server.modules.inbound_browsing.inbound_browsing_controller import gen_inbound_request, make_email_exfil_url
from app.server.modules.file.malware import Malware
from app.server.modules.constants.constants import FILE_CREATING_PROCESSES


from app.server.utils import *

# instantiate faker
fake = Faker()
fake.add_provider(user_agent)


class Trigger:
    """
    A trigger handles the generation of events that have consequences
    E.g. User receives email -> user clicks on email -> user browses website
         User browses website -> user downloads file
         Use downloads file -> Process runs on user machine

    Logic for event trigger should be handled here ???
    """

    @staticmethod
    def user_receives_email(email: Email, recipient: Employee) -> None:
        """
        A user received an email
        Decide whether or not the user clicks on the email

        TODO: add some variability later?
        """
        from app.server.modules.alerts.alerts_controller import generate_email_alert

        # users click on email after 30 - 600 seconds after it was sent to them
        delay = random.randint(30, 600)
        # add time delay
        time = Clock.increment_time(email.time, delay)

        if email.authenticity >= recipient.awareness and email.accepted:
            Trigger.user_clicks_link(recipient=recipient, link=email.link, actor=email.actor, time=time)
        else:
            # user didn't click the link they might report it instead
            if email.actor.is_default_actor:
                if random.random() < .01:
                    generate_email_alert(
                        time=time,
                        username=recipient.username,
                        subject=email.subject
                    )
            elif random.random() < .2:
                generate_email_alert(
                    time=time,
                    username=recipient.username,
                    subject=email.subject
                )
                


    @staticmethod
    def user_clicks_link(recipient:Employee, link:str, actor:Actor, time:float):
        """
        A user clicks a link
        can be from an email or otherwise
        """
        browse_website(
            employee=recipient,
            link= link,
            time=time,
            method="GET"
        )

        if ("." in link.split("/")[-1]) and ("html" not in link): # could be cleaner
            # This should be conditionals
            if random.random() > (recipient.awareness * .01):
                Trigger.user_downloads_file(recipient=recipient, link=link, actor=actor, time=time)
        elif actor.name != "Default":
            Trigger.actor_auths_into_user_email(recipient=recipient, actor=actor, time=time)


    @staticmethod
    def user_downloads_file(recipient: Employee, link: str, actor:Actor, time: float) -> None:
        """
        When a user clicks a bad link, they download a malicioud file
        Write a file to the filesystem
        """

        filename = link.split(
            "/")[-1]  # in the future, this should be parsed from the link
        file_creation_event = FileCreationEvent(
            hostname=recipient.hostname,
            username=recipient.username,
            timestamp=time,
            filename=filename,
            # TODO: generate in filesystem instead
            path=f"C:\\Users\\{recipient.username}\\Downloads\\{filename}",
            process_name=random.choice(['Edge.exe','chrome.exe','edge.exe','firefox.exe'])
        )

        # This will come from the filesystem controller
        upload_endpoint_event_to_azure(file_creation_event, table_name="FileCreationEvents")

        # if user runs the file then beacon from user machine
        # there should be a condition here
        if actor.name != "Default":
            if actor.malware:
                payload_time = Clock.delay_time_by(start_time=time, factor="seconds")
                Trigger.email_attachment_drops_payload(filename, recipient, payload_time, actor)

    @staticmethod
    def email_attachment_drops_payload(attachment_name:str, recipient: Employee, time: float, actor: Actor) -> None:
        """
        When a file is downloaded from a URL sent by a malicious actor, an implant will be dropped
        This will also trigger a process
        """
        from app.server.modules.alerts.alerts_controller import generate_host_alert

        if ".doc" in attachment_name:
            process_name = "winword.exe"
        elif ".ppt" in attachment_name:
            process_name = "ppt.exe"
        elif ".xls" in attachment_name:
            process_name = "excel.exe"
        elif ".zip" in attachment_name:
            process_name = "7zip.exe"
        elif ".rar" in attachment_name:
            process_name = "winrar.exe"
        else:
            process_name = "explorer.exe"

        malware_family_to_drop = actor.get_random_malware_name()
        malware = get_malware_by_name(malware_family_to_drop)
        implant = malware.get_implant()
        write_file_to_host(
            hostname=recipient.hostname,
            username=recipient.username,
            timestamp=time,
            file=implant,
            process_name=process_name
        )
        
        if random.random() < .1:
            generate_host_alert(
                time=Clock.delay_time_by(start_time=time, factor="minutes"),
                hostname=recipient.hostname,
                filename=implant.filename,
                sha256=implant.sha256
            )

        process_creation_time = Clock.delay_time_by(start_time=time, factor="minutes")
        Trigger.payload_creates_processes(recipient, process_creation_time, actor, malware, payload=implant)


        

    @staticmethod
    def payload_creates_processes(recipient: Employee, time: float, actor: Actor, malware: Malware, payload: File) -> None:
        """
        When a payload is dropped to a user's system, it should also spawn processes.
        The processes that are spawned are defined in the malware config
        """
        # Get a C2 IP from the Actor's infrastructure
        c2_ip = actor.get_ips(count_of_ips=1)[0]
        # Get random processes
        recon_process = malware.get_recon_process()
        c2_process = malware.get_c2_process(c2_ip)

        # Upload the recon and C2 processes to Azure
        for process in [recon_process, c2_process]:
            time = Clock.delay_time_by(start_time=time, factor="minutes")
            create_process_on_host(
                hostname=recipient.hostname,
                timestamp=time,
                parent_process_name=payload.filename,
                parent_process_hash=payload.sha256,
                process=process,
                username=recipient.username
            )

        # wait a couple hours before running post exploitation commands
        post_exploit_time = Clock.delay_time_by(start_time=time, factor="hours")
        if actor.post_exploit_commands:
            Trigger.actor_runs_post_exploitation_commands(recipient=recipient, time=post_exploit_time, actor=actor )


    @staticmethod
    def actor_runs_post_exploitation_commands(recipient: Employee, time: float, actor: Actor) -> None:
        """
        After the malware runs automated commands and establishes C2 channel,
        Run custom hands-on-keyboard commands defined on the actor
        """
        # Get a C2 IP from the Actor's infrastructure
        c2_ip = actor.get_ips(count_of_ips=1)[0]
        c2_domain = actor.get_domain()
        # Get random processes
        processes = actor.get_exploit_processes()

        # Upload the recon and C2 processes to Azure
        for process in processes:
            if random.random() > .9:
                break
            # now turn the command into necessry process object
            # print("getting actor hands on keyboard")
            # print(process)

            # turn process from dict into object
            process_obj = Malware.get_process_obj({
                "name": process.get("name", None),
                "process": process.get("process", None).replace("{actor_ip}", c2_ip).replace("{actor_domain}", c2_domain)
            })

            time = Clock.delay_time_by(start_time=time, factor="seconds")
            create_process_on_host(
                hostname=recipient.hostname,
                timestamp=time,
                parent_process_name=process_obj.process_name,
                parent_process_hash=process.get("hash", None) or "614ca7b627533e22aa3e5c3594605dc6fe6f000b0cc2b845ece47ca60673ec7f",
                process=process_obj,
                username=recipient.username
            )


    @staticmethod
    def actor_auths_into_user_email(recipient:Employee, actor: Actor, time: float) -> None:
        """
        After use clicks on a credential phishing link and enters their creds (we assume this for now)
        The threat actor will login to their account
        Generate a main authentication where where
            username = recipient's username
            src_up = actor's ip
        """
        print("Got to KC7...")
        # wait several hours before login
        time_delay = random.randint(5000, 99999)
        login_time = Clock.increment_time(time, time_delay)
        auth_results = ["Successful Login", "Failed Login"]
        src_ip = actor.get_ips(count_of_ips=1)
        
        result = random.choice(auth_results)
        if result == "Successful Login":
            password = f"{recipient.username}2023"
        else:
            # Get a random password (that is incorrect) if we have an unsuccessful login
            password = f"{uuid.uuid4()}"

        auth_to_mail_server(
            timestamp= login_time,
            username=recipient.username,
            src_ip=src_ip,  
            user_agent = fake.firefox(),
            result = result,
            password=password
        )

        if result == "Successful Login":
            Trigger.actor_downloads_files_from_email(recipient=recipient.username, src_ip=src_ip, time=login_time)

    @staticmethod
    def actor_downloads_files_from_email(recipient:Employee, src_ip:str, time: float) -> None:
        """
        Following successful auth into a user's account
        The actor downloads files from the user's email by making web requests
        """
        # wait several hours before exfil
        time_delay = random.randint(5000, 99999)
        exfil_time = Clock.increment_time(time, time_delay)
        exfil_url = make_email_exfil_url(recipient)

        gen_inbound_request(
            time=exfil_time,
            src_ip=src_ip,
            method="GET",
            status_code="200", # TODO: maybe these fail sometimes?
            url=exfil_url,
            user_agent=fake.firefox()
        )

        