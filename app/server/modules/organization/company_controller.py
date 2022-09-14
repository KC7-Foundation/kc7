# Import internal modules
from app.server.models import db
from app.server.modules.organization.Company import Company
from app.server.modules.logging.uploadLogs import LogUploader

# Import external modules
from flask import current_app
from faker import Faker
from faker.providers import internet, person, company

# instantiate faker
fake = Faker()
fake.add_provider(internet)
fake.add_provider(person)
fake.add_provider(company)


def upload_company_to_azure(company: Company) -> None:
    """
    Take a Company object and uploads the employee data to Azure
    """
    from app.server.game_functions import log_uploader

    for employee in company.get_jsonified_employees():
        log_uploader.send_request(
            data=employee,
            table_name="Employees")


def create_company():
    """"
    Create the company and its associated users
    Start with the company shell
    """
    print("Setting up the company")
    companies = Company.query.all()

    if any(companies):
        # company already exists return
        return

    print("No companies exist. Creating one now.")
    company_name = fake.company()
    company_domain = "acme.com"  # TODO: Pull this in from somewhere else

    company = Company(
            name=company_name,
            domain=company_domain
    )

    try:
        # Add the company object to the database
        # This might throw an error, so we do it in a try
        db.session.add(company)

        print("Generating company employees")
        for employee in company.employees:
            db.session.add(employee)
        db.session.commit()
    except Exception as e:
        print('Failed to create company.', e)
    print("Added a new company", 'success')

    upload_company_to_azure(company)
