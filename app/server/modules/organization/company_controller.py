# Import internal modules
from app.server.models import db, Company, Employee, Actor, DNSRecord
from app.server.modules.organization.Company import CompanyShell, EmployeeShell

from flask import current_app
from app.server.modules.logging.uploadLogs import LogUploader
from faker import Faker
from faker.providers import internet, person, company

# instantiate faker
fake = Faker()
fake.add_provider(internet)
fake.add_provider(person)
fake.add_provider(company)

def upload_company_to_azure(company_shell):
    """
    Take a CompanyShell object and uploads the employee data to Azure
    """

    uploader = LogUploader()
    try:
        uploader.create_tables()
    except:
        #tables exist
        pass

    uploader.send_request(
            data = company_shell.get_jsonified_employees(),
            table_name= "CompanyInfo")

def create_company():
    """"
    Create the company and its associated users
    Start with the company shell
    """
    companies = Company.query.all()
    if len(companies) < 1:
        print("No companies exist. Creating one now.")

        company_name = fake.company()
        company_shell = CompanyShell(
            name=company_name,
            domain="dummy.com"
        )
        try:
            # Create a database object for the Company and the auto create employees
            company = Company(
                name=company_shell.name,
                domain=company_shell.domain
            )
            db.session.add(company)

            for employee_shell in company_shell.employees:
                # Creating an employee database object
                employee = Employee(
                    name = employee_shell.name,
                    user_agent =  employee_shell.user_agent,
                    ip_addr = employee_shell.ip_addr,
                    awareness = employee_shell.awareness,
                    email_addr = employee_shell.email_addr,
                    company = company
                )
                db.session.add(employee)
            db.session.commit()
        except Exception as e:
            print('Failed to create company.', e)
        print("Added a new company", 'success')

        upload_company_to_azure(company_shell)

    print("A company already exists. Skipping.")