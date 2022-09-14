# Import internal modules
from app.server.models import Base
from app import db

# Import external modules
from faker import Faker
from faker.providers import internet

# Instantiate objects
fake = Faker()
fake.add_provider(internet)

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