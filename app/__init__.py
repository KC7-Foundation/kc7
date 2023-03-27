from datetime import date
from datetime import datetime
import sys, os, time
import requests

from flask_sqlalchemy import SQLAlchemy

from flask import Flask, render_template, g
from flask_login import LoginManager, current_user
from flask_security import Security, SQLAlchemyUserDatastore



application = Flask(
            __name__,
            template_folder="client/templates",
            static_folder="client/static"
        )

# aws likes 'application' but I want to use 'app'
# this is a hack to make us both happy
# azure may want the same
app = application

# Import Configurations from config.py
# Depends on the environment (e.g. production, dev, testing...)
#export APPLICATION_SETTINGS='config.DevelopmentConfig' to set config
#app.config.from_object(os.environ['APPLICATION_SETTINGS'])
app.config.from_object('config.DevelopmentConfig')
app.config.from_object('config.ActivityVolumeSettings')
#app_settings = "app.server.config.DevelopmentConfig"

# Define the database object which is imported
# by modules and views
db = SQLAlchemy(app)

# Import a module / component using its blueprint handler variable (mod_auth)
from app.server.views import main
from app.server.auth.auth_views import auth
from app.server.models import Users, Team, Roles, GameSession

# Register blueprint(s)
app.register_blueprint(main)
app.register_blueprint(auth)


# login manager to be used for authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Build the database:
# This will create the database file using SQLAlchemy
db.create_all()


# HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('auth/404.html'), 404


@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))

    
@app.before_request
def before_request():
    """
    Prepopulate an admin team and user in the database
    """
    g.user = current_user
    

@app.before_first_request
def before_first_request():
    db.create_all()

    #user_datastore.find_or_create_role(name='Admin')
    if not Team.query.first():
        print("Creating admins teams")
        db.session.add(Team(name='admins', score=0))
        db.session.commit()
    else:
        pass
        # reset scores
        #print("Admin team exists... all good :P")
        # teams = Team.query.all()
        # for team in teams:
        #     team.score = 0
        #     db.session.add(team)
        #     db.session.commit()

    if not Roles.query.first():
        admin_role = Roles(name='Admin')
        db.session.add(admin_role)
        db.session.commit()
    else:
        admin_role = Roles.query.first()
        

    admin_team = db.session.query(Team).get(1)
    if not Users.query.first():
        # if no users are found in the database
        # see an initial "Admin" user 
        admin_user = Users(
            username='admin',
            email='admin@logstream.com',
            password= 'admin',
            team=admin_team
        )

        admin_user.roles = [admin_role]
        db.session.add(admin_user)
        db.session.commit()

    current_session = db.session.query(GameSession).get(1)
    if not GameSession.query.all():
        try:
            current_session = GameSession(state=True, start_time=datetime.now())
            db.session.add(current_session)
            db.session.commit()
            print("Created a new game session!")
        except Exception as e:
            print("Failed to create a gaming session: %s" % e)

# Seeding the database with an admin account
user_datastore = SQLAlchemyUserDatastore(db=db, user_model=Users, role_model=Roles)
security = Security(app, user_datastore)

#### Issues
#### functions don't have access to config due to lack of persistence
### What needs to be held in memory? (flask can do this in a local db)
    # Company / employee
    # Actor data (infrastructure / themes)
    # DNS data

### What doesn't need ot be held in memory
    # emails send (follow up actions can be done using functions)
    # browsing data (follow up actions can be done using functions)


