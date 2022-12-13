### for now we assume there is only one mail server
# TODO: model this as an object later
import random
import uuid
from faker import Faker
from faker.providers import user_agent

from app.server.modules.authentication.authenticationEvent import AuthenticationEvent
from app.server.modules.organization.Company import Employee
from app.server.models import GameSession
from app.server.modules.clock.Clock import Clock 
from app.server.models import db
from app.server.utils import *

AUTH_RESULTS = ["Successful Login", "Failed Login"]

# instantiate faker
fake = Faker()
fake.add_provider(user_agent)

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

        auth_result = random.choice(AUTH_RESULTS)
        if auth_result == "Successful Login":
            password = f"{user.username}2023"
        else:
            # Get a random password (that is incorrect) if we have an unsuccessful login
            password = f"{uuid.uuid4()}"

        auth_to_mail_server(
            timestamp=time,
            username=user.username,
            src_ip= auth_ip,
            user_agent=user.user_agent,
            result= random.choice(AUTH_RESULTS),
            password=password
        )

def actor_password_spray(actor: Actor, num_employees:int = 25, num_passwords:int = 5) -> None:
    """
    Launches a password spray attack from a given actor given a specific actor
    """
    from app.server.modules.triggers.Trigger import Trigger

    spray_time = get_time()

    # target user with a particular role
    # TODO: abstract this out to the actor
    targeted_employees = random.choices(get_employees(role="IT associate"), k=num_employees)

    spray_passwords = [f"{uuid.uuid4()}" for _ in range(num_passwords)]

    # user agent should be actor specific  
    # TODO: abstract this out to the actor
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0" 

    actor_ip = actor.get_ips(count_of_ips=1)[0]

    print(f"spraying {num_employees} using {num_passwords} passwords")
    for password in spray_passwords:
        for employee in targeted_employees:
            result = random.choices(["Successful Login","Failed Login"],weights=[5, 95])[0]
            auth_to_mail_server(
                timestamp=spray_time,
                username=employee.username,
                src_ip=fake.ipv4_public() ,
                user_agent=user_agent,
                result=result,
                password=password
            )
            spray_time = Clock.delay_time_by(spray_time, "seconds")

            if "Success" in result:
                login_time = Clock.delay_time_by(spray_time, factor="hours")
                Trigger.actor_downloads_files_from_email(recipient=employee.username, src_ip=actor_ip, time=login_time)
            

def auth_user_to_mail_server(user: Employee, num_auth_events:int) -> None:
    """
    Tske a given user and have them login ot the mail server
    """
    # TODO: Possible deprecation? This isn't getting used anywhere.
    for _ in range(num_auth_events):
        time = get_time()
        # auths happen anywhere from one hour to one week ago
        time_since_auth = random.randint(3600, 604800) * -1
        time = Clock.increment_time(time, time_since_auth)
        
        if Clock.is_business_hours(time):
            auth_ip = user.ip_addr
        else:
            auth_ip = user.home_ip_addr

        auth_result = random.choice(AUTH_RESULTS)
        if auth_result == "Successful Login":
            password = f"{user.username}2023"
        else:
            # Get a random password (that is incorrect) if we have an unsuccessful login
            password = f"{uuid.uuid4()}"

        auth_to_mail_server(
            timestamp=time,
            username=user.username,
            src_ip= auth_ip,
            user_agent=user.user_agent,
            result= random.choice(AUTH_RESULTS),
            password=password
        )
    



def auth_to_mail_server( timestamp:float, username:str, src_ip:str, user_agent:str, result:str, password:str) -> None:

    auth_event =  AuthenticationEvent(
        timestamp= timestamp,
        hostname="MAIL-SERVER01",
        username= username,
        src_ip= src_ip,
        user_agent= user_agent,
        result=result, 
        password=password
    )

    upload_auth_event_to_azure(auth_event)


def upload_auth_event_to_azure(auth_event: AuthenticationEvent):
    # TODO: Let's abstract these. We have them strewn everywhere and its a bit chaotic
    from app.server.game_functions import LOG_UPLOADER
    LOG_UPLOADER.send_request(
            data = auth_event.stringify(),
            table_name= "AuthenticationEvents")


