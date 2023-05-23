# Import external modules
import random
import json
from faker import Faker
import glob
from faker.providers import internet
import names
from datetime import date

# Import internal modules
from app.server.models import Base
from app.server.modules.organization.Company import Company
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
    domain_themes               = db.Column(db.String(1000)) # Making this larger to account for lists of domains passed in via config
    sender_themes               = db.Column(db.String(300))
    subjects                    = db.Column(db.String(300))
    file_names                  = db.Column(db.String(300))
    tlds                        = db.Column(db.String(300))
    malware                     = db.Column(db.String(300))
    recon_search_terms          = db.Column(db.String(300))
    post_exploit_commands       = db.Column(db.String(1000))   #TODO: Remove this. No reason why this should be in the DB
    sender_emails               = db.Column(db.String(300))
    watering_hole_domains       = db.Column(db.String(300))
    watering_hole_target_roles  = db.Column(db.String(300))
    sender_domains              = db.Column(db.String(300))

    count_init_passive_dns      = db.Column(db.Integer)
    count_init_email            = db.Column(db.Integer)
    count_init_browsing         = db.Column(db.Integer)   # >:D
    domain_depth                 = db.Column(db.Integer)
    max_wave_size               = db.Column(db.Integer) 
    difficulty                  = db.Column(db.String(50))

    activity_start_date         = db.Column(db.String(50))
    activity_end_date           = db.Column(db.String(50))
    activity_start_hour         = db.Column(db.Integer())
    workday_length_hours        = db.Column(db.Integer())
    working_days                = db.Column(db.String(300))

    #options for what an actor can do
    generates_infrastructure    = db.Column(db.Boolean)
    spoofs_email                = db.Column(db.Boolean)
    
    

    def __init__(self, name:str, activity_start_date:str, activity_end_date:str, activity_start_hour: int, workday_length_hours:int,
                 working_days: list=[], effectiveness:int=50, domain_themes:list=[], sender_themes:list=[], 
                subjects:list=[],  tlds:list=[], spoofs_email:bool=False, generates_infrastructure:bool=True, 
                count_init_passive_dns:int=100, count_init_email:int=1, count_init_browsing:int=2, max_wave_size:int=2,
                file_names:list=[], file_extensions:list=[], attacks:list=[], malware:list=[], recon_search_terms:list=[],
                post_exploit_commands:list=[], difficulty="HARD", watering_hole_domains:list=[], watering_hole_target_roles:list=[],
                sender_domains:list=[],domain_depth=None, **kwargs):
        # note we don't actually use KWargs, this is simply in place so we can pass in unused kv pairs during initialization

        print(f"Instantiating actor {name}....")
        self.name = name
        self.effectiveness = effectiveness
        
        # we can't have lists in a database, hence the funny business here
        # take in the list as a space delimited string - then split
        self.attacks                    = "~".join(attacks)
        self.domain_themes              = "~".join(domain_themes)  # adding random words for entropy
        self.sender_themes              = "~".join(sender_themes)
        self.subjects                   = "~".join(subjects)
        self.file_names                 = "~".join(file_names)       # Will end up getting replaces by malware configs
        self.malware                    = "~".join(malware)
        self.recon_search_terms         = "~".join(recon_search_terms)
        self.watering_hole_domains      = "~".join(watering_hole_domains)
        self.watering_hole_target_roles  = "~".join(watering_hole_target_roles)
        self.sender_domains             = "~".join(sender_domains)
        self.tlds                       = "~".join(tlds) or "~".join(['com','net','biz','org','us']) # TODO: Put this in a config or something
        self.spoofs_email               = spoofs_email
        self.generates_infrastructure   = generates_infrastructure
        self.count_init_browsing        = int(count_init_browsing)
        self.count_init_email           = int(count_init_email)
        self.count_init_passive_dns     = int(count_init_passive_dns)
        self.max_wave_size              = int(max_wave_size)
        self.sender_emails              = "~".join(self.gen_sender_addresses())
        self.difficulty                 = difficulty
        self.domain_depth               = domain_depth
        # Timing stuff
        self.activity_start_date        = activity_start_date
        self.activity_end_date          = activity_end_date
        self.activity_start_hour        = activity_start_hour
        self.workday_length_hours       = workday_length_hours
        self.working_days               = "~".join(working_days or ['Monday','Tuesday','Wednesday','Thursday','Friday']) # Default to normal work week

        # post_exploit_commands come in as a list of dictionaries
        # turn the dicts into strings and join the list into a string
        # so list[dict] -> str~str~str
        self.post_exploit_commands      = "~".join([json.dumps(p) for p in post_exploit_commands])
        

    @property
    def is_default_actor(self) -> bool:
        if self.name == "Default":
            return True
        else:
            return False

    @property
    def tld_values(self):
        return Actor.string_to_list(self.tlds)

    @property
    def domain_theme_values(self):
        return list(set(Actor.string_to_list(self.domain_themes)))

    @property
    def domains_list(self):
        return [domain.name for domain in self.domains]
            
    @property
    def ips_list(self):
        return [ip.address for ip in self.ips]

    @property
    def water_hole_domains_list(self):
        return Actor.string_to_list(self.watering_hole_domains)

    @property
    def watering_hole_target_roles_list(self):
        return Actor.string_to_list(self.watering_hole_target_roles)
    
    @property
    def sender_domains_list(self):
        return Actor.string_to_list(self.sender_domains)
    
    @property
    def working_days_list(self) -> list:
        return Company.string_to_list(self.working_days)

    def get_attacks(self) -> "list[str]":
        """
        Converts string representation of file names into list
        """
        attacks = Actor.string_to_list(self.attacks)
        return [f for f in attacks if f!='']

    def get_recon_search_terms(self) -> "list[str]":
        """
        Get a list of recon search terms belonging to the actor
        """
        return Actor.string_to_list(self.recon_search_terms)

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

    
    def get_payload_name(self) -> str:
        pass

    def get_file_names(self) -> "list[str]":
        """
        Converts string representation of file names into list
        """
        return Actor.string_to_list(self.file_names)

    def get_domain(self):
        from app.server.game_functions import LEGIT_DOMAINS

        if self.is_default_actor:
            return random.choice(LEGIT_DOMAINS)
        return random.choice(self.domains_list)


    def get_ips(self, count_of_ips:int=10) -> "list[str]":
        """
        Get a list of IPs for the actor
        """
        actor_ips = [ip.address for ip in self.ips]
        if actor_ips:
            if count_of_ips == 1:
                random.choice(actor_ips)
            return random.choices(actor_ips, k=count_of_ips)
        else:
            return []
        

    def get_email_subject(self) -> str:
        """
        Assemble a subject line using list of theme words from the Actor object
        """
        subjects = Actor.string_to_list(self.subjects) 
        # give it some prefixes for variety
        prefix  = random.choices(["", "RE: ", "FW: ", "RE:RE: "], weights=(60, 20, 15, 5), k=1)[0]
        if subjects:
            return prefix + random.choice(subjects) 
        else:
            return prefix + sentenceGenerator.genSentence() 


    def get_sender_address(self) -> str:
        """
        Return a random email from the actor's pool of email addresses
        If the actor is default, then get a random address each time
        """
        if self.is_default_actor:
            return self.gen_sender_address()
            # print(Actor.string_to_list(self.sender_emails))
        return random.choice(Actor.string_to_list(self.sender_emails))


    def gen_partner_address(self) -> str:
        """
        Returns a partner email address
        """
        company = Company.query.first()

        email_prefix = "_".join(names.get_full_name().split(" ")).lower()
        partner_domain = random.choice(company.get_partners())
        return f"{email_prefix}@{partner_domain}"


    def gen_sender_address(self) -> str:
        """Make a list of fake sender addresses"""
        import names

        sender_themes = Actor.string_to_list(self.sender_themes)

        ### user provided themes, use these to build the sender addresses 
        splitter = random.choice(["", "_", "."])
        # Read actor domains from config
        # If nothing available in the config, choose a freemail provider
        if self.sender_domains_list:
            email_domain = random.choice(self.sender_domains_list)
        else:
            email_domain = random.choice(['yahoo.com', 'gmail.com', 'aol.com', 'verizon.com', 'yandex.com','hotmail.com','protonmail.com','qq.com'])

        if (self.is_default_actor and random.random() < .5)\
            or (not self.is_default_actor):
            # use words for the send prefic
            # all the time for non-default actors
            # half the time for default actor
            # get one or two words from our sender themes
            prefix_parts = random.choices(sender_themes, k=random.randint(1,2))
        else:
            prefix_parts = names.get_full_name().lower().split(" ")
        
        email_prefix = splitter.join(prefix_parts)
        sender_addr = email_prefix + "@" + email_domain
        
        return sender_addr

    def gen_sender_addresses(self, num_emails=5, num_compromised_partner_emails=2) -> "list[str]":
        """
        Generates actor email addresses to be used in email attacks
        Also includes logic to write compromised partner emails
        """
        from app.server.utils import AttackTypes

        if self.sender_themes:
            #if config contains full email addresses, just use those
            if  ("@" in self.sender_themes):
                return Actor.string_to_list(self.sender_themes)

            emails = [self.gen_sender_address() for _ in range(num_emails)]
        else:
            emails = []
        if AttackTypes.SUPPLY_CHAIN_VIA_EMAIL.value in self.get_attacks():
            emails += [self.gen_partner_address() for _ in range(num_compromised_partner_emails)]
        return emails        

    def get_exploit_processes(self) -> "list[str]":
        """
        Converts string representation of file names into list
        """
       
        return [
            json.loads(command) for command in
            self.post_exploit_commands.split("~")
        ]
    

    def __repr__(self):
        return '<Actor %r>' % self.name