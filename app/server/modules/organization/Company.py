from os import name
import random
import string
import ipaddress
from json import JSONEncoder
from faker import Faker
from faker.providers import internet, user_agent, person
from sqlalchemy import func
import names

from app.server.models import Base
from app.server.modules.clock.Clock import Clock
from app.server.models import GameSession

from app import db

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
    name                    = db.Column(db.String(50), nullable=False)
    domain                  = db.Column(db.String(50), nullable=False)
    partners                = db.Column(db.String(300))

    def __init__(self, name: str, domain: str, count_employees:int=100, roles:dict={}, partners:list=[]) -> None:
        self.name = name
        self.count_employees = count_employees or 100
        self.roles = roles
        self.partners = "~".join(partners)
        if domain:
            self.domain = domain
        else:
            # If a domain is not provided, take the name and add a random TLD
            self.domain = str.lower("".join(name.split())).replace(",", "") + "." + fake.tld()

        self.count_employees = count_employees
        # this var will allow us to keep count of company employees 
        # without making too many queries to the database
        self.num_generated_ips  = 0

        # cache variables to keep track of used employee mames 
        # so we don't have conflicts
        self.employee_usernames = [employee.username for employee in self.employees]
        self.employee_names = [employee.names for employee in self.employees]
        self.employee_emails = [employee.email_addr for employee in self.employees]
        

    def get_new_employee(self, timestamp:float=None, user_agent:str="", name:str="", days_since_hire:int=0):
        """
        Constructs a single employee instance and returns it.
        This function can take a specific creation time
        or uses days_since_hire to compute accopunt creation time
        """
        # time is returned as timestamp (float)
        # Get the current game session from the database
        current_session = db.session.query(GameSession).get(1)
        time = Clock.get_current_gametime(start_time=current_session.start_time,
                                                    seed_date=current_session.seed_date)
                                                    
        time_since_account_creation = days_since_hire * 24 * 60 * 60 # days to seconds
        account_creation_datetime = Clock.increment_time(time, time_since_account_creation * -1 )

        employee = Employee(
            timestamp=timestamp or account_creation_datetime or Clock.get_current_gametime(),
            name= name or  self.get_employee_name(),
            user_agent=user_agent or fake.chrome(),
            ip_addr=self.get_internal_ip(),
            company=self,
            role=self.get_role()
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

    def get_employee_name(self) -> str:
        """
        Return a name that doesn't have conflicting username as another user
        """
        # get a random name
        name = names.get_full_name()
        # if the name has already been used, try again
        while name in self.employee_names:
            name = names.get_full_name()

        # now get a unique email addr
        # update the cached list of employee names
        self.employee_names.append(name)

        return name

    def get_num_generated_ips(self) -> int:
        """
        Get number of child employee object
        If count_employees is 0 -> pull this number by querying the database
        Else get cached number
        """
        if self.num_generated_ips == 0:
            self.num_generated_ips = self.employees.count()
        
        return self.num_generated_ips


    def get_internal_ip(self) -> str:
        """Assign the employee an IP on the local network"""
        #  IP is 192.168.0.2 + count of employee (using CIDR addition)
        # this tries to reduce chance of IP collisions
    
        ip = format(ipaddress.IPv4Address('192.168.0.2') + self.get_num_generated_ips())
        # increment this -> so we know we have one more employee 
        # without needing to query the DB
        self.num_generated_ips +=1
        
        return ip


    def get_role(self) -> str:
        """
        Get a role from the company's dictionary of possible positions
        Decrement the limit
        Role Dict should look something like: 
          "roles": [
            {
            "role": "Chief Executive Officer",
            "limit": 1
            },
            {
            "role": "Chief Financial Officer",
            "limit": 3
            },
        """
        role = random.choice(self.roles)
        # decrement role because we've already assigned all the slots
        role["limit"] -= 1
        if role["limit"] == 0:
            self.roles.remove(role)
        return role.get('title')

    def get_partners(self) -> str:
        return Company.string_to_list(self.partners)

    def __repr__(self) -> str:
        return '<Company %r>' % self.name
    

class Employee(Base):
    """
    A class that defines the data model for the employee.
    Employees have a number of attributes which are represented in ADX and/or the DB.
    """
    # Define attributes that will be represented in database
    # NOTE: Only the following attributes are returned when retrieving an Employee object from the database
    name                = db.Column(db.String(50))
    user_agent          = db.Column(db.String(50))
    ip_addr             = db.Column(db.String(50))
    home_ip_addr        = db.Column(db.String(50))  # sometimes the user needs to login from home
    awareness           = db.Column(db.Integer)
    email_addr          = db.Column(db.String(50))
    username            = db.Column(db.String(50))
    hostname            = db.Column(db.String(50))
    timestamp           = db.Column(db.String(50))
    role                = db.Column(db.String(50))
    

    # Define database relationships
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    company = db.relationship(
        'Company', backref=db.backref('employees', lazy='dynamic'))

    def __init__(self, name: str, user_agent: str, ip_addr: str, company: Company, 
                timestamp:float, role:str="") -> None:
        self.name = name
        
        self.user_agent = user_agent
        self.ip_addr = ip_addr
        self.home_ip_addr = fake.ipv4_public()
        self.company = company
        # TODO: Make this global setting
        self.awareness = random.randint(30, 90)
        self.timestamp = Clock.from_timestamp_to_string(timestamp)
        self.role = role
        self.set_email()
        self.set_username()
        self.set_hostname()
        

    def set_email(self) -> None:
        """
        Constructs an email address for the employee.
        Email is generated using pattern firstName_lastName@company.domain

        Example: john doe -> john_doe@company.com
        """
        email_addr  = str.lower(
            "_".join(self.name.split(" "))) + '@' + self.company.domain

        counter = 1
        # if the email address is a duplicate, add the counter
        # e.g. john.doe@acme.com -> john.doe1@acme.com
        while email_addr in self.company.employee_emails:
            email_addr  = str.lower(
                "_".join(self.name.split(" "))) + str(counter) + '@' + self.company.domain
            counter += 1
        
        self.company.employee_emails.append(email_addr)
        self.email_addr = email_addr


    def set_username(self) -> None:
        """
        Constructs a username for the employee.
        Username is generated based on first two letter of first name + last name

        Example: john doe -> jodoe
        """
        name_parts = self.name.split(" ")
        username = str.lower(name_parts[0][:2] + name_parts[1])

        counter = 1
        # if the username is a duplicate, add the counter
        # e.g. jdoe -> jdoe1
        while username in self.company.employee_usernames:
            username = str.lower(name_parts[0][:2] + name_parts[1] + str(counter))
            counter += 1

        self.company.employee_usernames.append(username)
        self.username = username

    
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
            "timestamp": self.timestamp,
            "name": self.name,
            "user_agent": self.user_agent,
            "ip_addr": self.ip_addr,
            "email_addr": self.email_addr,
            "company_domain": self.company.domain,
            "username": self.username,
            "role":self.role,
            "hostname": self.hostname,
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
                "timestamp":"string",
                "name": "string",
                "user_agent": "string",
                "ip_addr": "string",
                "email_addr": "string",
                "company_domain": "string",
                "username": "string",
                "role":"string",
                "hostname": "string"
            }
        )
