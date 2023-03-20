
import json
import random
import yaml
from datetime import datetime
from flask_login import login_required, current_user
from flask_security import roles_required

from flask import Blueprint, request, render_template, \
    flash, g, session, redirect, url_for, abort, current_app, jsonify
from sqlalchemy import asc
from sqlalchemy.sql.expression import func, select

# Import module models (i.e. Company, Employee, Actor, DNSRecord)
from app.server.models import db, Team, Users, Roles, GameSession
from app.server.modules.organization.Company import Company, Employee
from app.server.modules.clock.Clock import Clock
from app.server.modules.logging.uploadLogs import LogUploader
from app.server.modules.email.email_controller import gen_email
from app.server.modules.infrastructure.DNSRecord import DNSRecord
from app.server.modules.outbound_browsing.browsing_controller import *
from app.server.modules.outbound_browsing.browsing_controller import browse_random_website
from app.server.modules.infrastructure.passiveDNS_controller import *
from app.server.utils import *

from app.server.game_functions import *

# Define the blueprint: 'main', set its url prefix: app.url/
main = Blueprint('main', __name__)


# @main.route("/")
# def home():
#     print("initialization complete...")
#     return redirect("/admin/manage_game")



@main.route("/")
def home():
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

    return render_template("admin/manage_game.html", game_state=game_state)


@main.route("/admin/manage_database")
@roles_required('Admin')
@login_required
def manage_database():
    log_uploader = LogUploader()
    perms = log_uploader.get_user_permissions()
    return render_template("admin/manage_database.html", perms=perms)

@main.route("/admin/start_game", methods=['GET'])
@roles_required('Admin')
@login_required
def call_start():
    """
    web endpoint to start the game. 
    Returns game state - this is used to update the view
    """
    start_game()
    return jsonify({"STATE": True})


@main.route("/admin/stop_game", methods=['GET'])
@roles_required('Admin')
@login_required
def stop_game():
    print("Stopping the game")
    current_session = db.session.query(GameSession).get(1)
    current_session.state = False
    db.session.commit()
    flash("The game has been Stopped")
    return jsonify({"STATE": current_session.state})


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

    return jsonify({"STATE": current_session.state})


@main.route("/admin/teams")
@roles_required('Admin')
@login_required
def manage_teams():
    team_list = Team.query.all()
    return render_template("admin/manage_teams.html",
                           teams=team_list)


@main.route("/admin/users")
@roles_required('Admin')
@login_required
def manage_users():
    user_list = Users.query.all()
    return render_template("admin/manage_users.html",
                           users=user_list)


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

@main.route("/updatePermissions", methods=['POST'])
@roles_required('Admin')
@login_required
def update_permissions():
    """
    POST request from mitigations page on click
    Take a list of indicators from the view
    Update the user's _mitigations attribute to reflect
    Mitigations are stored as a strigified list
    Must be json loaded after being retrieved
    """
    try:
        permissions_list = request.form['plist']
        log_uploader = LogUploader()
        user_strings = [x for x in permissions_list.split("\n") if x]
        for user_string in user_strings:
                log_uploader.add_user_permissions(user_string)
        return jsonify(success=True)
    except Exception as e:
        print(e)
        flash("Error updating ADX Permissions: ","error")
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
                           teams=team_list)


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
        print('Failed to create team.', e)
        flash("Could not create this team!", 'error')
    flash("Added a new team", 'success')
    return redirect(url_for('main.manage_teams'))


@main.route('/get_score', methods=['GET'])
def get_score():
    """
    Return a joson blob containing score for all teams in the game
    """
    from datetime import datetime
    return jsonify({}) # TODO: This disables the scorekeeping stuff to prevent crashes while debugging.

    try:
        # get all the teams except for admin team
        teams = db.session.query(Team).filter(Team.id != 1)
        SCORES = {}

        #  build a dictionary of team score
        # setting up here to create a data blob to be fed to javascript on the score page
        for team in teams:
            SCORES[team.name] = team.score

        # sort the dictionary
        SCORES = dict(
            sorted(SCORES.items(), key=lambda item: item[1], reverse=True))

        # flatten the dictionary and reformat it
        teams, scores = zip(*SCORES.items())
        SCORES = {
            "teams": list(teams),
            "scores": list(scores)
        }

        return jsonify(SCORES=SCORES)
    except Exception as e:
        print(e)
        abort(404)
