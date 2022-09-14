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

    # Define attributes that will be represented in database
    name = db.Column(db.String(50), nullable=False)
    domain = db.Column(db.String(50), nullable=False)

    # Define relationships to other databases
    # employee        = db.relationship('Employee', backref=db.backref('employees', lazy='dynamic'))

    def __init__(self, name: str, domain: str) -> None:
        self.name = name
        if domain:
            self.domain = domain
        else:
            self.domain = str.lower("".join(name.split())).replace(
                ",", "") + "." + fake.tld()
        self.employees = []
        self.add_employees()

    def add_employees(self, count_employees: int = 50):
        # TODO: Num of employees should be passed in from config
        for i in range(count_employees):
            employee = self.generate_employee()
            self.employees.append(employee)

    def generate_employee(self):
        employee = Employee(
            name=fake.name(),
            user_agent=fake.user_agent(),
            # TODO: Let's put these ont the same network
            ip_addr=self.generate_ip(),
            company=self
        )

        return employee

    def get_employees(self):
        return self.employees

    def get_jsonified_employees(self):
        return [employee.stringify() for employee in self.employees]

    def get_serialized_employees(self):
        return [json.dumps(employee.stringify()) for employee in self.employees]

    def generate_ip(self):
        """Create a dummy IP addr"""
        return fake.ipv4_private()

    def __repr__(self):
        return '<Company %r>' % self.name


class Employee(Base):

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
        self.email_addr = str.lower(
            "_".join(self.name.split(" "))) + '@' + self.company.domain

    def set_username(self) -> None:
        name_parts = self.name.split(" ")
        # first two letters of first name + last name
        # john doe -> jodoe
        self.username = str.lower(name_parts[0][:2] + name_parts[1])

    def set_hostname(self) -> None:
        # X7O9-DESTOP
        prefix = random.choices(string.ascii_letters + string.digits, k=4)
        prefix = str.upper("".join(prefix))
        postfix = random.choice(["DESKTOP", "LAPTOP", "MACHINE"])
        self.hostname = f"{prefix}-{postfix}"

    def stringify(self):
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
    def get_kql_repr():
        return (
            "Employees",  # table name
            {                # type dict
                "name": "string",
                "user_agent": "string",
                "ip_addr": "string",
                "email_addr": "string",
                "company_domain": "string",
                "username": "string",
                "hostname": "string"
            }
        )
