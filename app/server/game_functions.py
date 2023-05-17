import glob
import pandas as pd
from flask_security import roles_required

from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, abort, current_app, jsonify
from sqlalchemy import asc
from  sqlalchemy.sql.expression import func, select
from datetime import datetime, date, time, timedelta
import random

# Import module models (i.e. Company, Employee, Actor, DNSRecord)
from app.server.models import db, GameSession
from app.server.modules.organization.Company import Company, Employee
from app.server.modules.infrastructure.DNSRecord import DNSRecord
from app.server.modules.logging.uploadLogs import LogUploader
from app.server.modules.email.email_controller import gen_email, gen_actor_email
from app.server.modules.outbound_browsing.browsing_controller import *
from app.server.modules.infrastructure.passiveDNS_controller import *
from app.server.modules.organization.company_controller import create_company
from app.server.modules.outbound_browsing.browsing_controller import browse_random_website
from app.server.modules.inbound_browsing.inbound_browsing_controller import gen_inbound_browsing_activity
from app.server.modules.authentication.auth_controller import auth_random_user_to_mail_server, actor_password_spray
from app.server.modules.helpers.config_helper import read_config_from_yaml
from app.server.modules.endpoints.endpoint_controller import gen_system_files_on_host, gen_user_files_on_host, gen_system_processes_on_host
from app.server.modules.file.malware import Malware
from app.server.modules.helpers.config_helper import load_malware_obj_from_yaml_by_file, read_list_from_file
from app.server.modules.helpers.browsing_helpers import *
from app.server.modules.logging.meta import DebugLogger

