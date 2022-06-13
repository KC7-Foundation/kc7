import random
from faker import Faker
from faker.providers import internet, lorem

from app.server.models import db, Company, Employee, Actor, DNSRecord

# instantiate faker
fake = Faker()
fake.add_provider(internet)

def get_link(actor):
    """Get a link containing actor's IP"""

    dns_records = [record for record in actor.dns_records]
    dns_record = random.choice(dns_records)
    dns_record.active = True  # set record to active so we can track which domains have been used
    domain = dns_record.domain

    link = random.choice(["http://", "https://", ""]) + domain + "/" + fake.uri_path()
    return link



def get_employees():
    employees = [employee for employee in Employee.query.all()]
    return employees

