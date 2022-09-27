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
    for _ in range(count_browsing):
        employee = random.choice(employees)

        #Get the current game session from the database
        current_session = db.session.query(GameSession).get(1)

        # time is returned as timestamp (float)
        time = Clock.get_current_gametime(start_time=current_session.start_time,
                                                seed_date=current_session.seed_date)

        browse_website(employee, get_link(actor), time)


def browse_website(employee:Employee, link:str, time:float):
    """Browse a website on the web - given a link"""

    event = OutboundEvent(
        time = time, #TODO: Fix eventually
        src_ip = employee.ip_addr,
        user_agent = employee.user_agent,
        url = link
    )
    
    upload_event_to_azure(event)


def upload_event_to_azure(event):

    from app.server.game_functions import log_uploader
    log_uploader.send_request(
            data = [event.stringify()],
            table_name= "OutboundBrowsing")