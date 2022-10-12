### for now we assume there is only one mail server
# TODO: model this as an object later
import random

from app.server.modules.authentication.authenticationEvent import AuthenticationEvent
from app.server.modules.organization.Company import Employee
from app.server.models import GameSession
from app.server.modules.clock.Clock import Clock 
from app.server.models import db
from app.server.utils import *

AUTH_RESULTS = ["Successful Login", "Failed Login"]

def auth_random_user_to_mail_server(employees:"list[Employee]", num_auth_events:int) -> None:
    """
    Get a random company user and have them login to the mail server
    """
    users = random.choices(employees, k=num_auth_events)
    #Get the current game session from the database
    # this should be centralized somewhere as well
    

    for user in users:
        # time is returned as timestamp (float)
        # can we abstract this as well?
        time = get_time()
        # during business hours, users login using internal IPs.
        #  During off-hourse, they login using home IPs
        if Clock.is_business_hours(time):
            auth_ip = user.ip_addr
        else:
            auth_ip = user.home_ip_addr

        auth_to_mail_server(
            timestamp=time,
            username=user.username,
            src_ip= auth_ip,
            user_agent=user.user_agent,
            result= random.choice(AUTH_RESULTS)
        )


def auth_user_to_mail_server(user: Employee, num_auth_events:int) -> None:
    """
    Tske a given user and have them login ot the mail server
    """
    for _ in range(num_auth_events):
        time = get_time()
        # auths happen anywhere from one hour to one week ago
        time_since_auth = random.randint(3600, 604800) * -1
        time = Clock.increment_time(time, time_since_auth)
        
        if Clock.is_business_hours(time):
            auth_ip = user.ip_addr
        else:
            auth_ip = user.home_ip_addr

        auth_to_mail_server(
            timestamp=time,
            username=user.username,
            src_ip= auth_ip,
            user_agent=user.user_agent,
            result= random.choice(AUTH_RESULTS)
        )
    



def auth_to_mail_server( timestamp:float, username:str, src_ip:str, user_agent:str, result:str) -> None:

    auth_event =  AuthenticationEvent(
        timestamp= timestamp,
        hostname="MAIL-SERVER01",
        username= username,
        src_ip= src_ip,
        user_agent= user_agent,
        result=result
    )

    upload_auth_event_to_azure(auth_event)


def upload_auth_event_to_azure(auth_event: AuthenticationEvent):
    # TODO: Let's abstract these. We have them strewn everywhere and its a bit chaotic
    from app.server.game_functions import LOG_UPLOADER
    LOG_UPLOADER.send_request(
            data = auth_event.stringify(),
            table_name= "AuthenticationEvents")


