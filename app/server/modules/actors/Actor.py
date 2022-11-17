# Import external modules
import random
from faker import Faker
import glob
from faker.providers import internet

# Import internal modules
from app.server.models import Base
from app import db
from app.server.modules.helpers.word_generator import WordGenerator
from app.server.modules.helpers.markov_sentence_generator import SentenceGenerator
from app.server.modules.file.malware import Malware
from app.server.modules.helpers.config_helper import read_config_from_yaml

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
    attacks                     = db.Column(db.String(300))
    domain_themes               = db.Column(db.String(300))
    sender_themes               = db.Column(db.String(300))
    subject_themes              = db.Column(db.String(300))
    file_names                  = db.Column(db.String(300))
    file_extensions             = db.Column(db.String(300))
    tlds                        = db.Column(db.String(300))
    malware                     = db.Column(db.String(300))
    spoof_email                 = db.Column(db.Boolean)

    count_init_passive_dns      = db.Column(db.Integer)
    count_init_email            = db.Column(db.Integer)
    count_init_browsing         = db.Column(db.Integer)   # >:D
    max_wave_size               = db.Column(db.Integer) 

    

    def __init__(self, name:str, effectiveness:int=50, domain_themes:list=[], sender_themes:list=[], 
                subject_themes:list=[],  tlds:list=[], spoof_email:bool=False, 
                count_init_passive_dns:int=100, count_init_email:int=10, count_init_browsing:int=2, max_wave_size:int=2,
                file_names:list=[], file_extensions:list=[], attacks:list=[], malware:list=[]):

        print(f"Instantiating actor {name}....")
        self.name = name
        self.effectiveness = effectiveness
        
        # if any of these values are provided as strings, convert them to lists
        if isinstance(tlds, list):
            tlds = " ".join(tlds)
        

        # we can't have lists in a database, hence the funny business here
        # take in the list as a space delimited string - then split
        self.attacks                    = " ".join(attacks)
        self.domain_themes              = " ".join(domain_themes + wordGenerator.get_words(10))  # adding random words for entropy
        self.sender_themes              = " ".join(sender_themes + wordGenerator.get_words(10))
        self.subject_themes             = " ".join(subject_themes + wordGenerator.get_words(10))
        self.file_names                 = " ".join(file_names)       # Will end up getting replaces by malware configs
        self.file_extensions            = " ".join(file_extensions)  # Will end up getting replaces by malware configs
        self.malware                    = " ".join(malware)
        self.tlds                       = tlds or " ".join(['com','net','biz','org','us']) # TODO: Put this in a config or something
        self.spoof_email                = spoof_email
        self.count_init_browsing        = int(count_init_browsing)
        self.count_init_email           = int(count_init_email)
        self.count_init_passive_dns     = int(count_init_passive_dns)
        self.max_wave_size              = int(max_wave_size)
        self.sender_emails              = self.gen_sender_emails()

    
    def get_attacks(self) -> "list[str]":
        """
        Converts string representation of file names into list
        """
        attacks = self.attacks.split(" ")
        return [f for f in attacks if f!='']


    def get_malware_names(self) -> "list[str]":
        """
        Get a list of malware names belonging to the actor
        """
        return Actor.string_to_list(self.malware)

    def get_random_malware_name(self) -> str:
        """
        Get a random malware name belonging to the actor
        """
        return random.choice(self.get_malware_names())

    def get_attacks_by_type(self, attack_type:str) -> "list[str]":
        """
        Attacks are defined as attack_type:attack_name
        Return all attack names given an attack type
        attacks:
        - email:credential_phishing
        - email:malware_delivery
        - remote_exploitation:proxyshell
        """
        attacks = self.get_attacks()
        attacks = [attack.split(":")[1] for attack in attacks if attack_type in attack]
        return attacks    

    def get_file_names(self) -> "list[str]":
        """
        Converts string representation of file names into list
        """
        return Actor.string_to_list(self.file_names)

    def get_file_extensions(self) -> "list[str]":
        """
        Converts string representation of file extensions into list
        """
        return Actor.string_to_list(self.file_extensions)


    def get_domain_name(self) -> str:
        """
        Assemble a domain name using the list of theme words from the Actor object
        """
        separators = ["","-" ]
        tlds = self.tlds.split(" ")
        
        # if actor is default, let's get a larger list of randomised words
        if self.name == "Default":
            domain_themes = wordGenerator.get_words(1000)
        else:
            # Splitting string representation of list from db into actual list
            domain_themes = self.domain_themes.split(" ")

        words = random.choices(domain_themes, k=random.randint(1,2))
        domain = random.choice(separators).join(list(set(words))) + "." + random.choice(tlds)

        return domain


    def get_ips(self, count_of_ips:int=10) -> "list[str]":
        """
        Get a list of IPs for the actor
        """
        actor_ips = [record.ip for record in self.dns_records]
        if actor_ips:
            return random.choices(actor_ips, k=count_of_ips)
        else:
            return []
        

    def get_email_subject(self) -> str:
        """
        Assemble a subject line using list of theme words from the Actor object
        """

        subject_themes = self.subject_themes.split(" ")
        return sentenceGenerator.genSentence(seedWords=subject_themes)


    def get_sender_address(self) -> str:
        """
        Return a random email from the actor's pool of email addresses
        """
        return random.choice(self.sender_emails)

    def gen_sender_address(self) -> str:
        """Make a list of fake sender addresses"""
        sender_themes = self.sender_themes.split(" ")

         # TODO: Centralize this list of freemail providers somewhere else (probably contants?)
        email_domains = ['yahoo.com', 'gmail.com', 'aol.com', 'verizon.com', 'yandex.com','hotmail.com','protonmail.com','qq.com']

        # just for fun: add and actor domain in the mix: so 1/8 chance senderd domain will be actor domain
        # TODO: make this selectable 
        email_domains.append(self.get_domain_name())
        # senders will come in one of two flavors
        # 1. themed_word@freemail.com
        # 2. themed_word@actordomain.com
       
        # get one or two words from our sender themes
        words = random.choices(sender_themes, k=random.randint(1,2))
        

        splitter = random.choice(["", "_", "."])
        sender_addr = splitter.join(words) + "@" + random.choice(email_domains)
        
        return sender_addr

    def gen_sender_emails(self, num_emails=5) -> "list[str]":
        """
        Generates actor email addresses to be used in email attacks
        """
        return [self.gen_sender_address() for _ in range(num_emails)]

    @staticmethod
    def string_to_list(field_value_as_str:str) -> "list[str]":
        """
        Converts a long string into a unique list by splitting on space
        removes any empty string values from list
        """
        vals = field_value_as_str.split(" ")
        return list(set([f for f in vals if f!='']))

        

    def __repr__(self):
        return '<Actor %r>' % self.name