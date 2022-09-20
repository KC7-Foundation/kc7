# Import internal modules
from app.server.models import Base
from app import db
from app.server.modules.helpers.word_generator import WordGenerator

# Import external modules
import random
from faker import Faker
from faker.providers import internet
from app.server.modules.helpers.markov_sentence_generator import SentenceGenerator

# Instantiate classes to be used here
wordGenerator = WordGenerator()
fake = Faker()
fake.add_provider(internet)
sentenceGenerator = SentenceGenerator()

class Actor(Base):
    """
    A class that defines the actor data model.
    This class inherits from Base and will be represented in the database.
    """
    
    name                        = db.Column(db.String(50), nullable=False)
    effectiveness               = db.Column(db.Integer)

    # Lists cannot be represented in the flask db
    # This representation converts lists into a space-delimited string
    domain_themes               = db.Column(db.String(300))
    sender_themes               = db.Column(db.String(300))
    subject_themes              = db.Column(db.String(300))
    file_names                  = db.Column(db.String(300))
    file_extensions             = db.Column(db.String(300))
    tlds                        = db.Column(db.String(300))
    spoof_email                 = db.Column(db.Boolean)

    count_init_passive_dns      = db.Column(db.Integer)
    count_init_email            = db.Column(db.Integer)
    count_init_browsing         = db.Column(db.Integer)   # >:D

    def __init__(self, name:str, effectiveness:int=50, domain_themes:list=[], sender_themes:list=[], 
                subject_themes:list=[],  tlds:list=[], spoof_email:bool=False, 
                count_init_passive_dns:int=100, count_init_email:int=10, count_init_browsing:int=2, 
                file_names:str="", file_extensions:str="" ):

        self.name = name
        self.effectiveness = effectiveness
        
        # if any of these values are provided as strings, convert them to lists
        if isinstance(tlds, list):
            tlds = " ".join(tlds)
        

        # we can't have lists in a database, hence the funny business here
        # take in the list as a space delimited string - then split
        self.domain_themes              = " ".join(domain_themes + wordGenerator.get_words(10))  # adding random words for entropy
        self.sender_themes              = " ".join(sender_themes + wordGenerator.get_words(10))
        self.subject_themes             = " ".join(subject_themes + wordGenerator.get_words(10))
        self.file_names                 = " ".join(file_names)
        self.file_extensions            = " ".join(file_extensions)
        self.tlds                       = tlds or " ".join(['com','net','biz','org','us']) # TODO: Put this in a config or something
        self.spoof_email                = spoof_email
        self.count_init_browsing        = int(count_init_browsing)
        self.count_init_email           = int(count_init_email)
        self.count_init_passive_dns     = int(count_init_passive_dns)

    
    def get_file_names(self) -> "list[str]":
        """
        Converts string representation of file names into list
        """
        file_names = self.file_names.split(" ")
        return [f for f in file_names if f!='']


    def get_file_extensions(self) -> "list[str]":
        """
        Converts string representation of file extensions into list
        """
        file_extensions = self.file_extensions.split(" ")
        return [f for f in file_extensions if f!='']

    def get_domain_name(self) -> str:
        """
        Assemble a domain name using the list of theme words from the Actor object
        """
        separators = ["","-","and","or", "with", "on", "in" ]
        tlds = self.tlds.split(" ")
        
        # if actor is default, let's get a larger list of randomised world
        if self.name == "Default":
            domain_themes = wordGenerator.get_words(1000)
        else:
            # Splitting string representation of list from db into actual list
            domain_themes = self.domain_themes.split(" ")

        words = random.choices(domain_themes, k=random.randint(2,3))
        
        domain_components = []
        for loc, word in enumerate(words):
            domain_components += word 
            if loc < len(words)-2:
                domain_components += random.choice(separators)

        domain = "".join(domain_components) + "." + random.choice(tlds)

        return domain
        

    def get_email_subject(self) -> str:
        """
        Assemble a subject line using list of theme words from the Actor object
        """

        subject_themes = self.subject_themes.split(" ")
        return sentenceGenerator.genSentence(seedWords=subject_themes)


    def get_sender_address(self) -> str:
        """Make a list of fake sender addresses"""
        sender_themes = self.sender_themes.split(" ")

        # TODO: Centralize this list of freemail providers somewhere else (maybe helpers?)
        free_email_service_domains = ['yahoo.com', 'gmail.com', 'aol.com', 'verizon.com', 'yandex.com','hotmail.com','protonmail.com','qq.com']
        words = random.choices(sender_themes, k=random.randint(2,5))
        
        sender_addr = "".join(words) + "@" + random.choice(free_email_service_domains)
        
        return sender_addr

    def __repr__(self):
        return '<Actor %r>' % self.name