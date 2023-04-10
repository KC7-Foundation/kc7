import random 

# Import external modules
from flask import current_app
from faker import Faker
from faker.providers import internet, person, company

# Import internal modules
from app.server.models import db
from app.server.modules.organization.Company import Company, Employee
from app.server.modules.logging.uploadLogs import LogUploader
from app.server.modules.clock.Clock import Clock
from app.server.modules.helpers.config_helper import read_config_from_yaml

# instantiate faker
fake = Faker()
fake.add_provider(internet)
fake.add_provider(person)
fake.add_provider(company)


def upload_employee_to_azure(employee: Employee) -> None:
    """
    Take a Company object and uploads the employee data to Azure
    """
    from app.server.game_functions import LOG_UPLOADER

    LOG_UPLOADER.send_request(
        data=employee.stringify(),
        table_name="Employees")


def create_company():
    """"
    Create the company and its associated users
    Start with the company shell
    """
    print("Setting up the company")

    # we only want to have one company for now
    # if company already exists, return
    companies = Company.query.all()
    if any(companies):
        return

    print("No companies exist. Creating one now.")
    # loads json file as diction
    company_config = read_config_from_yaml('app/game_configs/company.yaml')
    # instantiate a company object using config info
    # print(company_config)
    company = Company(
            **company_config
    )
     # add the company to the database
    

    # Create 100 employees that work for the company
    # Specify how long they have been working at the company
    employees = []
    for _ in range(company.count_employees):
        # employees have worked for the company from 6months - 10years
        days_since_hire = random.randint(60, 365*10)
        new_employee = company.get_new_employee(
                            days_since_hire=days_since_hire
                        )
        employees.append(new_employee)
        db.session.add(new_employee)
        # this is not efficient ... but part of a workaround to avoid IP collisions
        # db must be aware of all employees during creation process
        upload_employee_to_azure(new_employee)


    print("Generating company employees")
    # Add the employees to the database
    # add the employees to Azure
    db.session.add(company)
    db.session.commit()
    