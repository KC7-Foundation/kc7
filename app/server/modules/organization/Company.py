from os import name
import random
import json
from json import JSONEncoder
from faker import Faker
from faker.providers import internet, user_agent, person
#import Employee

# instantiate faker
fake = Faker()
fake.add_provider(internet)
fake.add_provider(user_agent) 
fake.add_provider(person)

#print(NAMES)

class CompanyShell():

    def __init__(self, name, domain, description="A company that makes money") -> None:
        
        self.name = name
        if domain:
            self.domain = domain
        else:
            self.domain = str.lower("".join(name.split())).replace(",", "") + "." + fake.tld()
        self.description = description
        self.employees = []
        self.add_employees()
        
    def add_employees(self, count_employees=50): 
        for i in range(count_employees):
            employee = self.generate_employee()
            self.employees.append(employee)

    def generate_employee(self):
        employee = EmployeeShell(
            name = fake.name(),
            user_agent = fake.user_agent(),
            ip_addr = self.generate_ip(),
            company_domain = self.domain
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
    
    
class EmployeeShell():

    def __init__(self, name, user_agent, ip_addr, company_domain) -> None:
        
        self.name = name
        self.user_agent = user_agent
        self.ip_addr = ip_addr
        self.company_domain = company_domain
        self.awareness = random.randint(30, 90)
        self.set_email()

    def set_email(self):
        self.email_addr = str.lower("_".join(self.name.split(" "))) + '@' + self.company_domain

    def stringify(self):
        return {
            "name": self.name,
            "user_agent": self.user_agent,
            "ip_addr": self.ip_addr,
            "email_addr": self.email_addr,
            "company_domain": self.company_domain
        }