from app.server.utils import *
from app.server.modules.file.vt_seed_files import FILES_MALICIOUS_VT_SEED_HASHES
from app.server.utils import AttackTypes

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
    global LOG_UPLOADER
    LOG_UPLOADER = LogUploader(queue_limit=100000)
    LOG_UPLOADER.create_tables(reset=True)

    # instantiate a logUploader. This allows us to locally log actor activity 
    global DEBUG_LOGGER
    DEBUG_LOGGER = DebugLogger('actor_activity.log')
    DEBUG_LOGGER.log_debug('This is a debug message.')

    global MALWARE_OBJECTS
    MALWARE_OBJECTS = create_malware()

    global LEGIT_DOMAINS # Legit domains from legit.txt
    global ALEXA_DOMAINS # Domains from Alexa top 100k

    ALEXA_DOMAINS = read_list_from_file('app/server/modules/helpers/alexa_top100k.txt')

    legit = read_list_from_file('app/server/modules/helpers/legit.txt')
    wiki_domains = wiki_get_random_articles()
    reddit_worldnews = reddit_get_subreddit("worldnews")
    LEGIT_DOMAINS = legit + wiki_domains + reddit_worldnews 
    if current_app.config['API_NEWSAPI'] != "":
        news_domains = news_get_top_headlines(current_app.config['API_NEWSAPI'])
        LEGIT_DOMAINS = LEGIT_DOMAINS + news_domains
    if current_app.config['API_YOUTUBEAPI'] != "":
        youtube_domains = youtube_get_random_videos(current_app.config['API_YOUTUBEAPI'])
        youtube_domains2 = youtube_get_random_videos(current_app.config['API_YOUTUBEAPI'])
        LEGIT_DOMAINS = LEGIT_DOMAINS + youtube_domains + youtube_domains2

   
    global CONTENT_DOMAINS
    CONTENT_DOMAINS = read_list_from_file('app/server/modules/helpers/content-domains.txt')
    global RANDOMIZED_DOMAINS
    global PARTNER_DOMAINS
    global ALL_DOMAINS
    ALL_DOMAINS = LEGIT_DOMAINS + CONTENT_DOMAINS 


    #Global Question Domains 
    global COMPANY_NAME 
    global COMPANY_DOMAIN
    global PARTNER_DOMAIN_1
    global PARTNER_DOMAIN_2
    global PARTNER_DOMAIN_3
    global PARTNER_DOMAIN_4
    global RANDOM_ACTOR_DOMAIN
    global RANDOM_ACTOR_KEYWORD
    COMPANY_NAME = ""
    COMPANY_DOMAIN = ""
    PARTNER_DOMAIN_1 = ""
    PARTNER_DOMAIN_2 = ""
    PARTNER_DOMAIN_3 = ""
    PARTNER_DOMAIN_4 = ""
    RANDOM_ACTOR_DOMAIN = ""
    RANDOM_ACTOR_KEYWORD = ""


    # The is current game session
    # This data object tracks whether or not the game is currently running
    # It allows us to start/stop/restart the game from the views
    current_session = db.session.query(GameSession).get(1)
    current_session.state = True
    
    print(f"Game started at {current_session.start_time}")
    # TODO: allow users ot modify start time in the web UI    
    # run startup functions 
    employees = Employee.query.all()
    actors = Actor.query.all()
    if not (employees or actors):
        employees, actors  = init_setup()
    
    print("initialization complete...")

    # This is where the action happens
    # Iterate through each day in the loop
    # You can customize the length of the game in the company.yaml config file
    company = Company.query.get(1)

    #Generate Domains
    LEGIT_DOMAINS.append(company.domain)
    company_data = generate_company_domains(company.domain)
    partner_data = generate_partner_domains(company.get_partners())
    LEGIT_DOMAINS = LEGIT_DOMAINS + company_data + partner_data
    randomized_company_domains = generate_company_traffic(company.domain)
    RANDOMIZED_DOMAINS = randomized_company_domains
    PARTNER_DOMAINS = company.get_partners()
    ALL_DOMAINS =  ALL_DOMAINS + RANDOMIZED_DOMAINS + PARTNER_DOMAINS

    #Append to guide
    COMPANY_DOMAIN == company.domain
    COMPANY_NAME == company.name
    with open('app/server/modules/constants/template_guide.txt','r') as f:
        data = f.read()
        data = data.replace('{{COMPANY_NAME}}',company.name)
        partner_int = 1
        for partner in PARTNER_DOMAINS: 
            temp_name = "PARTNER_DOMAIN_" + str(partner_int)
            try: 
                if partner_int == 1: 
                    PARTNER_DOMAIN_1 = temp_name
                elif partner_int == 2:
                    PARTNER_DOMAIN_2 = temp_name
                elif partner_int == 3:
                    PARTNER_DOMAIN_3 = temp_name
                elif partner_int == 4:
                    PARTNER_DOMAIN_4 = temp_name
            except:
                print('Error adding PARTNER_DOMAIN variable')
            data = data.replace('{{' + temp_name + '}}',partner)
            partner_int = partner_int + 1
        with open (company.domain+".md", "w") as w: 
            w.write(data)


    current_date = date.fromisoformat(company.activity_start_date)
    while current_date <= date.fromisoformat(company.activity_end_date):
        print("##########################################")
        print(f"## Running for day {current_date}...")
        print("##########################################")
        
        for actor in actors: 
            if actor.is_default_actor:
                # Default actor is used to create noise
                generate_activity_new(actor, current_date, employees, num_passive_dns=200) 
            else:
                # generate activity of actors defined in actor config
                # num_email is actually number of emails waves sent
                # waves contain multiple emails
                # TODO: abstract this out to the actor / make this more elegant
                generate_activity_new(actor, 
                                  current_date,
                                  employees, 
                                  num_passive_dns=random.randint(5, 10), 
                                  num_email=random.randint(0, 3)
                )

        current_date += timedelta(days=1)
    print("Done running!")

    #ADD Keyword
    for actor in actors:
        if not actor.is_default_actor:
            try:
                RANDOM_ACTOR_KEYWORD = random.choice(actor.sender_themes)
                RANDOM_ACTOR_DOMAIN = random.choice(actor.domains_list)
                with open(COMPANY_DOMAIN+".md",'r') as f:
                    data = f.read()
                    data = data.replace('{{RANDOM_ACTOR_KEYWORD}}', RANDOM_ACTOR_KEYWORD)
                    data = data.replace('{{RANDOM_ACTOR_DOMAIN}}', RANDOM_ACTOR_DOMAIN)
                    with open (COMPANY_DOMAIN+".md",'r') as w:
                        w.write(data)
            except:
                print('COULDNT ADD RANDOM KEYWORDS')

    #### Cleanup activities
    # clear the rest of queue
    LOG_UPLOADER.submit_queue()

    print("#########################")
    print("Summary of activities")
    print("########################")
    # print the tally
    print(
        json.dumps(
            LOG_UPLOADER.tally, indent=4
        )
    )
    for actor in actors:
        if not actor.is_default_actor:
            print("###############")
            print(actor.name)
            print("###############")
            print(list(set(actor.domains_list)))
            print(list(set(actor.ips_list)))
            print(list(set(Actor.string_to_list(actor.sender_emails))))



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
        print("making employees")
        employees = Employee.query.all()
        print(f"made {len(employees)} employees")
    if not actors:
        create_actors()
        actors = Actor.query.all()

    return employees, actors


