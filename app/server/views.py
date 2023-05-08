
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




@main.route("/")
# @roles_required('Admin')
# @login_required
def manage_game():
    """
    Manage the state of the game. 
    Ideally: start, stop, restart
    """
    current_session = db.session.query(GameSession).get(1)
    game_state = current_session.state

    return render_template("admin/manage_game.html", game_state=game_state)


@main.route("/admin/manage_database")
# @roles_required('Admin')
# @login_required
def manage_database():
    log_uploader = LogUploader()
    perms = log_uploader.get_user_permissions()
    return render_template("admin/manage_database.html", perms=perms)

@main.route("/admin/start_game", methods=['GET'])
# @roles_required('Admin')
# @login_required
def call_start():
    """
    web endpoint to start the game. 
    Returns game state - this is used to update the view
    """
    start_game()
    return jsonify({"STATE": True})


@main.route("/admin/stop_game", methods=['GET'])
# @roles_required('Admin')
# @login_required
def stop_game():
    print("Stopping the game")
    current_session = db.session.query(GameSession).get(1)
    current_session.state = False
    db.session.commit()
    flash("The game has been Stopped")
    return jsonify({"STATE": current_session.state})


@main.route("/admin/restart_game", methods=['GET'])
# @roles_required('Admin')
# @login_required
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



@main.route("/config")
def validate_config():
    import yaml
    from app.server.modules.helpers.config_helper import validate_yaml

    file = "app/game_configs/actors/Prosecco.yaml"
    
    configs = []
    actor_config_paths = glob.glob("app/game_configs/actors/*.yaml") 
    malware_config_paths = glob.glob("app/game_configs/malware/*.yaml") 
    company_config_path = glob.glob("app/game_configs/company.yaml") 
    
    def load_config(path, config_type):
        with open(path, 'r') as f:
            config_text = f.read()
        with open(path, 'r', encoding="utf8") as stream:
            errors = None
            yaml_json = None
            try:
                yaml_json = yaml.safe_load(stream)
            except Exception as e:
                errors = f"Invalid yaml provided: {e}"
        config = {
            "path": path,
            "text": config_text,
            "errors": errors or validate_yaml(yaml_json, config_type=config_type, show_errors=True)
        }
        configs.append(config)

    for path in actor_config_paths:
        load_config(path, config_type="Actor")
    for path in malware_config_paths:
        load_config(path, config_type="Malware")
    for path in company_config_path:
        load_config(path, config_type="Company")
        
    return render_template("main/config.html", configs=configs)