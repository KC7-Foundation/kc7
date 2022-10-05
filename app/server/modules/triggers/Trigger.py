# Import external modules
from asyncore import write
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
from app.server.modules.endpoints.file_creation_event import FileCreationEvent
from app.server.modules.endpoints.processes import Process, ProcessEvent
from app.server.modules.endpoints.endpoint_alerts import EndpointAlert
from app.server.modules.endpoints.endpoint_controller import (
    upload_file_creation_event_to_azure, 
    upload_process_creation_event_to_azure,
    write_file_to_host )
from app.server.modules.infrastructure.DNSRecord import DNSRecord
from app.server.modules.authentication.auth_controller import auth_to_mail_server, upload_auth_event_to_azure
from app.server.modules.file.malware_controller import get_malware_by_name, write_file_to_host
from app.server.modules.inbound_browsing.inbound_browsing_controller import gen_inbound_request, make_email_exfil_url

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
        if email.authenticity >= recipient.awareness:
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

        # The downloaded file causes a process to kick off after some time
        Trigger.file_creates_process(recipient, time, email, file_creation_event)

        # if user runs the file then beacon from user machine
        # there should be a condition here
        if email.actor.name != "Default":
            if email.actor.malware:
                Trigger.email_attachment_drops_payload(recipient, time, email)
                Trigger.malware_beacons_on_user_machine(recipient, time, email)

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

    def file_creates_process(recipient: Employee, time: float, email: Email, file_creation_event: FileCreationEvent) -> None:
        """
        When a file is downloaded, it will kick off a process on the machine 
        This occurs after a random amount of time between 30 and 180 seconds
        """
        process_time=Clock.increment_time(time, random.randint(30,180))
        process = ProcessEvent(
           timestamp=process_time, 
           parent_process_name=email.link.split("/")[-1],
           parent_process_hash=file_creation_event.sha256,
           process_commandline="powershell -nop -w hidden -enc d2hvYW1p",
           process_name="powershell.exe",
           process_hash="cda48fc75952ad12d99e526d0b6bf70a",
           hostname=recipient.hostname
        )

        upload_process_creation_event_to_azure(process)

    def malware_beacons_on_user_machine(recipient: Employee, time: float, email: Email) -> None:
        """
        When a user dowloads a file, there is a chance the file gets executed
        On execution, the victim's machine should begin beaconing to an actor IP 
        The beacons are logged in the outbound browsing logs
        e.g. victim ip -> actor C2 IP
        """
        c2_commands = ["whoami", "dir", "net view", "ping%208.8.8.8", "netsh%20advfirewall",
                       "systeminfo", "ipconfig", "tasklist", "net%20time", "netstat"]

        # look up the domain in the DB and get actor from it
        # actor = DNSRecord.query.filter_by(domain=email.domain).first().actor
        actor = email.actor

        actor_domains = [record.domain for record in actor.dns_records]
        actor_ips = [record.ip for record in actor.dns_records]

        c2_command = random.choice(c2_commands)

        c2 = random.choice(actor_domains + actor_ips)
        c2_link = c2 + ":" + \
            str(random.randint(8000, 14000)) + "/" + c2_command

        # wait several hours before beaconing
        time_delay = random.randint(5000, 99999)
        time = Clock.increment_time(time, time_delay)

        browse_website(recipient, c2_link, time)

    @staticmethod
    def actor_auths_into_user_email(recipient:Employee, email: Email, time: float):
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
    def actor_downloads_files_from_email(recipient:Employee, src_ip:str, time: float):
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

        