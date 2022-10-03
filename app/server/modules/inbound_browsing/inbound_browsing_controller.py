
# Import external modules
import random
from faker import Faker
import urllib.parse

from faker.providers import user_agent, internet
from app.server.utils import *
from app.server.modules.inbound_browsing.inboundEvent import InboundBrowsingEvent
from app.server.modules.clock.Clock import Clock
from app.server.modules.constants.constants import *

#  instantiate faker
fake = Faker()
fake.add_provider(user_agent)
fake.add_provider(internet)
STATUS_CODES = ["200", "301", "404", "500"]

def gen_random_inbound_browsing(num_inbound_browsing_events:int=10) -> None:
    """
    Generate browsing to the company's website by random users
    This is background noise
    """
    src_ip = fake.ipv4_public()
    status_code = random.choice(STATUS_CODES)
    method = "GET"
    
    url = random.choice(["http://", "https://", ""]) + get_company().domain + "/" + get_uri_path(uri_type="browsing")
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

def make_email_exfil_url(targeted_user: str) -> str:
    """
    Takes a targeted user as a parameter and returns a URL indicative of email exfil
    """

    company_domain = get_company().domain
    # Use urllib.parse.quote() to URL-encode parameter values
    prefix = random.choice(["http","https"])
    mailbox_folder = urllib.parse.quote(random.choice(EMAIL_EXFIL_MAILBOX_FOLDER_NAMES))
    output_file = urllib.parse.quote(f"{random.choice(EMAIL_EXFIL_OUTPUT_FILENAMES)}.{random.choice(EMAIL_EXFIL_OUTPUT_EXTENSIONS)}")

    # Example URL = "https://mail.acme.com/readmail?login_user=jdoe@acme.com&mailbox_folder=Inbox&download=true&output=contents.rar"
    return f"{prefix}://mail.{company_domain}/readmail?login_user={targeted_user}%40{company_domain}&mailbox_folder={mailbox_folder}&download=true&output={output_file}"

def upload_event_to_azure(event):

    from app.server.game_functions import LOG_UPLOADER
    LOG_UPLOADER.send_request(
            data = [event.stringify()],
            table_name= "InboundBrowsing")
