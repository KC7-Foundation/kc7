import time
import atexit

import json, random
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from faker import Faker
from faker.providers import internet, person, company

from flask import Blueprint, request, render_template, \
                  flash, g, redirect, url_for, abort
from sqlalchemy import asc
from  sqlalchemy.sql.expression import func, select

# Import module models (i.e. Company, Employee, Actor, DNSRecord)
from flask import current_app
from app.main.models import db, Company, Employee, Actor, DNSRecord
from app.main.modules.organization.Company import CompanyShell, EmployeeShell
from app.main.modules.organization.company_controller import create_company
from app.main.modules.logging.uploadLogs import LogUploader
from app.main.modules.email.email_controller import gen_email
from app.main.modules.outbound_browsing.browsing_controller import *
from app.main.modules.outbound_browsing.browsing_controller import browse_random_website
from app.main.modules.infrastructure.passiveDNS_controller import *
from app.main.utils import *
import time

# instantiate faker
fake = Faker()
fake.add_provider(internet)
fake.add_provider(person)
fake.add_provider(company)

# Define the blueprint: 'main', set its url prefix: app.url/
main = Blueprint('main', __name__)


@main.route("/")
def home():
    #api_result = send_request()

    # Start button
    # when pressed will create company and employees

    # run startup functions 
    employees, actors  = init_setup()
    
# (actor, employees, num_passive_dns, num_email, num_random_browsing
    print("initialization complete...")

    #while True:
    #    for actor in actors: 
    #        generate_activity(actor, employees, num_passive_dns=3, num_email=2,num_random_browsing=3) 
    #    time.sleep(2)
    

    return "hello world"

def init_setup():
    """
    Create company
    Create default actor
    Create Malicious Actors
    Create first batch of legit passive DNS
    Create first batch of malicious passive DNS
    """
    create_company()
    create_actors()

    employees = Employee.query.all()
    actors = Actor.query.all()
    for actor in actors:
        generate_activity(
                            actor, 
                            employees, 
                            num_passive_dns=actor.count_init_passive_dns, 
                            num_email=actor.count_init_email, 
                            num_random_browsing=actor.count_init_browsing
                        )
    
    all_dns_records = DNSRecord.query.all()
    random.shuffle(all_dns_records)
    upload_dns_records_to_azure(all_dns_records)

    return employees, actors
    
def generate_activity(actor, employees, num_passive_dns, num_email, num_random_browsing):
    print(f"generating activity for actor {actor.name}")
    # Generate passive DNS for specified actor
    gen_passive_dns(actor, num_passive_dns)

    # Generate emails for random employees for specified actor
    for i in range(num_email):
        gen_email(employees, actor)

    # Generate browsing activity for random emplyoees for specified actor
    for i in range(num_random_browsing):
        employee = random.choice(employees)
        browse_random_website(employee, actor)
    
        

def print_date_time():
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))



@main.route("/test")
def test():
    #api_result = send_request()

    create_company()
    #companies  = Company.query.all()
    #names = [company.name for company in companies]

    #create_actor()
    #actors = Actor.query.all()
    #names = [actor.name for actor in actors]
    create_actors()
    actors = Actor.query.all()
    names = [actor.spoof_email for actor in actors]

    gen_default_passiveDNS()
    gen_actor_passiveDNS()
    
    #default_actor = db.session.query(Actor).filter_by(name = "Default").one()
    viking_actor = db.session.query(Actor).filter_by(name = "Flying Purple Vikings").one()
    employees = get_employees()

    employee = random.choice(employees)
    for i in range(13):
        gen_email(viking_actor)
        #browse_random_website(employee, viking_actor)
    
    return json.dumps(names)




def create_actors():
    """
    Create a malicious actor
    Start with an actor shell
    use this to create a database object
    TODO: abstact the creation of actors
    """

    default_actor = Actor(
        name = "Default",
        effectiveness = 99,
        count_init_passive_dns= 10, 
        count_init_email= 10, 
        count_init_browsing=10
    )

    # This should come from a config later
    viking_actor = Actor(
        name = "Flying Purple Vikings",
        effectiveness = 50,
        domain_themes = " ".join([
            "viking", "thor", "hammer","norse","mountain", "thunder", "storm", "seas", "rowing", "axe"
        ]),
        sender_themes = " ".join([
            "odin", "loki", "asgard", "fenrir", "astrid", "jormungand", "freya"
        ]),
        subject_themes = " ".join([
            "security","alert","urgent", "grand", "banquet", ""    
        ]),
        tlds = " ".join([
             "info", "io"   
        ]),
        spoof_email= True
    )

    third_actor = Actor(
        name = "Myotheractor",
        effectiveness = "99"
    )

    # we can add more actors later
    actors = []
    actors.append(default_actor)
    actors.append(viking_actor)
    actors.append(third_actor)
    
    try:
        for actor in actors:
            db.session.add(actor)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Failed to create actor %s" % e)




