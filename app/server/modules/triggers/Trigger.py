# Import external modules
from asyncore import write
from re import S
from faker import Faker
from faker.providers import user_agent

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
    upload_file_creation_event_to_azure, 
    upload_process_creation_event_to_azure,
    write_file_to_host,
    create_process_on_host )
from app.server.modules.infrastructure.DNSRecord import DNSRecord
from app.server.modules.authentication.auth_controller import auth_to_mail_server, upload_auth_event_to_azure
from app.server.modules.file.malware_controller import get_malware_by_name
from app.server.modules.inbound_browsing.inbound_browsing_controller import gen_inbound_request, make_email_exfil_url
from app.server.modules.file.malware import Malware

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
        if email.authenticity >= recipient.awareness and email.accepted:
            # users click on email after 30 - 600 seconds after it was sent to them
            click_delay = random.randint(30, 600)
            # add time delay
            time = Clock.increment_time(email.time, click_delay)

            browse_website(recipient, email.link, time)
            Trigger.update_team_scores_for_browsing(email.domain)

            if ("." in email.link.split("/")[-1]) and ("html" not in email.link): # could be cleaner
                # This is a link to a file
                #  #TODO make this more elegant
                Trigger.user_downloads_file(recipient, email, time)
            elif email.actor.name != "Default":
                Trigger.actor_auths_into_user_email(recipient, email, time)

    @staticmethod
    def update_team_scores_for_browsing(domain: str) -> None:
        """
        For each actor domain seen in email
            - if a user clicks on the malicious domain in email
        """
        teams = Team.query.all()

        for team in teams:
            if domain not in team._mitigations:
                team.score = team.score - 50
                db.session.commit()
                # TODO: Generate a logon attempt for the recipient (random success/fail rate??)
                # print(f"The user {recipient.name} opened this email!")

    @staticmethod
    def user_downloads_file(recipient: Employee, email: Email, time: float) -> None:
        """
        When a user clicks a bad link, they download a malicioud file
        Write a file to the filesystem
        """
        filename = email.link.split(
            "/")[-1]  # in the future, this should be parsed from the link
        file_creation_event = FileCreationEvent(
            hostname=recipient.hostname,
            timestamp=time,
            filename=filename,
            # TODO: generate in filesystem instead
            path=f"C:\\Users\\{recipient.username}\\Downloads\\{filename}",
        )

        # This will come from the filesystem controller
        upload_file_creation_event_to_azure(file_creation_event)

        # if user runs the file then beacon from user machine
        # there should be a condition here
        if email.actor.name != "Default":
            if email.actor.malware:
                payload_time = Clock.delay_time_by(start_time=time, factor="seconds")
                Trigger.email_attachment_drops_payload(recipient, payload_time, email)

    @staticmethod
    def email_attachment_drops_payload(recipient: Employee, time: float, email: Email) -> None:
        """
        When a file is downloaded from a URL sent by a malicious actor, an implant will be dropped
        This will also trigger a process
        """
        malware_family_to_drop = email.actor.get_random_malware_name()
        malware = get_malware_by_name(malware_family_to_drop)
        implant = malware.get_implant()
        write_file_to_host(
            hostname=recipient.hostname,
            timestamp=time,
            file=implant
        )
        
        process_creation_time = Clock.delay_time_by(start_time=time, factor="minutes")
        Trigger.payload_creates_processes(recipient, process_creation_time, email, malware, payload=implant)

    @staticmethod
    def payload_creates_processes(recipient: Employee, time: float, email: Email, malware: Malware, payload: File) -> None:
        """
        When a payload is dropped to a user's system, it should also spawn processes.
        The processes that are spawned are defined in the malware config
        """
        # Get a C2 IP from the Actor's infrastructure
        c2_ip = email.actor.get_ips(count_of_ips=1)[0]
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
                process=process
            )

    @staticmethod
    def actor_auths_into_user_email(recipient:Employee, email: Email, time: float) -> None:
        """
        After use clicks on a credential phishing link and enters their creds (we assume this for now)
        The threat actor will login to their account
        Generate a main authentication where where
            username = recipient's username
            src_up = actor's ip
        """
        # wait several hours before login
        time_delay = random.randint(5000, 99999)
        login_time = Clock.increment_time(time, time_delay)
        auth_results = ["Successful Login", "Failed Login"]
        src_ip = email.actor.dns_records.first().ip
        result = random.choice(auth_results)

        auth_to_mail_server(
            timestamp= login_time,
            username=recipient.username,
            src_ip=src_ip,  
            user_agent = fake.firefox(),
            result = result
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

        