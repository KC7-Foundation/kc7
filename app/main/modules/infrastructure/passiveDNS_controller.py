
from flask import current_app
from app.main.models import db, Company, Employee, Actor, DNSRecord
from app.main.modules.logging.uploadLogs import LogUploader
from app.main.utils import *
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

def gen_passive_dns(actor, count_of_records):
    """
    Generate passive DNS entries 
    This should happen in bulk and the start 
    with a lower stream of entries created as the game goes on
    """
    # For all non-default actors, indicators should be pivotable
    # Result is that 3x number of specified records will be created
    new_records = []

    if actor.name != "Default":
        for i in range(count_of_records):
            #TODO: if actor isn;t default, IPs and Domains should be reused
            actor_records = [record for record in actor.dns_records]
            if not actor_records:
                seed_record = DNSRecord(actor)
                db.session.add(seed_record)
            else:
                seed_record = random.choice(actor_records)

            for i in range(random.randint(1,3)):
                # IP is known and domain is new
                record = DNSRecord(actor, ip=seed_record.ip)
                #print(record.stringify())
                db.session.add(record)
                # Domain is known and IP is new
                pivot_record = DNSRecord(actor, domain=record.domain)
                #print(pivot_record.stringify())
                db.session.add(pivot_record)
                new_records.append(record)
                new_records.append(pivot_record)
    else:
        for i in range(count_of_records):
            record = DNSRecord(actor)
            db.session.add(record)
            new_records.append(record)
    try:
        #print(f"Adding {count_of_records} passiveDNS records")
        upload_dns_records_to_azure(new_records)
        db.session.commit()
    except Exception as e:
        print(f"Error adding passiveDNS record {e}")

def upload_dns_records_to_azure(dns_records):
    """
    take array of dns_record db objects
    writes to azure
    """
    stringified_records = [record.stringify() for record in dns_records]

    uploader = LogUploader(
        log_type = current_app.config["LOG_PREFIX"] + "_PassiveDns",
        data = stringified_records
    )

    uploader.send_request()