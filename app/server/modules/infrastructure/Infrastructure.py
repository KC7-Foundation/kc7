# Import internal modules
from app.server.models import Base
import random
from app import db
from app.server.modules.helpers.word_generator import WordGenerator

# Import external modules
from faker import Faker
from faker.providers import internet

# Instantiate objects
fake = Faker()
fake.add_provider(internet)

wordGenerator = WordGenerator()


class Domain(Base):
    """ 
    Belongs to an actor
    There should be default actor to own non-malicious infrastructure
    """

    name              = db.Column(db.String(50))

    actor_id            = db.Column(db.Integer, db.ForeignKey('actor.id'))
    actor               = db.relationship('Actor', backref=db.backref('domains', lazy='dynamic'))

    def __init__(self, actor): 
        self.actor = actor
        self.name =  self._get_domain_name()
        


    def _get_domain_name(self) -> str:
        """
        Assemble a domain name using the list of theme words from the Actor object
        """
        from app.server.game_functions import LEGIT_DOMAINS

        separators = ["","-" ]
        tlds = self.actor.tld_values
        
        # if actor is default, let's get a larger list of randomised words
        if self.actor.is_default_actor:
            return random.choice(LEGIT_DOMAINS)
        else:
            # Splitting string representation of list from db into actual list
            domain_themes = self.actor.domain_theme_values
        domain_depth = self.actor.domain_depth or random.randint(1,2)
        words = random.choices(domain_themes, k=domain_depth)
        # THIS IS A HACK! You can optionally provide a list of domains (rather than theme words) in the actor config under 'domain_themes"
        if domain_depth == 1 and "." in words[0]:
            domain = random.choice(separators).join(list(set(words)))
        # This is the normal behavior (ie theme_word.tld)
        else:
            domain = random.choice(separators).join(list(set(words))) + "." + random.choice(tlds)

        return domain

class IP(Base):
    """ 
    Belongs to an actor
    There should be default actor to own non-malicious infrastructure
    """
    address             = db.Column(db.String(50), unique=True)              #next figure out how to have actors steal this
    actor_id            = db.Column(db.Integer, db.ForeignKey('actor.id'))
    actor               = db.relationship('Actor', backref=db.backref('ips', lazy='dynamic'))

    def __init__(self, actor): 
        self.actor = actor
        self.address = fake.ipv4_public()