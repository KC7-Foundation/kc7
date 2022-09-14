from os import name
import random
import string
import json
from json import JSONEncoder
from faker import Faker
from faker.providers import internet, user_agent, person

from app.server.models import Base
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
        self.employees = []
        self.add_employees()

    def add_employees(self, count_employees: int = 50) -> None:
        """
        Generates count_employees number of employees and associates them with the company
        """
        # TODO: Num of employees should be passed in from config
        for i in range(count_employees):
            employee = self.generate_employee()
            self.employees.append(employee)

    def generate_employee(self):
        """
        Constructs a single employee instance and returns it.
        """
        employee = Employee(
            name=fake.name(),
            user_agent=fake.user_agent(),
            # TODO: Let's put these ont the same network
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
        """Create a dummy RFC1918 IP"""
        # TODO: Can we make these all on the same subnet?
        return fake.ipv4_private()

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

    # Define database relationships
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    company = db.relationship(
        'Company', backref=db.backref('employees', lazy='dynamic'))

    def __init__(self, name: str, user_agent: str, ip_addr: str, company: Company) -> None:
        self.name = name
        self.user_agent = user_agent
        self.ip_addr = ip_addr
        self.company = company
        # TODO: Make this global setting
        self.awareness = random.randint(30, 90)
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
                "name": "string",
                "user_agent": "string",
                "ip_addr": "string",
                "email_addr": "string",
                "company_domain": "string",
                "username": "string",
                "hostname": "string"
            }
        )
