# Import external modules
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
from app.server.modules.endpoints.processes import Processes
from app.server.modules.endpoints.endpoint_alerts import EndpointAlert
from app.server.modules.endpoints.endpoint_controller import upload_endpoint_event_to_azure
from app.server.modules.infrastructure.DNSRecord import DNSRecord
from app.server.modules.authentication.auth_controller import auth_to_mail_server, upload_auth_event_to_azure

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

            if "." in email.link.split("/")[-1]:
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

    def user_downloads_file(recipient: Employee, email: Email, time: float) -> None:
        """
        When a user clicks a bad link, they download a malicioud file
        Write a file to the filesystem
        """
        filename = email.link.split(
            "/")[-1]  # in the future, this should be parsed from the link
        file_creation_event = FileCreationEvent(
            hostname=recipient.hostname,
            creation_time=time,
            md5=FileCreationEvent.get_random_hash(),
            # TODO: generate in filesystem instead
            path=f"C:\\Users\\{recipient.username}\\Downloads\\{filename}",
            # TODO: have payload class that define properties. This was Greg's idea! :) "It will be trivial"
            size=random.randint(100, 999999),
        )

        # This will come from the filesystem controller
        upload_endpoint_event_to_azure(file_creation_event)

        # if user runs the file then beacon from user machine
        # there should be a condition here
        if email.actor.name != "Default":
            Trigger.malware_beacons_on_user_machine(recipient, time, email)

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


    def actor_auths_into_user_email(recipient:Employee, email: Email, time: float):

        # wait several hours before login
        time_delay = random.randint(5000, 99999)
        login_time = Clock.increment_time(time, time_delay)
        auth_results = ["Successful Login", "Failed Login"]

        src_ip = email.actor.dns_records.first().ip

        auth_event = auth_to_mail_server(
            creation_time= login_time,
            username=recipient.username,
            src_ip=src_ip,  
            user_agent = fake.firefox(),
            result = random.choice(auth_results)
        )

        #Trigger mroe bad stuff - e.g. download of email files from server

