from os import name
import random
import string
import ipaddress
from json import JSONEncoder
from faker import Faker
from faker.providers import internet, user_agent, person
from sqlalchemy import func

from app.server.models import Base
from app.server.modules.clock.Clock import Clock
from app.server.models import GameSession

from app import db

#import Employee

# instantiate faker
fake = Faker()
fake.add_provider(internet)
fake.add_provider(user_agent)
fake.add_provider(person)


class Company(Base):
    """
    A class that defines the model for the company.
    The company has a name, a domain name, and a set of employees.
    The company is represented in the DB.
    """
    # Define attributes that will be represented in database
    name        = db.Column(db.String(50), nullable=False)
    domain      = db.Column(db.String(50), nullable=False)

    def __init__(self, name: str, domain: str) -> None:
        self.name = name
        if domain:
            self.domain = domain
        else:
            # If a domain is not provided, take the name and add a random TLD
            self.domain = str.lower("".join(name.split())).replace(",", "") + "." + fake.tld()
        


    def get_new_employee(self, creation_time:float=None, user_agent:str="", name:str="", days_since_hire:int=0):
        """
        Constructs a single employee instance and returns it.
        This function can take a specific creation time
        or uses days_since_hire to compute accopunt creation time
        """
        # time is returned as timestamp (float)
        #Get the current game session from the database
        current_session = db.session.query(GameSession).get(1)
        time = Clock.get_current_gametime(start_time=current_session.start_time,
                                                    seed_date=current_session.seed_date)
                                                    
        time_since_account_creation = days_since_hire * 24 * 60 * 60 # days to seconds
        account_creation_datetime = Clock.increment_time(time, time_since_account_creation * -1 )

        employee = Employee(
            creation_time=creation_time or account_creation_datetime or Clock.get_current_gametime(),
            name=name or fake.name(),
            user_agent=user_agent or fake.user_agent(),
            ip_addr=self.generate_ip(),
            company=self
        )

        return employee

    def get_employees(self) -> "list[Employee]":
        """
        Getter function to return all employees associated with a company
        """
        return self.employees

    def get_jsonified_employees(self) -> "list[dict[str,str]]":
        """
        Returns the JSON representation for every employee associated with the company.
        """
        return [employee.stringify() for employee in self.employees]


    def generate_ip(self) -> str:
        """Assign the employee an IP on the local network"""
        # get the largest assigned IP addr and add 1
        # this ensures we don't have IP collisions
        # TODO: make thid better
        company =  db.session.query(Company).get(1)
        count_of_existing_employees = company.employees.count()
        return format(ipaddress.IPv4Address('192.168.0.2') + count_of_existing_employees)

    def __repr__(self) -> str:
        return '<Company %r>' % self.name


class Employee(Base):
    """
    A class that defines the data model for the employee.
    Employees have a number of attributes which are represented in ADX and/or the DB.
    """
    # Define attributes that will be represented in database
    # NOTE: Only the following attributes are returned when retrieving an Employee object from the database
    name = db.Column(db.String(50))
    user_agent = db.Column(db.String(50))
    ip_addr = db.Column(db.String(50))
    awareness = db.Column(db.Integer)
    email_addr = db.Column(db.String(50))
    username = db.Column(db.String(50))
    hostname = db.Column(db.String(50))
    creation_time = db.Column(db.String(50))
    

    # Define database relationships
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    company = db.relationship(
        'Company', backref=db.backref('employees', lazy='dynamic'))

    def __init__(self, name: str, user_agent: str, ip_addr: str, company: Company, creation_time:float) -> None:
        self.name = name
        
        self.user_agent = user_agent
        self.ip_addr = ip_addr
        self.company = company
        # TODO: Make this global setting
        self.awareness = random.randint(30, 90)
        self.creation_time = Clock.from_timestamp_to_string(creation_time)
        self.set_email()
        self.set_username()
        self.set_hostname()
        

    def set_email(self) -> None:
        """
        Constructs an email address for the employee.
        Email is generated using pattern firstName_lastName@company.domain

        Example: john doe -> john_doe@company.com
        """
        self.email_addr = str.lower(
            "_".join(self.name.split(" "))) + '@' + self.company.domain

    def set_username(self) -> None:
        """
        Constructs a username for the employee.
        Username is generated based on first two letter of first name + last name

        Example: john doe -> jodoe
        """
        name_parts = self.name.split(" ")
        self.username = str.lower(name_parts[0][:2] + name_parts[1])

    def set_hostname(self) -> None:
        """
        Constructs a hostname for the employee's device.
        Randomly choose some letters and numbers, and appends a device identified

        Example: X7O9-DESTOP
        """
        prefix = random.choices(string.ascii_letters + string.digits, k=4)
        prefix = str.upper("".join(prefix))
        postfix = random.choice(["DESKTOP", "LAPTOP", "MACHINE"])
        self.hostname = f"{prefix}-{postfix}"

    def stringify(self) -> "dict[str,str]":
        """
        A function to return the JSON representation of the employee object.
        Used for uploading data to ADX.
        """
        return {
            "creation_time": self.creation_time,
            "name": self.name,
            "user_agent": self.user_agent,
            "ip_addr": self.ip_addr,
            "email_addr": self.email_addr,
            "company_domain": self.company.domain,
            "username": self.username,
            "hostname": self.hostname
        }

    @staticmethod
    def get_kql_repr() -> "tuple[str,dict[str,str]]":
        """
        A static helper method for defining the ADX schema
        Returns a tuple
        (table_name:str, 
        column_types:dict)
        The column_types dict contains a mapping of column_name:data_type
        """
        return (
            "Employees",  # table name
            {             # type dict
                "creation_string":"string",
                "name": "string",
                "user_agent": "string",
                "ip_addr": "string",
                "email_addr": "string",
                "company_domain": "string",
                "username": "string",
                "hostname": "string"
            }
        )
