import random
import json
from faker import Faker
from faker.providers import internet

# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db

# instantiate faker
fake = Faker()
fake.add_provider(internet)

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

    company_id          = db.Column(db.Integer, db.ForeignKey('company.id'))
    company             = db.relationship('Company', backref=db.backref('employees', lazy='dynamic'))

    def __init__(self, name, user_agent, ip_addr, awareness, email_addr, company):
        self.name = name
        self.user_agent = user_agent
        self.ip_addr = ip_addr
        self.awareness = awareness
        self.email_addr = email_addr
        self.company = company


    def set_email(self):
        self.email_addr = str.lower("_".join(self.name.split(" "))) + '@' + self.company_domain

    def __repr__(self):
        return  {
            "name": self.name,
            "user_agent": self.user_agent,
            "ip_addr": self.ip_addr,
            "email_addr": self.email_addr,
            "company_domain": self.company.name
        }


class Actor(Base):
    """ Bad guys doing bad things"""
    
    name                = db.Column(db.String(50), nullable=False)
    effectiveness       = db.Column(db.Integer)

    # makes these long strings and just split them on use
    domain_themes       = db.Column(db.String(300))
    sender_themes       = db.Column(db.String(300))
    subject_themes      = db.Column(db.String(300))
    tlds                = db.Column(db.String(300))
    spoof_email         = db.Column(db.Boolean)

    count_init_passive_dns              = db.Column(db.Integer)
    count_init_email                    = db.Column(db.Integer)
    count_init_browsing                 = db.Column(db.Integer)   # >:D

    def __init__(self, name, effectiveness=50, domain_themes="", sender_themes="", 
                subject_themes="",  tlds=None, spoof_email=False, 
                count_init_passive_dns=100, count_init_email=10, count_init_browsing=2):

        self.name = name
        self.effectiveness      = effectiveness
        # we can't have lists in a database, hence the funny business here
        self.domain_themes              = " ".join(domain_themes.split(" ") + fake.words(nb=10))
        self.sender_themes              = " ".join(sender_themes.split(" ") + fake.words(nb=10))
        self.subject_themes             = " ".join(subject_themes.split(" ") + fake.words(nb=10))
        self.tlds                       = tlds or " ".join(['com','net','biz','org','us'])
        self.spoof_email                = spoof_email
        self.count_init_browsing        = count_init_browsing
        self.count_init_email           = count_init_email
        self.count_init_passive_dns     = count_init_passive_dns

    def get_domain_name(self):
        """
        Assemble a domain name using the list of theme words from the Actor object
        """
        separators = ["","-","and","or", "with", "on", "in" ]
        tlds = self.tlds.split(" ")
        domain_themes = self.domain_themes.split(" ")

        words = random.choices(domain_themes, k=random.randint(2,5))

        domain_components = []
        for loc, word in enumerate(words):
            domain_components += word 
            if loc < len(words)-1:
                domain_components += random.choice(separators)

        domain = "".join(domain_components) + "." + random.choice(tlds)

        return domain
        

    def get_email_subject(self):
        """
        Assemble a subject line using list of theme words from the Actor object
        """
        subject_themes = self.subject_themes.split(" ")
        return fake.sentence(nb_words=7, ext_word_list=subject_themes)


    def get_sender_address(self):
        """Make a list of fake sender addresses"""
        sender_themes = self.sender_themes.split(" ")

        free_email_service_domains = ['yahoo.com', 'gmail.com', 'aol.com', 'verizon.com', 'yandex.com','hotmail.com','protonmail.com','qq.com']
        words = random.choices(sender_themes, k=random.randint(2,5))
        
        sender_addr = "".join(words) + "@" + random.choice(free_email_service_domains)
        
        return sender_addr

    def __repr__(self):
        return '<Actor %r>' % self.name


class DNSRecord(Base):
    """ 
    Belongs to an actor
    There should be default actor to own non-malicious infrastructure
    """

    ip                  = db.Column(db.String(50))
    domain              = db.Column(db.String(50))

    actor_id            = db.Column(db.Integer, db.ForeignKey('actor.id'))
    actor               = db.relationship('Actor', backref=db.backref('dns_records', lazy='dynamic'))

    def __init__(self, actor, ip=None, domain=None): 
        self.actor = actor
        self.ip = ip or self._get_ip()
        self.domain = domain or self._get_domain()
        
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