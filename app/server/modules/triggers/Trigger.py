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
from app.server.utils import *


class Trigger:
    """
    A trigger handles the generation of events that have consequences
    E.g. User receives email -> user clicks on email -> user browses website
         User browses website -> user downloads file
         Use downloads file -> Process runs on user machine

    Logic for event trigger should be handled here ???
    """

    @staticmethod
    def user_receives_email(email:Email, recipient:Employee):
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
            Trigger.update_team_scores_for_browsing(email.link)
            if "." in email.link.split("/")[-1]:
                # This is a link to a file
                #  #TODO make this more elegant
                Trigger.user_downloads_file(recipient, email.link, time)


    @staticmethod
    def update_team_scores_for_browsing(domain: str):
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


    def user_downloads_file(recipient:Employee, link, time):
        """
        When a user clicks a bad link, they download a malicioud file
        Write a file to the filesystem
        """
        filename = link.split("/")[-1] # in the future, this should be parsed from the link
        file_creation_event = FileCreationEvent(
            hostname=recipient.hostname,
            creation_time=time,
            md5= FileCreationEvent.get_random_hash(),
            #TODO: generate in filesystem instead
            path= f"C:\\Users\\{recipient.username}\\Downloads\\{filename}",
            size = random.randint(100, 999999)  #TODO: have payload class that define properties. This was Greg's idea! :) "It will be trivial"
        )

        upload_endpoint_event_to_azure(file_creation_event, "FileCreationEvent") # This will come from the filesystem controller
