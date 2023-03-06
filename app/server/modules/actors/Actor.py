# Import external modules
import random
import json
from faker import Faker
import glob
from faker.providers import internet
import names

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
    domain_themes               = db.Column(db.String(300))
    sender_themes               = db.Column(db.String(300))
    subjects                    = db.Column(db.String(300))
    file_names                  = db.Column(db.String(300))
    tlds                        = db.Column(db.String(300))
    malware                     = db.Column(db.String(300))
    recon_search_terms          = db.Column(db.String(300))
    post_exploit_commands       = db.Column(db.String(1000))
    sender_emails               = db.Column(db.String(300))
    watering_hole_domains       = db.Column(db.String(300))
    watering_hole_target_roles  = db.Column(db.String(300))

    count_init_passive_dns      = db.Column(db.Integer)
    count_init_email            = db.Column(db.Integer)
    count_init_browsing         = db.Column(db.Integer)   # >:D
    max_wave_size               = db.Column(db.Integer) 
    difficulty                  = db.Column(db.String(50))

    #options for what an actor can do
    generates_infrastructure    = db.Column(db.Boolean)
    spoofs_email                = db.Column(db.Boolean)
    
    

    def __init__(self, name:str, effectiveness:int=50, domain_themes:list=[], sender_themes:list=[], 
                subjects:list=[],  tlds:list=[], spoofs_email:bool=False, generates_infrastructure:bool=True, 
                count_init_passive_dns:int=100, count_init_email:int=1, count_init_browsing:int=2, max_wave_size:int=2,
                file_names:list=[], file_extensions:list=[], attacks:list=[], malware:list=[], recon_search_terms:list=[],
                post_exploit_commands:list=[], difficulty="HARD", watering_hole_domains:list=[], watering_hole_target_roles:list=[]):

        print(f"Instantiating actor {name}....")
        self.name = name
        self.effectiveness = effectiveness
        
        # we can't have lists in a database, hence the funny business here
        # take in the list as a space delimited string - then split
        self.attacks                    = "~".join(attacks)
        self.domain_themes              = "~".join(domain_themes + wordGenerator.get_words(10))  # adding random words for entropy
        self.sender_themes              = "~".join(sender_themes)
        self.subjects                   = "~".join(subjects)
        self.file_names                 = "~".join(file_names)       # Will end up getting replaces by malware configs
        self.malware                    = "~".join(malware)
        self.recon_search_terms         = "~".join(recon_search_terms)
        self.watering_hole_domains      = "~".join(watering_hole_domains)
        self.watering_hole_target_roles  = "~".join(watering_hole_target_roles)
        self.tlds                       = "~".join(tlds) or "~".join(['com','net','biz','org','us']) # TODO: Put this in a config or something
        self.spoofs_email               = spoofs_email
        self.generates_infrastructure   = generates_infrastructure
        self.count_init_browsing        = int(count_init_browsing)
        self.count_init_email           = int(count_init_email)
        self.count_init_passive_dns     = int(count_init_passive_dns)
        self.max_wave_size              = int(max_wave_size)
        self.sender_emails              = "~".join(self.gen_sender_addresses())
        self.difficulty                 = difficulty

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
        return Actor.string_to_list(self.domain_themes)

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

    def get_hacky_domain_name(self) -> str:
        """
        Assemble a domain name using the list of theme words from the Actor object
        THIS IS A HACK given that these don't apprea in the passiveDNSls
        """
        separators = ["","-" ]
        tlds = Actor.string_to_list(self.tlds)  
        
        # if actor is default, let's get a larger list of randomised words
        if self.name == "Default":
            domain_themes = wordGenerator.get_words(1000)
        else:
            # Splitting string representation of list from db into actual list
            domain_themes = Actor.string_to_list(self.domain_themes) 

        words = random.choices(domain_themes, k=random.randint(1,2))
        domain = random.choice(separators).join(list(set(words))) + "." + random.choice(tlds)

        return domain

    def get_domain(self):
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
        if subjects:
            return random.choice(subjects)
        else:
            return sentenceGenerator.genSentence()


    def get_sender_address(self) -> str:
        """
        Return a random email from the actor's pool of email addresses
        If the actor is default, then get a random address each time
        """
        if self.is_default_actor:
            return self.gen_sender_address()
        else:
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
        sender_themes = Actor.string_to_list(self.sender_themes) 

         # TODO: Centralize this list of freemail providers somewhere else (probably constants?)
         # let's not use all of the domains for every actor. this minimized their legitimacy as a TTP
        email_domains = random.choices(
            ['yahoo.com', 'gmail.com', 'aol.com', 'verizon.com', 'yandex.com','hotmail.com','protonmail.com','qq.com'],
            k=random.randint(1,3)
        )

        # just for fun: add and actor domain in the mix: so 1/8 chance senderd domain will be actor domain
        # TODO: make this selectable 
        email_domains.append(self.get_hacky_domain_name())
        # senders will come in one of two flavors
        # 1. themed_word@freemail.com
        # 2. themed_word@actordomain.com
       
        # get one or two words from our sender themes
        words = random.choices(sender_themes, k=random.randint(1,2))
        

        splitter = random.choice(["", "_", "."])
        sender_addr = splitter.join(words) + "@" + random.choice(email_domains)
        
        return sender_addr

    def gen_sender_addresses(self, num_emails=5, num_compromised_partner_emails=2) -> "list[str]":
        """
        Generates actor email addresses to be used in email attacks
        Also includes logic to write compromised partner emails
        """
        from app.server.utils import AttackTypes

        emails = [self.gen_sender_address() for _ in range(num_emails)]
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