import random
import string
from datetime import datetime

from faker import Faker
from faker.providers import internet
from faker.providers import user_agent
from app.server.modules.clock.Clock import Clock
# instantiate faker
fake = Faker()
fake.add_provider(internet)

METHODS = ["GET", "POST"]
STATUS_CODES = ["202", "301", "302", "404", "403"]


class OutboundEvent:
    """
    Outbound Web browsing events. Represents an egress event 
    """

    def __init__(self, time:float, src_ip:str, user_agent:str, url:str):
        """Set initial values"""

        self.time = Clock.from_timestamp_to_string(time)
        self.src_ip = src_ip
        self.user_agent = user_agent
        self.set_method()
        self.set_status_code()

        self.url = url or fake.uri()


    def set_method(self):
        """
        Request method
        e.g. GET, POST PUT
        Currently limited to GET ONLY
        """
        self.method = random.choice(METHODS)

    def set_status_code(self):
        """
        Result of the request
        Chosen randomly from status codes defined above
        """
        self.status_code = random.choice(STATUS_CODES)

    def stringify(self):
        """Return event in json format"""    
        return  {
                  "timestamp": self.time, 
                  "method": self.method, 
                  "src_ip": self.src_ip, 
                  "user_agent":self.user_agent,
                  "url": self.url
            }


    @staticmethod
    def get_kql_repr():
        return (
            "OutboundBrowsing",         # table name
            {                           # type dict
                  "timestamp": "string",
                  "method": "string",
                  "src_ip": "string",
                  "user_agent":"string",
                  "url": "string"
            }
        )