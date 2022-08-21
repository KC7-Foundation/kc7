# Import external modules
import enum
import random
from datetime import datetime
from faker import Faker
from faker.providers import internet, lorem


# Import internal modules
from app.server.models import *
from app.server.modules.clock.Clock import Clock

# instantiate faker
fake = Faker()
fake.add_provider(internet)
fake.add_provider(lorem)

class Email:

    def __init__(self, sender, recipient, subject, time=None, authenticity=None, accepted=True, link=None, reply_to=None, opened=False):

        self.time = time or datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
        self.subject = subject
        self.sender = sender
        self.recipient = recipient
        self.opened = opened
        self.authenticity = authenticity # How convincing is the email?

        self.link = link
        
        if not accepted:
            self.accepted = random.choice([True, False])
        else:
            self.accepted = accepted

        if not link:
            self.link = fake.uri()
        else:
            self.link = link

        if not reply_to:
            self.reply_to = sender
        else:
            self.reply_to = reply_to

        if not authenticity:
            self.authenticity = random.randint(30, 100)
        else:
            self.authenticity = authenticity
            
    def stringify(self):
        """return json object with email attributes"""
        # if time is a timestamp convert to datetime string
        if isinstance(self.time, float):
            time_str = Clock.from_timestamp_to_string(self.time)
        else:
            time_str = self.time

        return {
            "event_time": time_str,
            "sender": self.sender,
            "reply_to": self.reply_to,
            "recipient": self.recipient,
            "subject": self.subject,
            "accepted": self.accepted,
            "link": self.link
        }
    
 