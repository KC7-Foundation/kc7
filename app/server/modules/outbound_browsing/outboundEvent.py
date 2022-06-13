import random
import string

from faker import Faker
from faker.providers import internet
from faker.providers import user_agent

# instantiate faker
fake = Faker()
fake.add_provider(internet)

METHODS = ["GET", "POST"]
STATUS_CODES = ["202", "301", "302", "404", "403"]


class OutboundEvent:

    def __init__(self, time, src_ip, user_agent, url):
        """Set initial values"""
        self.time = time.strftime("%a %b %d %H:%M:%S %Y")
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
                  "time": self.time, 
                  "method": self.method, 
                  "src_ip": self.src_ip, 
                  "user_agent":self.user_agent,
                  "url": self.url
            }

