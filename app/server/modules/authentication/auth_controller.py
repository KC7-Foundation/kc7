### for now we assume there is only one mail server
# TODO: model this as an object later
import random

from app.server.modules.authentication.authenticationEvent import AuthenticationEvent
from app.server.modules.organization.Company import Employee
from app.server.models import GameSession
from app.server.modules.clock.Clock import Clock 
from app.server.models import db

def auth_random_user_to_mail_server(employees:"list[Employee]", num_auth_events:int) -> None:
    """
    Get a random company user and have them login to the mail server
    """

    users = random.choices(employees, k=num_auth_events)
    #Get the current game session from the database
    current_session = db.session.query(GameSession).get(1)
    # this should be centralized somewhere as well
    auth_results = ["Successful Login", "Failed Login"]

    for user in users:
        # time is returned as timestamp (float)
        # can we abstract this as well?
        time = Clock.get_current_gametime(start_time=current_session.start_time,
                                                seed_date=current_session.seed_date)

        # during business hours, users login using internal IPs.
        #  During off-hourse, they login using home IPs
        if Clock.is_business_hours(time):
            auth_ip = user.ip_addr
        else:
            auth_ip = user.home_ip_addr

        auth_to_mail_server(
            creation_time=time,
            username=user.username,
            src_ip= auth_ip,
            user_agent=user.user_agent,
            result= random.choice(auth_results)
        )



def auth_to_mail_server( creation_time:float, username:str, src_ip:str, user_agent:str, result:str) -> None:

    auth_event =  AuthenticationEvent(
        creation_time= creation_time,
        hostname="MAIL-SERVER01",
        username= username,
        src_ip= src_ip,
        user_agent= user_agent,
        result=result
    )

    upload_event_to_azure(auth_event)


def upload_event_to_azure(event):
    # TODO: Let's abstract these. We have them strewn everywhere and its a bit chaotic
    from app.server.game_functions import log_uploader
    log_uploader.send_request(
            data = event.stringify(),
            table_name= "AuthenticationEvents")


