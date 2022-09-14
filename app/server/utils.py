# Import internal modules
from app.server.models import db, Company, Employee, DNSRecord
from app.server.modules.helpers.word_generator import WordGenerator
from app.server.modules.actors.Actor import Actor

# Import external modules
from fileinput import filename
import random
from faker import Faker
from faker.providers import internet, lorem, file

# instantiate faker
fake = Faker()
fake.add_provider(internet)
fake.add_provider(file)
fake.add_provider(lorem)

# instantiate word genertor
wordGenerator = WordGenerator()

def get_link(actor:Actor, return_domain:bool=False) -> str:
    """Get a link containing actor's domain"""

    dns_records = [record for record in actor.dns_records]
    dns_record = random.choice(dns_records)
    dns_record.active = True  # set record to active so we can track which domains have been used
    domain = dns_record.domain

    if actor.name == "Default":
        uri_type = random.choice(['file', 'browsing'])
    else:
        uri_type = 'file'

    link = random.choice(["http://", "https://", ""]) + domain + "/" + get_uri_path(uri_type=uri_type, actor=actor)
    
    # return both the links and the domain - 
    # so that we can access the domain without having to do a weird regex
    if return_domain:
        return link, domain
    return link



def get_uri_path(max_depth:int=6, max_params:int=14, uri_type="browsing", actor=Actor) -> str:
    """
    Generate a uri_path: either browsing uri or path uri (for file downloads)
    browsing uri example: 
        - http://campaignandshould.us/public/share/files?type=protect?tracking=evening?id=discuss?user=board?type=marriage?query=P
    path uri example:
        - https://decisiondecision.biz/online/published/published/files/public/runner.xls
    """
    uri_path = ""

    dir_words = ['share','files','search','published','online','images','modules','public']

    # Define constants for browsing-type
    param_names = ['query','source','id','keyword', 'search', 'user','uid','aid','tracking','type']
    param_values = wordGenerator.get_words(100)

   
    # Generate these using faker
    file_names = param_values
    file_extensions = ['zip','rar','docx','7z','pptx', 'xls','exe']
    
    # Overide default filenames if new ones provided in config
    if actor.get_file_names():
        file_names = actor.get_file_names()
    if actor.get_file_extensions():
        file_extensions = actor.get_file_extensions()


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
    elif uri_type == "file":
        file_name = random.choice(file_names)
        file_extension = random.choice(file_extensions)
        uri_path += f"/{file_name}.{file_extension}"
    return uri_path


def get_employees() -> list:
    employees = [employee for employee in Employee.query.all()]
    return employees




