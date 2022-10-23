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


def browse_random_website(employees:"list[Employee]", actor:Actor, count_browsing:int):
    """
    Generate n web requests to random websites on the internet    
    """
    # get a random user from the database
    actor_domains = [record.domain for record in actor.dns_records]

    for _ in range(count_browsing):
        link = get_link(actor=actor, actor_domains=actor_domains)
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