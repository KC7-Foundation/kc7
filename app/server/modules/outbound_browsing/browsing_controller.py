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
from app.server.utils import *

# instantiate faker
fake = Faker()
fake.add_provider(internet)
fake.add_provider(user_agent)


def browse_random_website(employee, actor):
    """Browse a random website on the web"""
    # get a random user from the database
    #user = employee.... #TODO: implement this
    browse_website(employee, get_link(actor))


def browse_website(employee, link):
    """Browse a website on the web - given a link"""

    event = OutboundEvent(
        time = datetime.now(), #TODO: Fix eventually
        src_ip = employee.ip_addr,
        user_agent = employee.user_agent,
        url = link
    )
    
    upload_event_to_azure(event)


def upload_event_to_azure(event):

    uploader = LogUploader()
    # TODO: Instantiate once - user many times
    uploader.send_request(
            data = [event.stringify()],
            table_name= "OutboundBrowsingEvents")