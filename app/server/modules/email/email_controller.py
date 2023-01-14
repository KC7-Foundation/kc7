# Import external modules
from enum import Enum
import random
from faker import Faker
from faker.providers import internet, lorem
import names


# Import internal modules
from flask import current_app
from app.server.models import *
from app.server.modules.email.email import Email
from app.server.modules.outbound_browsing.browsing_controller import browse_website
from app.server.modules.logging.uploadLogs import LogUploader
from app.server.modules.clock.Clock import Clock
from app.server.modules.triggers.Trigger import Trigger
from app.server.modules.actors.Actor import Actor
from app.server.modules.organization.Company import Company, Employee
from app.server.utils import *

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
    INTERNAL = 3,
    PARTNER = 4


INTERNAL_EMAIL_AUTHENTICITY = 95
PARTNER_EMAIL_AUTHENTICITY = 90
DEFAULT_ACTOR_NAME = "Default"


def get_random_actor():
    """Return a random actor from the database"""
    pass

def gen_email(employees: "list[Employee]", partners: "list[str]", actor: Actor, count_emails:int) -> None:
    """
    Make a call to the Azure email function
    to create an email, post to log analytics
    and send a secondary request to generate browsing traffic
    """

    actor_domains = [record.domain for record in actor.dns_records]

    for _ in range(count_emails):
        # time is returned as timestamp (float)
        time = get_time()

        # If the actor is default, we'll randomly pick an email type
        if actor.is_default_actor:
            email_type = random.choice([t.value for t in EmailType])
        else:
            email_type = EmailType.INBOUND.value

        # Depending on the email type selected, call a different function
        if email_type == EmailType.INBOUND.value:
            wave_size = random.randint(1, actor.max_wave_size)
            recipients = random.choices(employees, k=wave_size)
            gen_inbound_mail(recipients, actor, actor_domains, time )

        elif email_type == EmailType.OUTBOUND.value:
            sender = random.choice(employees)
            gen_outbound_mail(sender, actor, actor_domains, time)

        elif email_type == EmailType.INTERNAL.value:
            sender = random.choice(employees)
            recipient = random.choice(employees)
            gen_internal_mail(sender, recipient, actor, actor_domains, time)

        elif email_type == EmailType.PARTNER.value:
            partner_domain = random.choice(partners)
            employee = random.choice(employees)
            gen_partner_mail(employee, partner_domain, actor, actor_domains, time)
        


def gen_inbound_mail(recipients: "list[Employee]", actor: Actor, actor_domains:"list[str]", time: float) -> None:
    """
    Generate an email from someone outside the company to someone inside
    """
    link, domain = get_link(actor, actor_domains, return_domain=True)
    sender = actor.get_sender_address()
    reply_to = actor.get_sender_address() if actor.spoof_email else sender
    subject = actor.get_email_subject()

    for recipient in recipients:
        email = Email(
            time=time,
            sender=sender,
            recipient=recipient.email_addr,
            subject=subject,
            reply_to=reply_to,
            link=link,
            domain=domain,
            actor=actor,
            accepted=random.choices([True, False], weights=(70, 30), k=1)[0],
            authenticity=actor.effectiveness
        )

        send_email_to_azure(email)

        # Initiate the trigger for the recipient receiving the constructed email
        Trigger.user_receives_email(email, recipient)


def gen_outbound_mail(sender: Employee, actor: Actor, actor_domains:"list[str]", time: float) -> None:
    """
    Generate an email from someone inside the company to someone outside
    """
    email = Email(
        time=time,
        sender=sender.email_addr,
        recipient=fake.ascii_email(),
        subject=actor.get_email_subject(),
        link=get_link(actor, actor_domains=actor_domains),
        accepted=True
    )

    send_email_to_azure(email)


def gen_internal_mail(sender: Employee, recipient: Employee, actor: Actor, actor_domains:"list[str]", time: float) -> None:
    """
    Generate mail from someone inside the company to someone else in the company
    """
    email = Email(
        time=time,
        sender=sender.email_addr,
        recipient=recipient.email_addr,
        subject=actor.get_email_subject(),
        link=get_link(actor, actor_domains=actor_domains),
        accepted=True,
        authenticity=INTERNAL_EMAIL_AUTHENTICITY
    )

    send_email_to_azure(email)

def gen_partner_mail(employee: Employee, partner_domain: str, actor: Actor, actor_domains:"list[str]", time: float) -> None:
    """
    Generates mail to/from one of the company's partner organizations
    """
    # Determine partner email directionality (inbound or outbound)
    directionality = random.choice([EmailType.INBOUND.value, EmailType.OUTBOUND.value])

    partner_email = f"{get_email_prefix()}@{partner_domain}"

    # Set the sender and recipient based on the directionality
    if directionality == EmailType.INBOUND.value:
        sender = partner_email
        recipient = employee.email_addr
    else:
        sender = employee.email_addr
        recipient = partner_email

    email = Email(
        time=time,
        sender=sender,
        recipient=recipient,
        subject=actor.get_email_subject(),
        link=get_link(actor, actor_domains),
        accepted=True,
        authenticity=PARTNER_EMAIL_AUTHENTICITY
    )

    send_email_to_azure(email)
    


def send_email_to_azure(email):
    """
    Upload email object to azure
    """
    from app.server.game_functions import LOG_UPLOADER

    LOG_UPLOADER.send_request(
        data=[email.stringify()],
        table_name="Email")
