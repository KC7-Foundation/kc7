# Import internal modules
from app.server.models import db
from app.server.modules.helpers.word_generator import WordGenerator
from app.server.modules.actors.Actor import Actor
from app.server.modules.organization.Company import Company, Employee
from app.server.modules.clock.Clock import Clock 
from app.server.models import GameSession

# Import external modules
from fileinput import filename
from enum import Enum
import random
from faker import Faker
from faker.providers import internet, lorem, file
from itsdangerous import base64_encode
import string
from functools import wraps
from time import time
import names

# instantiate faker
fake = Faker()
fake.add_provider(internet)
fake.add_provider(file)
fake.add_provider(lorem)

# instantiate word genertor
wordGenerator = WordGenerator()


class AttackTypes(Enum):
    """
    An enum to describe types of attacks that cna be conducted by an actor
    """
    PHISHING_VIA_EMAIL              = "email:phishing"
    MALWARE_VIA_EMAIL               = "email:malware_delivery"
    SUPPLY_CHAIN_VIA_EMAIL          = "delivery:supply_chain"
    PASSWORD_SPRAY                  = "identity:password_spray"
    RECONNAISSANCE_VIA_BROWSING     = "recon:browsing"
    MALWARE_VIA_WATERING_HOLE       = "watering_hole:malware_delivery"
    PHISHING_VIA_WATERING_HOLE      = "watering_hole:phishing"


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print(f"function {f.__name__} took: {te-ts}")
        # print 'func:%r args:[%r, %r] took: %2.4f sec' % (f.__name__, args, kw, te-ts)
        return result
    return wrap

# @timing
def get_link(actor:Actor, actor_domains:"list[str]", return_domain:bool=False) -> str:
    """Get a link containing actor's domain"""

    domain = random.choice(actor_domains)

    try:
        uri_type = random.choice(actor.get_attacks_by_type("email"))
    except IndexError:
        all_uri_types = ["browsing", "phishing", "malware_delivery"]
        uri_type = random.choice(all_uri_types)

    link = random.choice(["http://", "https://"]) + domain + "/" + get_uri_path(uri_type=uri_type, actor=actor)
    
    # return both the links and the domain - 
    # so that we can access the domain without having to do a weird regex
    if return_domain:
        return link, domain
    return link



def get_uri_path(max_depth:int=6, max_params:int=14, uri_type:str="browsing", actor:Actor=None) -> str:
    """
    Generate a uri_path: either browsing uri or path uri (for file downloads)
    browsing uri example: 
        - http://campaignandshould.us/public/share/files?type=protect?tracking=evening?id=discuss?user=board?type=marriage?query=P
    path uri example:
        - https://decisiondecision.biz/online/published/published/files/public/runner.xls
    auth uri example
        - google.com/login

    NOTE: This function is poorly optimized due to repeated iterations for URL generation. Can we make this more efficient?
    """
    uri_path = ""

    dir_words = ['share','files','search','published','online','images','modules','public']

    # Define constants for browsing-type
    param_names = ['query','source','id','keyword', 'search', 'user','uid','aid','tracking','type']
    param_values = wordGenerator.get_words(100)

    login_paths = ['login', 'login.html', 'signin', 'sign_in', 'enter','login?language=en', 'auth']

   
    # Generate these using faker
    file_names = param_values
    file_extensions = ['zip','rar','docx','7z','pptx', 'xls','exe']
    
    # Overide default filenames if new ones provided in config
    if actor and actor.get_file_names():
        file_names = actor.get_file_names()
    else:
        # Randomly append filenames
        file_names = [f"{file_name}.{random.choice(file_extensions)}" for file_name in file_names]

    # Generate the URL
    for i in range(random.randint(1,max_depth)):
        if i > 0:
            # if this isn't the first dir, add a slash to the end
            uri_path += "/"

        dir_word = random.choice(dir_words)
        uri_path += f"{dir_word}"
            
    if uri_type == "browsing":
        for _ in range(random.randint(1,max_params)):
            param_name = random.choice(param_names)
            param_value = random.choice(param_values)
            uri_path += f"?{param_name}={param_value}"
    elif uri_type == "malware_delivery":
        file_name = random.choice(file_names)
        uri_path += f"/{file_name}"
    elif uri_type == "phishing":
        # crude but will do for now
        uri_path += f"/{random.choice(login_paths)}"
    return uri_path


def get_employees(roles_list=None, count=0) -> "list[Employee]":
    """
    Get a list of employees and conditionally query by a role (other colums can be implemented later)
    """
    if isinstance(roles_list, str):
        roles_list = [roles_list]

    if roles_list:
        # filter by this rle
        employees = [
            employee for employee in
            Employee.query.filter(Employee.role.in_(roles_list)).all()
        ]

        if len(employees) == 0:
            # no employees were found after filtering
            employees = [employee for employee in Employee.query.all()]
    else:
        employees = [employee for employee in Employee.query.all()]

    if count:
        return random.choices(employees, k=count)

    return employees


def get_random_employee() -> Employee:
    """
    Return a random employee object
    """
    return random.choice(get_employees(count=1))


def get_company() -> Company:
    return Company.query.first()


def get_actors() -> "list[Actor]":
    return Actor.query.all()


def get_email_prefix() -> str:
    return "_".join(names.get_full_name().split(" ")).lower()

def write_seed_files(max_num_files: int = 25):
    eicar_string = 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
    for i in range(1, max_num_files):
        file_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))+random.choice(['.exe','.dll','.dat'])
        unique_string = f"Welcome to KC7, the cybersecurity game. If you're a player, congrats! You found malware file {file_name}. If you aren't a player... how'd you find us? Visit kc7cyber.com to learn more!"
        file_string = eicar_string + "\n\n\n" + base64_encode(unique_string).decode("utf-8")

        file = open("output/"+file_name,"w")
        file.write(file_string)

# Yield successive n-sized
# chunks from l.
def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]