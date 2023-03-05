# Import internal modules
from app.server.models import Base
from app import db

# Import external modules
from faker import Faker
from faker.providers import internet

# Instantiate objects
fake = Faker()
fake.add_provider(internet)

class WhoIsRecord(Base):
    """
    Created when an actor registers a domain
    Lists registration info a given domain
    """

    creation_time               = db.Column(db.String(50))
    updated_time                = db.Column(db.String(50))
    domain                      = db.Column(db.String(50))
    registrar                   = db.Column(db.String(50))
    registrant_city             = db.Column(db.String(50))
    registrant_country          = db.Column(db.String(50))
    registrant_email            = db.Column(db.String(50))

    actor_id            = db.Column(db.Integer, db.ForeignKey('actor.id'))
    actor               = db.relationship('Actor', backref=db.backref('whois_records', lazy='dynamic'))


    def __init__(self, creation_time:str=creation_time, updated_time:str=updated_time, 
                    domain:st=domain,registrar:str=registrar, registrant_city:str=registrant_city, 
                    registrant_country:str=registrant_country, registrant_email:str=registrant_email,
                    actor=actor) -> None:

        self.actor = actor
        self.creation_time = creation_time
        self.updated_time = updated_time
        self.domain = domain
        self.registrar = registrar
        self.registrant_city = registrant_city
        self.registrant_country = registrant_country
        self.registrant_email = registrant_email



