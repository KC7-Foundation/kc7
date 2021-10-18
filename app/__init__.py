import sys, os
import requests
from flask_sqlalchemy import SQLAlchemy
#from app.main.models import db #, Users, Roles, Team

from flask import Flask


application = Flask(__name__)


# aws likes 'application' but I want to use 'app'
# this is a hack to make us both happy
# azure may want the same
app = application

# Import Configurations from config.py
# Depends on the environment (e.g. production, dev, testing...)
#export APPLICATION_SETTINGS='config.DevelopmentConfig' to set config
#app.config.from_object(os.environ['APPLICATION_SETTINGS'])
app.config.from_object('config.DevelopmentConfig')
#app_settings = "app.main.config.DevelopmentConfig"

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Import a module / component using its blueprint handler variable (mod_auth)
from app.main.controllers import main


# Register blueprint(s)
app.register_blueprint(main)

# Build the database:
# This will create the database file using SQLAlchemy
db.create_all()

#### Issues
#### functions don't have access to config due to lack of persistence
### What needs to be held in memory? (flask can do this in a local db)
    # Company / employee
    # Actor data (infrastructure / themes)
    # DNS data

### What doesn't need ot be held in memory
    # emails send (follow up actions can be done using functions)
    # browsing data (follow up actions can be done using functions)


