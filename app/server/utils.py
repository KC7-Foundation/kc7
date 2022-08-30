import random
from faker import Faker
from faker.providers import internet, lorem

from app.server.models import db, Company, Employee, Actor, DNSRecord

# instantiate faker
fake = Faker()
fake.add_provider(internet)
fake.add_provider(lorem)

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

    link = random.choice(["http://", "https://", ""]) + domain + "/" + get_uri_path(uri_type=uri_type)
    
    # return both the links and the domain - 
    # so that we can access the domain without having to do a weird regex
    if return_domain:
        return link, domain
    return link

def get_uri_path(max_depth:int=6, max_params:int=14, uri_type="browsing") -> str:
    """
    Generate a uri_path: either browsing uri or path uri (for file downloads)
    """
    uri_path = ""

    dir_words = ['share','files','search','published','online','images','modules','public']

    # Define constants for browsing-type
    param_names = ['query','source','id','keyword', 'search', 'user','uid','aid','tracking','type']
    param_values = fake.paragraph(nb_sentences=20).replace(".", "").split(" ")

    # Define constants for file-type
    file_names = ['scvhost', 'dllhost', 'Runtimeexplorer', 'plink', 'runner', 'proposal', 'invoice', 'salutations', 'nigerian_uncle', 'russian_prince',
    'hello', 'wwlib','goopdate','Resume','putty','server','job_opportunity','job_offer', 'for_your_review', 'free_money']
    file_extensions = ['zip','rar','docx','dll','7z','pptx', 'xls', 'dotm','exe']

    for _ in range(random.randint(1,max_depth)):
        dir_word = random.choice(dir_words)
        uri_path += f"/{dir_word}"
            
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

