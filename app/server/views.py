import time
import atexit

import json, random
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from faker import Faker
from faker.providers import internet, person, company
from flask_login import login_required, current_user
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

# instantiate faker
fake = Faker()
fake.add_provider(internet)
fake.add_provider(person)
fake.add_provider(company)

# Define the blueprint: 'main', set its url prefix: app.url/
main = Blueprint('main', __name__)


@main.route("/")
def home():
    print("initialization complete...")

    return render_template("main/score.html")

@main.route("/test_keys")
def testkey():
    # TODO: figure out how to test this efficiently

    return "Ok"

@main.route("/scoreboard")
def scoreboard():
    return render_template("main/score.html")

@main.route("/admin/manage_game")
@roles_required('Admin')
@login_required
def manage_game():
    """
    Manage the state of the game. 
    Ideally: start, stop, restart
    """
    current_session = db.session.query(GameSession).get(1)
    game_state = current_session.state

    indicators = db.session.query(DNSRecord).filter(DNSRecord.active == True)

    return render_template("admin/manage_game.html", game_state=game_state, indicators=indicators)


@main.route("/admin/start_game", methods=['GET'])
@roles_required('Admin')
@login_required
def call_start():
    # web endpoint to start the game
    start_game()
    return jsonify({"STATE":True})

def start_game():
    # The game session is a database table
    # The current game is session (1) - could probably do this better later
    current_session = db.session.query(GameSession).get(1)
    current_session.state = True

    # instantiate the clock
    print(f"Game started at {current_session.start_time}")

    # TODO: allow users ot modify start time in the web UI
    db.session.commit()
    
    # run startup functions 
    employees, actors  = init_setup()

    # (actor, employees, num_passive_dns, num_email, num_random_browsing
    print("initialization complete...")

    while current_session.state == True:

        teams = Team.query.all()

        # generate the activity
        for actor in actors: 
            if actor.name == "Default":
                generate_activity(actor, employees, num_passive_dns=10, num_email=10,num_random_browsing=5) 
            else:
                generate_activity(actor, employees, num_passive_dns=1, num_email=2,num_random_browsing=3) 

        # Update the scores for each team
        for team in teams:
            team.score += 1000

            count_mitigations = len(team._mitigations)
            mitigation_cost = count_mitigations 
            team.score -= mitigation_cost

        db.session.commit()
        print("updated team scores")
        # time.sleep(5)  #do this when liv
    


@main.route("/admin/stop_game", methods=['GET'])
@roles_required('Admin')
@login_required
def stop_game():
    print("Stopping the game")
    current_session = db.session.query(GameSession).get(1)
    current_session.state = False
    db.session.commit()
    flash("The game has been Stopped")
    return jsonify({"STATE":current_session.state}) 


@main.route("/admin/restart_game", methods=['GET'])
@roles_required('Admin')
@login_required
def restart_game():
    print("Restarting the game")
    # Set game state to False
    current_session = db.session.query(GameSession).get(1)
    current_session.state = False
    current_session.start_time = datetime.now()
    # Reset team scores

    teams = Team.query.all()
    for team in teams:
        print("Resetting team scores")
        team.score = 0
        print("Resetting team mitigations")
        team._mitigations = ""
    
    db.session.query(DNSRecord).delete()
    db.session.query(Actor).delete()
    db.session.query(Employee).delete()
    db.session.query(Company).delete()

    db.session.commit()
    flash("The game has been reset", 'success')

    return jsonify({"STATE":current_session.state}) 


@main.route("/admin/teams")
@roles_required('Admin')
@login_required
def manage_teams():
    team_list = Team.query.all()
    return render_template("admin/manage_teams.html",
                            teams = team_list)


@main.route("/admin/users")
@roles_required('Admin')
@login_required
def manage_users():
    user_list = Users.query.all()
    return render_template("admin/manage_users.html",
                            users = user_list)    


@main.route("/mitigations")
@login_required
def mitigations():
    """
    Users can view and apply mitigations from this page
    Mitigations are submitted as a list to updateDenyList endpoint
    """
    return render_template("main/mitigations.html")


