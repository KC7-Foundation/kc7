# Import external modules
from asyncore import write
import os
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
from app.server.utils import metalog
from app.server.modules.triggers.Actions import Actions
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

        company = get_company()
        action_time = Clock.delay_time_in_working_hours(
                start_time=email.time, factor="minutes", 
                workday_start_hour=company.activity_start_hour,
                workday_length_hours=company.workday_length_hours, 
                working_days_of_week=company.working_days_list
            )

        if email.accepted:
            if email.authenticity >= recipient.awareness:
                # users click on email minutes (within working hours) after it was sent to them
                # add time delay
                Trigger.user_clicks_link(recipient=recipient, link=email.link, actor=email.actor, time=action_time)
                if email.actor.is_default_actor:
                    if random.random() < current_app.config['FP_RATE_EMAIL_ALERTS']: # FP, user reports legit email
                        generate_email_alert(
                            time=action_time,
                            username=recipient.username,
                            subject=email.subject
                        )
            else:
                # user didn't click the link they might report it instead
                if random.random() < current_app.config['TP_RATE_EMAIL_ALERTS']: # TP, user reports malicious email
                    generate_email_alert(
                        time=action_time,
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

        if not actor.is_default_actor:
            metalog(
                time=time, 
                actor=actor, 
                message=f'{recipient.name} clicked on a link: {link}'
            )

        if ("." in link.split("/")[-1]) and ("html" not in link): # could be cleaner
            # This should be conditionals
            download_time = Clock.delay_time_by(time, "seconds")
            Trigger.user_downloads_file(recipient=recipient, link=link, actor=actor, time=download_time)
        elif actor.name != "Default":
            # Use working time delay because this is an actor hands-on-keyboard activity
            login_time = Clock.delay_time_in_working_hours(start_time=time, factor="hours", workday_start_hour=actor.activity_start_hour,
                                                           workday_length_hours=actor.workday_length_hours, working_days_of_week=actor.working_days_list)
            Trigger.actor_auths_into_user_email(recipient=recipient, actor=actor, time=login_time)


    @staticmethod
    def user_downloads_file(recipient: Employee, link: str, actor:Actor, time: float) -> None:
        """
        When a user clicks a bad link, they download a malicioud file
        Write a file to the filesystem
        """
        from app.server.modules.alerts.alerts_controller import generate_host_quarantine_alert

        

        filename = link.split(
            "/")[-1]  # in the future, this should be parsed from the link
        path = f"C:\\Users\\{recipient.username}\\Downloads\\{filename}"
        process_name = random.choice(['Edge.exe','chrome.exe','edge.exe','firefox.exe']) 
        file_creation_event = FileCreationEvent(
            hostname=recipient.endpoint.name,
            username=recipient.username,
            timestamp=time,
            filename=filename,
            # TODO: generate in filesystem instead
            path=path,
            process_name=process_name#TODO: Make this correlate to employee UA
        )

        # This will come from the filesystem controller
        upload_endpoint_event_to_azure(file_creation_event, table_name="FileCreationEvents")

        ## log metadata for question generation
        if not actor.is_default_actor:
            metalog(
                time=time, 
                actor=actor, 
                message=f'{recipient.name} ({recipient.username}) downloaded file with path {path} via {process_name}'
            )

        # if user runs the file then beacon from user machine
        # there should be a condition here
        if not actor.is_default_actor:
            if actor.malware:
                payload_time = Clock.delay_time_by(start_time=time, factor="seconds")
                if random.random() < .9:
                    Trigger.email_attachment_drops_payload(filename, recipient, payload_time, actor)
                else:
                    # Qurantine the file and send an alert
                    generate_host_quarantine_alert(time=payload_time, hostname=recipient.endpoint.name, filename=filename, sha256="-")

    @staticmethod
    def email_attachment_drops_payload(attachment_name:str, recipient: Employee, time: float, actor: Actor) -> None:
        """
        When a file is downloaded from a URL sent by a malicious actor, an implant will be dropped
        This will also trigger a process
        """
        from app.server.modules.alerts.alerts_controller import generate_host_alert


        malware_family_to_drop = actor.get_random_malware_name()
        malware = get_malware_by_name(malware_family_to_drop)
        implant = malware.get_implant()

        write_file_to_host(
            hostname=recipient.endpoint.name,
            username=recipient.username,
            timestamp=time,
            file=implant,
            process_name=None
        )
        
        if random.random() < current_app.config['TP_RATE_HOST_ALERTS']:
            generate_host_alert(
                time=Clock.delay_time_by(start_time=time, factor="minutes"),
                hostname=recipient.endpoint.name,
                filename=implant.filename,
                sha256=implant.sha256
            )

        ## log metadata for question generation
        if not actor.is_default_actor:
            metalog(
                time=time, 
                actor=actor, 
                message=f'{recipient.name} ({recipient.username}) had an malicious file {implant.filename} ({implant.sha256}) created on their machine by {attachment_name}'
            )

        process_creation_time = Clock.delay_time_by(start_time=time, factor="minutes")
        Trigger.payload_creates_processes(recipient, process_creation_time, actor, malware, payload=implant)


        
    @staticmethod
    def payload_creates_processes(recipient: Employee, time: float, actor: Actor, malware: Malware, payload: File) -> None:
        # Log metadata for question generation
        if not actor.is_default_actor:
            metalog(
                time=time,
                actor=actor,
                message=f'A suspicious was created on {recipient.username}\'s machine by {payload.filename}: {process.process_commandline}'
            )

        # Execute all actions defined in the malware config
        actions = malware.actions
        env_vars = {
            "time": time,
            "actor": actor,
            "user": recipient
        }

        for action in actions:
            action_name, args = next(iter(action.items()))
            Actions.execute_action(action_name, args, env_vars)

        # Wait a couple of hours before running post-exploitation commands
        if actor.lateral_movement:
            post_exploit_time = Clock.delay_time_in_working_hours(
                start_time=time,
                factor="hours",
                workday_start_hour=actor.activity_start_hour,
                workday_length_hours=actor.workday_length_hours,
                working_days_of_week=actor.working_days_list
            )
            Trigger.actor_controls_host(recipient=recipient, time=post_exploit_time, actor=actor)

    # @staticmethod
    # def payload_creates_processes(recipient: Employee, time: float, actor: Actor, malware: Malware, payload: File) -> None:
    #     """
    #     When a payload is dropped to a user's system, it should also spawn processes.
    #     The processes that are spawned are defined in the malware config
    #     """
    #     # Get a C2 IP from the Actor's infrastructure
    #     c2_ip = actor.get_ips(count_of_ips=1)[0]
    #     # Get random processes
    #     recon_process = malware.get_recon_process()
    #     c2_process = malware.get_c2_process(c2_ip)

    #     # Upload the recon and C2 processes to Azure
    #     for process in [recon_process, c2_process]:
    #         time = Clock.delay_time_by(start_time=time, factor="minutes")
    #         create_process_on_host(
    #             hostname=recipient.endpoint.name,
    #             timestamp=time,
    #             parent_process_name=payload.filename,
    #             parent_process_hash=payload.sha256,
    #             process=process,
    #             username=recipient.username
    #         )

    #         ## log metadata for question generation
    #         if not actor.is_default_actor:
    #             metalog(
    #                 time=time, 
    #                 actor=actor, 
    #                 message=f'A suspicious was created on {recipient.username}\'s machine by {payload.filename}: {process.process_commandline}'
    #             )

    #     # wait a couple hours before running post exploitation commands
    #     if actor.lateral_movement:
    #         post_exploit_time = Clock.delay_time_in_working_hours(start_time=time, factor="hours", workday_start_hour=actor.activity_start_hour,
    #                                                        workday_length_hours=actor.workday_length_hours, working_days_of_week=actor.working_days_list)
    #         Trigger.actor_controls_host(recipient=recipient, time=post_exploit_time, actor=actor )




    @staticmethod
    def actor_controls_host(recipient: Employee, time: float, actor: Actor) -> None:
        """
        After the malware runs automated commands and establishes C2 channel,
        Run custom hands-on-keyboard commands defined on the actor
        """
        # Run actions based on the key-value pair provided
        from app.server.modules.triggers.Actions import Actions

        ## MAJOR TODO: Figure our how to handle timing differences between actions that are run
        ## Right now the clock just recents for every event and follows time-delays relative to when the function was invoked

        # loop through all the phases and run the define action in those pahses
        for phase in [actor.discovery, actor.lateral_movement, actor.exfiltration, actor.impact]:
            if phase:
                for action in phase:
                    for action_name, args in action.items():
                        # action_name is the name of the function to run
                        # args are the arguments defined in the yaml config. This can be a string, list, or dict
                        env_vars = {
                            "user": recipient,
                            "time": time,  #handle the delay better
                            "actor": actor
                        }
                        Actions.execute_action(action_name, args, env_vars)


    
                



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
        login_time = time
        auth_results = ["Successful Login", "Failed Login"]
        src_ip = actor.get_ips(count_of_ips=1)[0]
        
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

        if not actor.is_default_actor:
            metalog(
                time=time, 
                actor=actor, 
                message=f'A suspicious login attempt was observed to {recipient.username}\'s account from ip {src_ip}. The result of the login attempt was: {result}.'
            )

        if result == "Successful Login":
            download_time = Clock.delay_time_in_working_hours(start_time=time, factor="minutes", workday_start_hour=actor.activity_start_hour,
                                                           workday_length_hours=actor.workday_length_hours, working_days_of_week=actor.working_days_list)
            Trigger.actor_downloads_files_from_email(recipient=recipient, src_ip=src_ip, time=download_time, actor=actor)


    @staticmethod
    def actor_downloads_files_from_email(recipient:Employee, src_ip:str, time: float, actor:Actor) -> None:
        """
        Following successful auth into a user's account
        The actor downloads files from the user's email by making web requests
        """
        # wait several hours before exfil
        time_delay = random.randint(5000, 99999)
        exfil_time = Clock.increment_time(time, time_delay)
        exfil_url = make_email_exfil_url(recipient.username)

        gen_inbound_request(
            time=exfil_time,
            src_ip=src_ip,
            method="GET",
            status_code="200", # TODO: maybe these fail sometimes?
            url=exfil_url,
            user_agent=fake.firefox()
        )

        metalog(
                time=time, 
                actor=actor, 
                message=f'A file was downloaded from {recipient.username}\'s email account from ip {src_ip}. The download url was: {exfil_url}'
            )

        