
from flask import current_app
from app.server.models import db, Company, Employee, Actor, DNSRecord
from app.server.modules.logging.uploadLogs import LogUploader
from app.server.utils import *
import random


# def gen_default_passiveDNS():
#     """
#     Generate some passiveDNS entries to start
#     """
#     default_actor = db.session.query(Actor).filter_by(name = "Default").one()
#     gen_passive_dns(default_actor, 100)


# def gen_actor_passiveDNS():
#     """Generate passiveDNS for the bad actors"""
#     actors = Actor.query.filter(Actor.name != "Default").all()
#     for actor in actors:
#         if actor.name != "Default":
#             gen_passive_dns(actor, 10)

def gen_passive_dns(actor, count_of_records=1):
    """
    Generate passive DNS entries 
    This should happen in bulk and the start 
    with a lower stream of entries created as the game goes on
    """
    print(f"Adding {count_of_records} passiveDNS records for {actor.name} actor")
    # For all non-default actors, indicators should be pivotable
    # Result is that 3x number of specified records will be created
    new_records = []

    if actor.name != "Default":
        #TODO: if actor isn;t default, IPs and Domains should be reused
        actor_records = [record for record in actor.dns_records] #listify DB results
        if not actor_records:
            # if no DB records exist, create one
            seed_record = DNSRecord(actor)
            db.session.add(seed_record)
        else:
            # else choose a seed record to pivot on
            seed_record = random.choice(actor_records)

        # IP is known and domain is new
        record = DNSRecord(actor, ip=seed_record.ip)
        # Domain is known and IP is new
        pivot_record = DNSRecord(actor, domain=record.domain)

        # pick one new DNS record based on the two pivot methods above
        new_record = random.choice([record, pivot_record])
        
        # write the new record
        db.session.add(new_record)
        new_records.append(new_record.stringify())
    else:
        # this is the default actor
        for i in range(count_of_records):
            record = DNSRecord(actor)
            new_records.append(record.stringify())
            db.session.add(record)
    try:
        upload_dns_records_to_azure(new_records)
        db.session.commit()
    except Exception as e:
        print(f"Error adding passiveDNS record {e}")


def upload_dns_records_to_azure(dns_records):
    """
    take array of dns_record db objects or json objects
    writes to azure
    """
    uploader = LogUploader()

    random.shuffle(dns_records)
    uploader.send_request(
            data = dns_records,
            table_name= "PassiveDNS")