@main.route("/getDenyList", methods=['GET'])
@login_required
def get_deny_list():
    """
    Query database for team mitigations
    Return mitigations in list format
    """
    return jsonify(current_user.team._mitigations)



@main.route("/updateDenyList", methods=['POST'])
@login_required
def update_deny_list():
    """
    POST request from mitigations page on click
    Take a list of indicators from the view
    Update the user's _mitigations attribute to reflect
    Mitigations are stored as a strigified list
    Must be json loaded after being retrieved
    """
    try:
        deny_list = request.form['dlist']
        mitigations = deny_list.split("\n")
        mitigations = [x for x in mitigations if x]
        current_user.team._mitigations = json.dumps(mitigations)

        #exists = db.session.query(User.id).filter_by(name='davidism').first() is not None
        # update the teams score
        # check if any new indicators are tagged as malicious
        # # award point for malicious indicators found
        # for indicator in mitigations:
        #     current_user.team.score += 100

        print(current_user.team.score)

        db.session.commit()
        return jsonify(success=current_user.team._mitigations)
    except Exception as e:
        print(e)
        return jsonify(success=False)


@login_required
@main.route('/deluser', methods=['GET', 'POST'])
def deluser():
    """
    Delete a user
    """
    try:
        user_id = request.form['user_id']
        user = db.session.query(Users).get(user_id)
        db.session.delete(user)
        db.session.commit()
        flash("User removed!", 'success')
    except Exception as e:
        print("Error: %s" % e)
        flash("Failed to remove user", 'error')
    return redirect(url_for('main.manage_users'))


@login_required
@main.route('/delreport', methods=['GET', 'POST'])
def delreport():
    """
    Delete a report
    """
    try:
        report_id = request.form['report_id']
        report = db.session.query(Report).get(report_id)
        db.session.delete(report)
        db.session.commit()
        flash("Report removed!", 'success')
    except Exception as e:
        print("Error: %s" % e)
        flash("Failed to remove report", 'error')
    return redirect(url_for('main.reports'))


@main.route("/teams")
@login_required
def teams():
    team_list = Team.query.all()
    return render_template("main/teams.html",
                            teams = team_list)


@login_required
@main.route('/delteam', methods=['GET', 'POST'])
def delteam():
    """
    Delete a team
    """
    try:
        team_id = request.form['team_id']
        team = db.session.query(Team).get(team_id)
        db.session.delete(team)
        db.session.commit()
        flash("Team removed!", 'success')
    except Exception as e:
        print("Error: %s" % e)
        flash("Failed to remove team", 'error')
    return redirect(url_for('main.manage_teams'))



@main.route("/create_team", methods=['POST'])
@login_required
@roles_required('Admin')
def create_team():
    try:
        team_name = request.form['team_name']
        team = Team(name=team_name, score=0)
        db.session.add(team)
        db.session.commit()
    except Exception as e:
        print_error_message('Failed to create team.', e)
        flash("Could not create this team!", 'error')
    flash("Added a new team", 'success')
    return redirect(url_for('main.manage_teams'))


@main.route('/get_score', methods= ['GET'])
def get_score():
    from datetime import datetime 

    try:
        # get all the teams except for admin team
        teams = db.session.query(Team).filter(Team.id != 1)
        SCORES = {}

        #  build a dictionary of team score
        # setting up here to create a data blob to be fed to javascript on the score page
        for team in teams:
            SCORES[team.name] = team.score

        # sort the dictionary
        SCORES = dict(sorted(SCORES.items(), key=lambda item: item[1], reverse=True))

        # flatten the dictionary and reformat it
        teams, scores = zip(*SCORES.items())
        SCORES = {
                "teams":list(teams),
                "scores":list(scores)
            }

        return jsonify(SCORES=SCORES)
    except Exception as e:
        print(e)
        abort(404)


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
    all_dns_records = [d.stringify() for d in all_dns_records]
    upload_dns_records_to_azure(all_dns_records)

    return employees, actors
    
