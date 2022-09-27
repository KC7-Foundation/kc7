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

# instantiate faker
fake = Faker()
fake.add_provider(internet)
fake.add_provider(person)
fake.add_provider(company)


def upload_employee_to_azure(employee: Employee) -> None:
    """
    Take a Company object and uploads the employee data to Azure
    """
    from app.server.game_functions import log_uploader

    log_uploader.send_request(
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
    company_name = "Acme Corp " #fake.company()
    company_domain = "acme.com"  # TODO: Pull this in from somewhere else

    # instantiate a company object
    company = Company(
            name=company_name,
            domain=company_domain
    )
     # add the company to the database
    db.session.add(company)
    db.session.commit()

    # Create 100 employees that work for the company
    # Specify how long they have been working at the company
    employees = []
    count_of_employees = 100
    for _ in range(count_of_employees):
        # employees have worked for the company from 6months - 10years
        days_since_hire = random.randint(60, 365*10)
        new_employee = company.get_new_employee(
                            days_since_hire=days_since_hire
                        )
        employees.append(new_employee)

        # this is not efficient ... but part of a workaround to avoid IP collisions
        # db must be aware of all employees during creation process
        db.session.add(new_employee)
        db.session.commit()
        upload_employee_to_azure(new_employee)

       

    print("Generating company employees")
    # Add the employees to the database
    # add the employees to Azure
    for employee in employees:
        db.session.add(employee)
        

        


    print("Added a new company", 'success')

    