def generate_activity_new(actor: Actor, 
                        current_date: date, 
                        employees: list, 
                        num_passive_dns:int=30, 
                        num_email:int=10, 
                        num_random_browsing_per_employee:int=20, 
                        num_auth_events_per_employee:int=10,
                        num_random_inbound_browsing:int=100,
                        count_of_user_endpoint_events=5,
                        count_of_system_endpoint_events=5) -> None:
    """
    Given an actor, generates one cycle of activity for users in the orgs 
    based on the attack types that they have defined

    The Default actor is used to represent normal company activities
    """

    # Activity will be generated for 20% of employees each day
    percent_employees_to_generate_activity_daily = 0.10 #percent

    # Generate legit activity for default actor
    if actor.is_default_actor:
            gen_passive_dns                     (actor, current_date, num_passive_dns)

            gen_email                           (employees=employees,
                                                partners=get_company().get_partners(),
                                                actor=actor,
                                                count_emails_per_user=num_email,
                                                percent_employees_to_generate=percent_employees_to_generate_activity_daily,
                                                start_date=current_date)
            
            browse_random_website               (employees=employees, 
                                                actor=actor, 
                                                count_browsing=num_random_browsing_per_employee, 
                                                percent_employees_to_generate=percent_employees_to_generate_activity_daily, 
                                                start_date=current_date)
            
            auth_random_user_to_mail_server     (employees=employees, 
                                                num_auth_events_per_user=num_auth_events_per_employee, 
                                                percent_employees_to_generate=percent_employees_to_generate_activity_daily,
                                                start_date=current_date, 
                                                start_hour=actor.activity_start_hour, 
                                                day_length_hours=actor.workday_length_hours)
            
            gen_inbound_browsing_activity       (actor=actor, 
                                                start_date=current_date, 
                                                num_inbound_browsing_events=num_random_inbound_browsing)
            
            gen_system_files_on_host            (start_date=current_date, 
                                                start_hour=actor.activity_start_hour, 
                                                workday_length_hours=actor.workday_length_hours,
                                                percent_employees_to_generate=percent_employees_to_generate_activity_daily, 
                                                count_of_events_per_user=count_of_system_endpoint_events)
            
            gen_user_files_on_host              (start_date=current_date, 
                                                start_hour=actor.activity_start_hour, 
                                                workday_length_hours=actor.workday_length_hours, 
                                                percent_employees_to_generate=percent_employees_to_generate_activity_daily,
                                                count_of_events_per_user=count_of_user_endpoint_events)
            
            gen_system_processes_on_host        (start_date=current_date, 
                                                start_hour=actor.activity_start_hour, 
                                                workday_length_hours=actor.workday_length_hours, 
                                                percent_employees_to_generate=count_of_system_endpoint_events)
            
            return
    
    # Generate activity for malicious actors

    if date.fromisoformat(actor.activity_start_date) <= current_date <= date.fromisoformat(actor.activity_end_date) and\
        Clock.weekday_to_string(current_date.weekday()) in actor.working_days_list:
        # There's a 10% chance the actor will take the day off
        if random.random() <= current_app.config['ACTOR_SKIPS_DAY_RATE']:
            print(f"Actor {actor} is randomly taking a day off today: {current_date}!")
            return
        print(f"Generating activity for actor {actor.name}")
        # Generate passive dns
        gen_passive_dns(actor, current_date, num_passive_dns)

        # Send emails
        if AttackTypes.PHISHING_VIA_EMAIL.value in actor.get_attacks()\
        or AttackTypes.MALWARE_VIA_EMAIL.value in actor.get_attacks():
            gen_actor_email(employees,
                      actor, 
                      start_date=current_date
            )

        # Malicious Activity; Conduct Password Spray Attack
        if AttackTypes.PASSWORD_SPRAY.value in actor.get_attacks():
            actor_password_spray(
                actor=actor, 
                start_date=current_date,
                num_employees=random.randint(5, 50),
                num_passwords=5
            )

        # Watering hole attack
        if AttackTypes.MALWARE_VIA_WATERING_HOLE.value in actor.get_attacks():
            actor_stages_watering_hole(
                actor=actor,
                start_date=current_date, 
                num_employees=random.randint(5, 10),
                link_type="malware_delivery"
            )
        
        # Recon activity
        if AttackTypes.RECONNAISSANCE_VIA_BROWSING.value in actor.get_attacks():
            gen_inbound_browsing_activity(actor=actor, 
                                          start_date=current_date, 
                                          num_inbound_browsing_events=random.randint(0,10))
    
def create_actors() -> None:
    """
    Create a malicious actor in the game and adds them to the database
    Actors are read in from yaml files in the actor_configs folder

    TODO: there should be some validation of actor configs prior to creation
    """
    company = Company.query.get(1) # TODO: This works because we only have one company

    # Instantiate a default actor - this actor should always exist
    # the default actor is used to generate background noise in the game
    default_actor = Actor(
        name = "Default",  # Dont change the name!
        effectiveness = 99,
        count_init_passive_dns=500, 
        count_init_email= 5000, 
        count_init_browsing=5000,
        domain_themes = wordGenerator.get_words(1000),
        sender_themes = wordGenerator.get_words(1000),
        activity_start_date=company.activity_start_date,
        activity_end_date=company.activity_end_date,
        activity_start_hour=company.activity_start_hour,
        workday_length_hours=company.workday_length_hours,
        working_days=company.working_days_list
    )

    # load add default_actor
    actors = [default_actor]

    # use yaml configs to load other actors
    # read yaml file for each new actor, load json from yaml
    actor_configs = glob.glob("app/game_configs/actors/*.yaml") 
    for file in actor_configs:
        actor_config = read_config_from_yaml(file, config_type="Actor")
        # use dictionary value to instantiate actor
        if actor_config:
            # print(f"adding actor: {actor_config}")
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
        
def create_malware() -> "list[Malware]":
    """
    Load all malware configs from YAML and configure a list of Malware objects
    """
    malware_objects = []
    malware_configs = glob.glob(f"app/game_configs/malware/*.yaml")
    for path in malware_configs:
        malware_objects.append(load_malware_obj_from_yaml_by_file(path))
    
    return malware_objects