def generate_activity(actor, employees, num_passive_dns, num_email, num_random_browsing):
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

            # time is return as timestamp (float)
            time = Clock.get_current_gametime(start_time=current_session.start_time,
                                                    seed_date=current_session.seed_date)

            browse_random_website(employee, actor, time)
        


# @main.route("/test")
# def test():
#     #api_result = send_request()

#     create_company()
#     #companies  = Company.query.all()
#     #names = [company.name for company in companies]

#     #create_actor()
#     #actors = Actor.query.all()
#     #names = [actor.name for actor in actors]
#     create_actors()
#     actors = Actor.query.all()
#     names = [actor.spoof_email for actor in actors]

#     gen_default_passiveDNS()
#     gen_actor_passiveDNS()
    
#     #default_actor = db.session.query(Actor).filter_by(name = "Default").one()
#     viking_actor = db.session.query(Actor).filter_by(name = "Flying Purple Vikings").one()
#     employees = get_employees()

#     employee = random.choice(employees)
#     for i in range(13):
#         gen_email(viking_actor)
#         #browse_random_website(employee, viking_actor)
    
#     return json.dumps(names)




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
        domain_themes = " ".join(wordGenerator.get_words(100)),
        sender_themes = " ".join(wordGenerator.get_words(100))
    )

    # This should come from a config later
    # viking_actor = Actor(
    #     name = "Flying Purple Vikings",
    #     effectiveness = 50,
    #     domain_themes = " ".join([
    #         "viking", "thor", "hammer","norse","mountain", "thunder", "storm", "seas", "rowing", "axe"
    #     ]),
    #     sender_themes = " ".join([
    #         "odin", "loki", "asgard", "fenrir", "astrid", "jormungand", "freya"
    #     ]),
    #     subject_themes = " ".join([
    #         "security","alert","urgent", "grand", "banquet", ""    
    #     ]),
    #     tlds = " ".join([
    #          "info", "io"   
    #     ]),
    #     spoof_email= True
    # )

    # third_actor = Actor(
    #     name = "Myotheractor",
    #     effectiveness = "99"
    # )

    football_actor = Actor(
        name = "Commanders",
        effectiveness = 50,
        count_init_passive_dns= 1,
        count_init_email= 1,
        domain_themes = " ".join([
            "touchdown", "interception", "hike","reception","pass", "back", "tackle", "ball", "quarter", "zone"
        ]),
        sender_themes = " ".join([
            "patriots", "commands", "cardinals", "rams", "steelers", "ravens", "jets"
        ]),
        subject_themes = " ".join([
            "playoff","scrimmage","competition", "pigskin", "kickoff", "superbowl"    
        ]),
        tlds = " ".join([
             "info", "io"   
        ]),
        file_names = " ".join([
            'scvhost', 'dllhost', 'Runtimeexplorer', 'plink', 'runner', 'proposal', 'invoice', 'salutations', 'nigerian_uncle', 'russian_prince',
    'hello', 'wwlib','goopdate','Resume','putty','server','job_opportunity','job_offer', 'for_your_review', 'free_money'
        ]),
        file_extensions = " ".join([
            'zip','rar','docx','dll','7z','pptx', 'xls', 'dotm','exe'
        ]),
        spoof_email= True
    )

    black_panther_actor = Actor(
        name = "Wakanda",
        effectiveness = 50,
        count_init_passive_dns= 1,
        count_init_email= 1,
        domain_themes = " ".join([
            "warrior", "black", "king","waterfall","royalty", "vibranium", "marvel", "throne", "stripped", "tribe"
        ]),
        sender_themes = " ".join([
            "panther", "shuri", "tchalla", "killmonger", "okoye", "nakia", "mbaku"
        ]),
        subject_themes = " ".join([
            "conflict","responsibility","fight", "coronation", "shipment", "casino", "museum"   
        ]),
        tlds = " ".join([
             "site", "xyz"   
        ]),
        spoof_email= True
        # set sender to internal address
    )


    # we can add more actors later
    actors = []
    actors.append(default_actor)
    actors.append(football_actor)
    actors.append(black_panther_actor)
    # actors.append(third_actor)
    
    try:
        for actor in actors:
            db.session.add(actor)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Failed to create actor %s" % e)




