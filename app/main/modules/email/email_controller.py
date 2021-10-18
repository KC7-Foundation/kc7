# Import external modules
from enum import Enum
import random
from faker import Faker
from faker.providers import internet, lorem


# Import internal modules
from flask import current_app
from app.main.models import *
from app.main.modules.email.email import Email
from app.main.modules.outbound_browsing.browsing_controller import browse_website
from app.main.modules.logging.uploadLogs import LogUploader
from app.main.utils import *

# instantiate faker
fake = Faker()
fake.add_provider(internet)
fake.add_provider(lorem)

class EmailType(Enum):
    """
    An enum to describe types of email that can be sent
    """
    INBOUND = 1,
    OUTBOUND = 2,
    INTERNAL = 3

INTERNAL_EMAIL_AUTHENTICITY = 95
DEFAULT_ACTOR_NAME = "Default"

def get_random_actor():
    """Return a random actor from the database"""
    pass

# def get_random_user():
#     """Return a random employee from the database"""
#     # TODO: get an employee that is actually random
#     num  = randin(1,2)
#     # get either the first or second user
#     user = Employee.query.get(num)
#     return user

def gen_email(employees, actor):
    """
    Make a call to the Azure email function
    to create an email, post to log analytics
    and send a secondary request to generate browsing traffic
    """
    #print(f"Creating email for actor {actor.name}")
    # If the actor is a malicious one, we will always generate an inbound email (external -> internal)
    if actor.name == DEFAULT_ACTOR_NAME:
        email_type = random.choice([t.value for t in EmailType])
    else:
        
        email_type = EmailType.INBOUND.value

    # Depending on the email type selected, call a different function
    if email_type == EmailType.INBOUND.value:
        recipient = random.choice(employees)
        gen_inbound_mail(recipient, actor)

    elif email_type == EmailType.OUTBOUND.value:
        sender = random.choice(employees)
        gen_outbound_mail(sender, actor)

    elif email_type == EmailType.INTERNAL.value:
        sender = random.choice(employees)
        recipient = random.choice(employees)
        gen_internal_mail(sender, recipient, actor)


def gen_inbound_mail(recipient, actor):
    """
    Generate an email from someone outside the company to someone inside
    """
    link = get_link(actor)
    sender = actor.get_sender_address()
    reply_to = actor.get_sender_address() if actor.spoof_email else sender

    email = Email(
        sender = actor.get_sender_address(),
        recipient = recipient.email_addr,
        subject = actor.get_email_subject(),
        reply_to = reply_to,
        link = link,
        accepted = random.choices([True, False], weights=(80, 20), k=1)[0],
        authenticity = actor.effectiveness
    )

    send_email_to_azure(email)

    if email.authenticity >= recipient.awareness:
        browse_website(recipient, link)
        # TODO: Generate a logon attempt for the recipient (random success/fail rate??)
        #print(f"The user {recipient.name} opened this email!")

def gen_outbound_mail(sender, actor):
    """
    Generate an email from someone inside the company to someone outside
    """
    email = Email(
        sender = sender.email_addr,
        recipient = fake.ascii_email(),
        subject = actor.get_email_subject(),
        link = get_link(actor),
        accepted=True
    )

    send_email_to_azure(email)

def gen_internal_mail(sender, recipient, actor):
    """
    Generate mail from someone inside the company to someone else in the company
    """
    email = Email(
        sender = sender.email_addr,
        recipient = recipient.email_addr,
        subject = actor.get_email_subject(),
        link = get_link(actor),
        accepted=True,
        authenticity=INTERNAL_EMAIL_AUTHENTICITY
    )

    send_email_to_azure(email)

def send_email_to_azure(email):

    uploader = LogUploader(
        log_type= current_app.config["LOG_PREFIX"] + "_EmailLogs",
        data = [email.stringify()]
    )

    uploader.send_request()