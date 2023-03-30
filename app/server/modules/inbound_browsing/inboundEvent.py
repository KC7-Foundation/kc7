
# Import external modules
import random
from faker import Faker
from faker.providers import user_agent

from app.server.modules.clock.Clock import Clock

#  instantiate faker
fake = Faker()
fake.add_provider(user_agent)
STATUS_CODES = ["202", "301", "302", "404", "403"]


class InboundBrowsingEvent:
    """
    Inbound Server connection events. Represents an ingress event 
    Connection could be to one of many server
    """

    def __init__(self, time:float, src_ip:str, url:str, status_code:str, method:str, user_agent:str=None) -> None:

        self.time = Clock.from_timestamp_to_string(time)
        self.src_ip = src_ip
        self.user_agent = user_agent or fake.firefox()
        self.url = url
        self.method = method
        self.status_code = status_code or random.choice(STATUS_CODES)


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
            "InboundNetworkEvents",         # table name
            {                           # type dict
                  "timestamp": "datetime",
                  "method": "string",
                  "src_ip": "string",
                  "user_agent":"string",
                  "url": "string"
            }
        )