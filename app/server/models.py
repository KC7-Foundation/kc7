import random
import string
import json
import datetime
from faker import Faker
from faker.providers import internet
from flask_security import RoleMixin, UserMixin
# Import password / encryption helper tools
from werkzeug.security import check_password_hash, generate_password_hash
from flask import jsonify

# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db
from app.server.modules.helpers.word_generator import WordGenerator

# instantiate faker
fake = Faker()
fake.add_provider(internet)

wordGenerator = WordGenerator()

# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__    = True

    id              = db.Column(db.Integer, primary_key=True)

    def __init__(self, id, name, domain):

        self.id = id


class Company(Base):
    """A company has many employees"""

    name            = db.Column(db.String(50), nullable=False)
    domain          = db.Column(db.String(50), nullable=False)
   #employee        = db.relationship('Employee', backref=db.backref('employees', lazy='dynamic'))

    def __init__(self, name, domain):
        self.name = name
        self.domain = domain

    def __repr__(self):
        return '<Company %r>' % self.name


class Employee(Base):
    """ Belongs to a company"""

    name                = db.Column(db.String(50))
    user_agent          = db.Column(db.String(50))
    ip_addr             = db.Column(db.String(50))
    awareness           = db.Column(db.Integer)
    email_addr          = db.Column(db.String(50))
    username            = db.Column(db.String(50))
    hostname            = db.Column(db.String(50))
    # TODO - users should have roles in the company (CEO, CIO, IT Admin, Janitor, Intern, HR

    company_id          = db.Column(db.Integer, db.ForeignKey('company.id'))
    company             = db.relationship('Company', backref=db.backref('employees', lazy='dynamic'))

    def __init__(self, name, user_agent, ip_addr, awareness, email_addr, company, username, hostname):
        self.name = name
        self.user_agent = user_agent
        self.ip_addr = ip_addr
        self.awareness = awareness
        self.email_addr = email_addr
        self.company = company
        self.username = username
        self.hostname = hostname

    def __repr__(self):
        return  {
            "name": self.name,
            "user_agent": self.user_agent,
            "ip_addr": self.ip_addr,
            "email_addr": self.email_addr,
            "company_domain": self.company.name
        }

class DNSRecord(Base):
    """ 
    Belongs to an actor
    There should be default actor to own non-malicious infrastructure
    """

    ip                  = db.Column(db.String(50))
    domain              = db.Column(db.String(50))
    active              = db.Column(db.Boolean)

    actor_id            = db.Column(db.Integer, db.ForeignKey('actor.id'))
    actor               = db.relationship('Actor', backref=db.backref('dns_records', lazy='dynamic'))

    def __init__(self, actor, ip=None, domain=None): 
        self.actor = actor
        self.ip = ip or self._get_ip()
        self.domain = domain or self._get_domain()
        self.active = False
        
    def _get_ip(self):
        """Add a new IP to the record"""
        new_ip = fake.ipv4_public()
        return new_ip

    def _get_domain(self):
        """Add a new IP to the record"""
        new_domain = self.actor.get_domain_name()
        return new_domain

    def stringify(self):
        return {
            "ip":self.ip, 
            "domain": self.domain
        }

    @staticmethod
    def get_kql_repr():
        return (
            "PassiveDns",
            {
                "ip":"string",
                "domain":"string"
            }
        )


##########################################################
# The following classes are specific to user autentication
###########################################################

class AuthBase(db.Model):

    __abstract__    = True
    id              = db.Column(db.Integer, primary_key=True)


class Team(AuthBase):

    __tablename__   = "teams"

    name                    = db.Column(db.String(50), nullable=False)
    score                   = db.Column(db.Integer, nullable=False)
    _mitigations            = db.Column(db.Text)
    security_awareness      = db.Column(db.Float, nullable=False)

    def __init__(self, name, score, _mitigations="", security_awareness=.25):

        self.name = name
        self.score = score
        self._mitigations = _mitigations
        self.security_awareness = security_awareness

    def __repr__(self):
        return '<Team %r>' % self.name


class Users(AuthBase, RoleMixin):

    __tablename__   = "users"
    id              = db.Column('user_id', db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1') 
    
    username        = db.Column('username', db.String(50), unique=True, index=True)
    pw_hash         = db.Column('pw_hash', db.String(150))
    email           = db.Column('email', db.String(50), unique=True, index=True)
    registered_on   = db.Column('registered_on', db.DateTime)

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    team = db.relationship('Team', backref=db.backref('members', lazy='dynamic'))
    
    roles = db.relationship('Roles', secondary='user_roles', backref='users', lazy=True)

    def __init__(self, username, password, email, team):
        self.username = username
        self.set_password(password)
        self.email = email
        self.registered_on = datetime.datetime.now()
        self.team = team

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def has_role(self, role):
        return role in self.get_roles()

    def get_roles(self):
        return [role.name for role in self.roles]

    def __repr__(self):
        return '<User %r>' % (self.username)


# Define the Role data-model
class Roles(AuthBase):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


# Define the UserRoles association table
class UserRoles(AuthBase):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.user_id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


class Report(AuthBase):

    """
        A report object is generated by company employees
        Each report belongs to a team and is generated 
        based on the security awareness of the company
    """
    __tablename__   = "report"

    subject                = db.Column(db.String(50), nullable=False)
    sender                 = db.Column(db.String(50), nullable=False)
    recipient              = db.Column(db.String(50), nullable=False)
    time                   = db.Column(db.String(50), nullable=False)
    
    team_id                = db.Column(db.Integer, db.ForeignKey('teams.id'))
    team                   = db.relationship('Team', backref=db.backref('reports', lazy='dynamic'))

    def __init__(self, subject, sender, recipient, time, team):

        self.subject = subject
        self.sender = sender
        self.recipient = recipient
        self.time = time
        self.team = team

    def __repr__(self):
        return '<Report %r>' % self.id


##########################################################
# The following classes are specific to game sessions
###########################################################

# Define the Role data-model
class GameSession(Base):
    id              = db.Column(db.Integer(), primary_key=True)
    state           = db.Column(db.Boolean)
    start_time      = db.Column(db.String(50)) #should be given as a timestamp float
    seed_date       = db.Column(db.String(50))  
    time_multiplier = db.Column(db.Integer())

    def __init__(self, state, start_time, seed_date="2022-01-01", time_multiplier=1000):
        self.state = False
        self.seed_date = seed_date    # starting date for the game
        self.start_time = start_time  # real life start time of game
        self.time_multiplier = time_multiplier