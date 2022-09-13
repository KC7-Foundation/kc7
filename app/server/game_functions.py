import yaml 
import glob

from flask_security import roles_required

from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, abort, current_app, jsonify
from sqlalchemy import asc
from  sqlalchemy.sql.expression import func, select

# Import module models (i.e. Company, Employee, Actor, DNSRecord)
from app.server.models import db, Company, Employee, Actor, DNSRecord, Team, Users, Roles, GameSession
from app.server.modules.organization.Company import CompanyShell, EmployeeShell
from app.server.modules.organization.company_controller import create_company
from app.server.modules.clock.Clock import Clock
from app.server.modules.logging.uploadLogs import LogUploader
from app.server.modules.email.email_controller import gen_email
from app.server.modules.outbound_browsing.browsing_controller import *
from app.server.modules.outbound_browsing.browsing_controller import browse_random_website
from app.server.modules.infrastructure.passiveDNS_controller import *
from app.server.utils import *



def start_game():
    """
    1. Get the game session
    2. Generate starter data
    3. Run infinite loop to generate additional activity
    """
    global log_uploader
    # The game session is a database table
    # The current game is session (1) - could probably do this better later

    # Create tables in Kusto as necessary
    print("Starting the game...")

    log_uploader = LogUploader()
    log_uploader.create_tables(reset=True)

    current_session = db.session.query(GameSession).get(1)
    current_session.state = True

    # instantiate the clock
    print(f"Game started at {current_session.start_time}")

    # TODO: allow users ot modify start time in the web UI
    db.session.commit()
    
    # run startup functions 
    employees = Employee.query.all()
    actors = Actor.query.all()
    if not (employees or actors):
        print(employees)
        print(actors)
        employees, actors  = init_setup()
    

    # (actor, employees, num_passive_dns, num_email, num_random_browsing
    print("initialization complete...")

    while current_session.state == True:

        

        # generate the activity
        for actor in actors: 
            if actor.name == "Default":
                generate_activity(actor, employees, num_passive_dns=10, num_email=10, num_random_browsing=5) 
            else:
                generate_activity(actor, employees, num_passive_dns=1, num_email=2, num_random_browsing=3) 

    #     # Update the scores for each team
        #   teams = Team.query.all()
    #     for team in teams:
    #         team.score += 1000

    #         count_mitigations = len(team._mitigations)
    #         mitigation_cost = count_mitigations 
    #         team.score -= mitigation_cost

    #     db.session.commit()
    #     print("updated team scores")
        # time.sleep(5)  #do this when liv
    

def init_setup():
    """
    Create company
    Create default actor
    Create Malicious Actors
    Create first batch of legit passive DNS
    Create first batch of malicious passive DNS
    """
    employees = Employee.query.all()
    actors = Actor.query.all()

    if not employees:
        create_company()
        employees = Employee.query.all()
    if not actors:
        create_actors()
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
    all_dns_records = [d.stringify() for d in all_dns_records]
    upload_dns_records_to_azure(all_dns_records)

    return employees, actors

    
def generate_activity(actor, employees, num_passive_dns:int, num_email:int, num_random_browsing:int):
    """
    Given an actor, enerates one cycle of activity for users in the orgs
    Current:
        - Generate Email
        - Generate Web Browsing
        - General 
    """
    print(f"generating activity for actor {actor.name}")
    # Generate passive DNS for specified actor
    gen_passive_dns(actor, num_passive_dns)

    # Generate emails for random employees for specified actor
    for i in range(num_email):
        gen_email(employees, actor)

    # for i in range(num_email):
        # gen_email(employees, actor)

    # Generate browsing activity for random emplyoees for the default actor
    # browsing for other actors should only come through email clicks
    current_session = db.session.query(GameSession).get(1)

    if actor.name == "Default":
        for i in range(num_random_browsing):
            employee = random.choice(employees)

            # time is returned as timestamp (float)
            time = Clock.get_current_gametime(start_time=current_session.start_time,
                                                    seed_date=current_session.seed_date)

            browse_random_website(employee, actor, time)



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
        count_init_browsing=10,
        domain_themes = wordGenerator.get_words(100),
        sender_themes = wordGenerator.get_words(100)
    )

    # load add default_actor
    actors = [default_actor]

    # use yaml configs to load other actors
    actor_configs = glob.glob("app/actor_configs/*.yaml") 
    for file in actor_configs:
        actor_config = read_actor_config_from_yaml(file)
        # use dictionary value to instantiate actor
        if actor_config:
            print(f"adding actor: {actor_config}")
            actors.append(
                Actor(**actor_config)
            )

    try:
        for actor in actors:
            db.session.add(actor)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Failed to create actor %s" % e)


def read_actor_config_from_yaml(filename):
    """Read actor_config from file. Return none if somethign goes wrong"""
    with open(filename, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            return None
            print(exc)