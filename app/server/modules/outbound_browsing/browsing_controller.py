import os
import random, json
import urllib.parse
from datetime import datetime, timedelta, date
 
from faker import Faker
from faker.providers import internet
from faker.providers import user_agent

# Import internal modules
from flask import current_app
from app.server.modules.logging.uploadLogs import LogUploader
from app.server.modules.outbound_browsing.outboundEvent import OutboundEvent
from app.server.modules.clock.Clock import Clock 
from app.server.models import GameSession
from app.server.utils import *
from app.server.modules.helpers.browsing_helpers import *
from app.server.modules.helpers.config_helper import read_list_from_file

# instantiate faker
fake = Faker()
fake.add_provider(internet)
fake.add_provider(user_agent)

@timing
def browse_random_website(employees:"list[Employee]", actor:Actor, count_browsing:int, percent_employees_to_generate: float, start_date: date):
    """
    Generate n web requests to random websites on the internet  
    # this should typically be for the default actor  
    """
    from app.server.game_functions import LEGIT_DOMAINS, CONTENT_DOMAINS, RANDOMIZED_DOMAINS, PARTNER_DOMAINS
    company = get_company()   
        
    # Get the number of employees to generate
    total_num_employees = company.count_employees
    employees_for_activity_generation = int(total_num_employees*percent_employees_to_generate)
    employees_to_generate = random.choices(employees, k=employees_for_activity_generation)

    browsing_events = []
    # TODO: Can this be made more efficient?
    for employee in employees_to_generate:
        for _ in range(count_browsing):
            link = get_link()
            employee = random.choice(employees)
            time = Clock.generate_bimodal_timestamp(start_date, actor.activity_start_hour, actor.workday_length_hours).timestamp()
            outbound_event = OutboundEvent(
                time=time,
                src_ip=employee.ip_addr,
                user_agent=employee.user_agent,
                url=link,
            )
            upload_event_to_azure(outbound_event, "OutboundNetworkEvents")    


def browse_website(employee:Employee, link:str, time:float, method: str = None):
    """Browse a website on the web - given a link"""
    event = OutboundEvent(
        time = time, #TODO: Fix eventually
        src_ip = employee.ip_addr,
        user_agent = employee.user_agent,
        url = link,
        method = method
    )
    
    upload_event_to_azure(event, "OutboundNetworkEvents")


def upload_event_to_azure(events, table_name:str):
    from app.server.game_functions import LOG_UPLOADER

    if isinstance(events, list):
        events = [event.stringify() for event in events]
        # print(data)
    else:
        # it should just be an event obj
        events = [events.stringify()]

    for event in events:
        # print(f"submitting {len(chunk)} events to ADX")
        LOG_UPLOADER.send_request(
            data=[event],
            table_name=table_name)

@timing
def actor_stages_watering_hole(actor:Actor, start_date: date, num_employees:int, link_type="malware_delivery"):
    """
    Certain users click on a watering hole link, and download malware
    """
    from app.server.modules.triggers.Trigger import Trigger

    if not actor.water_hole_domains_list:
        raise Exception("You need to provide some watering_hole_domains in the actor config")

    for employee in get_employees(roles_list=actor.watering_hole_target_roles_list, count=num_employees):        
        water_hole_domain = random.choice(actor.water_hole_domains_list) 
        actor_domain = actor.get_domain()

        redirect_url = f"https://{water_hole_domain}?redirect={actor_domain}"
        malicious_url = (
         "https://"
         + actor_domain 
         + "/"
         + get_uri_path(
                max_depth=2, 
                max_params=2, 
                uri_type=link_type, 
                actor=actor
            )
        )
        
        time = Clock.generate_bimodal_timestamp(start_date=start_date, 
                                                start_hour=actor.activity_start_hour,
                                                day_length=actor.workday_length_hours).timestamp()

        # first browse to the compromised website and get redirected
        browse_website(
            employee=employee,
            link= redirect_url,
            time=time,
            method="GET"
        )

        # then browse to the malicious url
        Trigger.user_clicks_link(
            recipient=employee,
            link=malicious_url,
            actor=actor,
            time=Clock.delay_time_by(start_time=time, factor="seconds")
        )
