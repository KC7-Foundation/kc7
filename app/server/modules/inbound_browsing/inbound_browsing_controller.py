
# Import external modules
import random
from faker import Faker
import urllib.parse
from enum import Enum


from faker.providers import user_agent, internet
from app.server.utils import *
from app.server.modules.inbound_browsing.inboundEvent import InboundBrowsingEvent
from app.server.modules.helpers.markov_sentence_generator import SentenceGenerator
from app.server.modules.clock.Clock import Clock
from app.server.modules.constants.constants import *
 
#  instantiate faker
fake = Faker()
fake.add_provider(user_agent)
fake.add_provider(internet)
STATUS_CODES = ["200", "301", "404", "500"]
sentenceGenerator = SentenceGenerator()


class BrowsingType(Enum):
    """
    An enum to describe types of email that can be sent
    """
    STATIC = 1
    BLOG = 2
    MAIL = 3
    SEARCH = 4
    OTHER = 5

def gen_inbound_browsing_activity(actor: Actor, num_inbound_browsing_events:int=10) -> None:
    """
    Generate browsing to the company's website by random users
    This is background noise
    """
    for _ in range(num_inbound_browsing_events):

        # Choose an IP for the browsing
        # If non-default actor, then choose an actor IP as the source
        if actor.is_default_actor:
            src_ip = fake.ipv4_public()
        else:
            src_ip = actor.get_ips(count_of_ips=1)[0]
        status_code = random.choice(STATUS_CODES)
        method = "GET"

        # Generate a random sentence to be used for blog or search term
        random_sentence =  sentenceGenerator.gen_sentence_nopunc()

        # URI Path should be one of three things (for now)
        # Browsing to static page on company website
        # browsing to dynamic uri on blog of website
        # downloading file from mailserver (this will serve to hide our exfil for now)

        browsing_type = random.choices(population = [t.value for t in BrowsingType], weights=(47, 30, 3, 10, 10), k=1)[0]
        if browsing_type == BrowsingType.STATIC.value:
            uri_path = random.choice(WEBSITE_STATIC_PATHS)
        elif browsing_type == BrowsingType.BLOG.value:
            blog_title = random_sentence.replace(" ", "-").lower()
            uri_path = "blog/" + blog_title
        elif browsing_type == BrowsingType.MAIL.value and not actor.is_default_actor:
            # We do not want random mail browsing for malicious actor
            employee = get_random_employee()
            src_ip = employee.home_ip_addr  #overide this value with the employee's home IP 
            uri_path = make_email_exfil_url(employee.username, add_prefix=False)
        elif browsing_type == BrowsingType.SEARCH.value:
            if actor.get_recon_search_terms():
                search_term = random.choice(actor.get_recon_search_terms())
            else:
                search_term = random_sentence
            uri_path = f"search?query={urllib.parse.quote(search_term)}"
        else:
            uri_path = get_uri_path(uri_type="browsing")
        
        url = random.choice(["http://", "https://", ""]) + get_company().domain + "/" + uri_path
        time = get_time()

        gen_inbound_request(time, src_ip, method, status_code, url)


def gen_inbound_request(time:float, src_ip:str, method:str, status_code:str, url:str, user_agent:str=None) -> None:
    """
    Instatiate an inboundEvent and write it to logs
    """

    browsing_event = InboundBrowsingEvent(
        time=time,
        src_ip=src_ip,
        method=method,
        user_agent=user_agent,
        status_code=status_code,
        url=url
    )

    upload_event_to_azure(browsing_event)

def make_email_exfil_url(targeted_user: str, add_prefix:bool=True) -> str:
    """
    Takes a targeted user as a parameter and returns a URL indicative of email exfil
    """

    company_domain = get_company().domain

    # add domain to the prefix
    if add_prefix:
        prefix = random.choice(["http","https"]) + "://" + company_domain + "/"
    else:
        prefix = ""

    mailbox_folder = urllib.parse.quote(random.choice(EMAIL_EXFIL_MAILBOX_FOLDER_NAMES))
    output_file = urllib.parse.quote(f"{random.choice(EMAIL_EXFIL_OUTPUT_FILENAMES)}.{random.choice(EMAIL_EXFIL_OUTPUT_EXTENSIONS)}")

    # Example URL = "https://mail.acme.com/readmail?login_user=jdoe@acme.com&mailbox_folder=Inbox&download=true&output=contents.rar"
    return f"{prefix}mail/readmail?login_user={targeted_user}%40{company_domain}&mailbox_folder={mailbox_folder}&download=true&output={output_file}"


def upload_event_to_azure(event):

    from app.server.game_functions import LOG_UPLOADER
    LOG_UPLOADER.send_request(
            data = [event.stringify()],
            table_name= "InboundBrowsing")
