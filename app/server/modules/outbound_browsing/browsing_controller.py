import os
import random, json
import urllib.parse
from datetime import datetime
from datetime import timedelta
 
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

# instantiate faker
fake = Faker()
fake.add_provider(internet)
fake.add_provider(user_agent)

@timing
def browse_random_website(employees:"list[Employee]", actor:Actor, count_browsing:int):
    """
    Generate n web requests to random websites on the internet    
    """

    for _ in range(count_browsing):
        link = get_link(actor=actor, actor_domains=actor.domains_list)
        employee = random.choice(employees)

        #Get the current game session from the database
        time = get_time()
        browse_website(employee, link, time)


def browse_website(employee:Employee, link:str, time:float, method: str = None):
    """Browse a website on the web - given a link"""

    event = OutboundEvent(
        time = time, #TODO: Fix eventually
        src_ip = employee.ip_addr,
        user_agent = employee.user_agent,
        url = link,
        method = method
    )
    
    upload_event_to_azure(event)


def upload_event_to_azure(event):

    from app.server.game_functions import LOG_UPLOADER
    LOG_UPLOADER.send_request(
            data = [event.stringify()],
            table_name= "OutboundBrowsing")


@timing
def actor_stages_malware_on_watering_hole(actor:Actor, num_employees:int):
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
                uri_type="malware_delivery", 
                actor=actor
            )
        )
        
        time = Clock.delay_time_by(start_time=get_time(), factor="hours")

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
