from unittest.mock import NonCallableMagicMock
import yaml 
import glob

from flask_security import roles_required

from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, abort, current_app, jsonify
from sqlalchemy import asc
from  sqlalchemy.sql.expression import func, select

# Import module models (i.e. Company, Employee, Actor, DNSRecord)
from app.server.models import db, Team, Users, Roles, GameSession
from app.server.modules.organization.Company import Company, Employee
from app.server.modules.organization.company_controller import create_company
from app.server.modules.clock.Clock import Clock
from app.server.modules.logging.uploadLogs import LogUploader
from app.server.modules.email.email_controller import gen_email
from app.server.modules.outbound_browsing.browsing_controller import *
from app.server.modules.outbound_browsing.browsing_controller import browse_random_website
from app.server.modules.infrastructure.passiveDNS_controller import *
from app.server.modules.infrastructure.DNSRecord import DNSRecord
from app.server.modules.actors.Actor import Actor
from app.server.utils import *
from app.server.modules.helpers.markov_sentence_generator import SentenceGenerator



def start_game() -> None:
    """
    This function call starts the game

    1. Get the game session
    2. Generate starter data
    3. Run infinite loop to generate additional activity
    """
    print("Starting the game...")

    # instantiate a logUploader. This instance is used by all other modules to send logs to azure
    # we use a singular instances in order to queue up muliple rows of logs and send them all at once
    global log_uploader
    log_uploader = LogUploader()
    log_uploader.create_tables(reset=True)

    # The the current game session
    # This data object tracks whether or not the game is currently running
    # It allows us to start/stop/restart the game from the views
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
    
    print("initialization complete...")

    # This is where the action is
    # While this infinite loop runs, the game continues to generate data
    # To implement games of finite size -> bound this loop (e.g. use a for loop instead)
    print(current_session.state)
    while current_session.state == True:
        # generate the activity
        print("Running the game...")
        for actor in actors: 
            print(actor.name)
            if actor.name == "Default":
                # Default actor is used to create noise
                generate_activity(actor, 
                                 employees, 
                                 num_passive_dns=50, 
                                 num_email=100, 
                                 num_random_browsing=500) 
            else:
                # generate activity of actors defined in actor config
                generate_activity(actor, 
                                  employees, 
                                  num_passive_dns=1, 
                                  num_email=1, 
                                  num_random_browsing=3) 



def init_setup():
    """
    These actions are conducted at the start of a new game session

    Create company
    Create default actor
    Create Malicious Actors
    Create first batch of legit passive DNS
    Create first batch of malicious passive DNS
    """
    employees = Employee.query.all()
    actors = Actor.query.all()

    # only create employees for the company or actors 
    # if they do not already exist
    if not employees:
        create_company()
        employees = Employee.query.all()
    if not actors:
        create_actors()
        actors = Actor.query.all()
    
    # generate some initial activity for the actors
    for actor in actors:
        generate_activity(
                            actor, 
                            employees, 
                            num_passive_dns=actor.count_init_passive_dns, 
                            num_email=actor.count_init_email, 
                            num_random_browsing=actor.count_init_browsing
                        )
    
    all_dns_records = DNSRecord.query.all()
    # shuffle the dns records so that pivot points are not all next to each other in azure
    random.shuffle(all_dns_records)
    all_dns_records = [d.stringify() for d in all_dns_records]
    upload_dns_records_to_azure(all_dns_records)

    return employees, actors

    
def generate_activity(actor: Actor, employees: list, num_passive_dns:int, num_email:int, num_random_browsing:int) -> None:
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
    # TODO: handle number of emails generated in the function
    gen_email(employees, actor, num_email)

    # Generate browsing activity for random emplyoees for the default actor
    # browsing for other actors should only come through email clicks
    if actor.name == "Default":
        browse_random_website(employees, actor, num_random_browsing)



def create_actors() -> None:
    """
    Create a malicious actor in the game and adds them to the database
    Actors are read in from yaml files in the actor_configs folder

    TODO: there should be some validation of actor configs prior to creation
    """

    # instantial a default actor - this actor should always exist
    # the default actor is used to generate background noise in the game
    default_actor = Actor(
        name = "Default",  # Dont change the name!
        effectiveness = 99,
        count_init_passive_dns= 10, 
        count_init_email= 100, 
        count_init_browsing=100,
        domain_themes = wordGenerator.get_words(100),
        sender_themes = wordGenerator.get_words(100)
    )

    # load add default_actor
    actors = [default_actor]

    # use yaml configs to load other actors
    # read yaml file for each new actor, load json from yaml
    actor_configs = glob.glob("app/actor_configs/*.yaml") 
    for file in actor_configs:
        actor_config = read_actor_config_from_yaml(file)
        # use dictionary value to instantiate actor
        if actor_config:
            print(f"adding actor: {actor_config}")
            # use dict to instantiate the actor
            actors.append(
                Actor(**actor_config)
            )

    # add all the actors to the database
    try:
        for actor in actors:
            db.session.add(actor)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Failed to create actor %s" % e)
        

def read_actor_config_from_yaml(filename) -> dict:
    """
    Read actor_config from file.
    Return a json representation of the yaml file 
    """
    with open(filename, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            return None
            print(exc)