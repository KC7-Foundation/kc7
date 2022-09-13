# Import external modules
import enum
import random
from datetime import datetime
from unicodedata import name
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
    """
    A class that defines the data model for an email
    """

    def __init__(self, sender: str, recipient: str, subject: str, time: float = None, authenticity: int = None,
                 accepted: bool = True, link: str = None, domain: str = "", reply_to: str = None, opened: bool = False, actor: Actor = None):

        self.time = time or datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
        self.subject = subject
        self.sender = sender
        self.recipient = recipient
        self.opened = opened
        self.authenticity = authenticity  # How convincing is the email?
        self.domain = domain
        self.link = link
        self.actor = actor

        if not accepted:
            self.accepted = random.choice([True, False])
        else:
            self.accepted = accepted

        if not link:
            # this should not occur
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

    def stringify(self) -> "dict[str, str]":
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

    @staticmethod
    def get_kql_repr() -> "tuple[str, dict[str,str]]":
        return (
            "Email", {
                "event_time": "string",
                "sender": "string",
                "reply_to": "string",
                "recipient": "string",
                "subject": "string",
                "accepted": "bool",
                "link": "string"
            }
        )
