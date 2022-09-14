# Import internal modules
from app.server.modules.actors.Actor import Actor
from app.server.models import db, Company, Employee, DNSRecord
from app.server.modules.logging.uploadLogs import LogUploader
from app.server.utils import *

# Import external modules
from flask import current_app
import random


def gen_passive_dns(actor: Actor, count_of_records: int = 1) -> None:
    """
    Generate passive DNS entries 
    This should happen in bulk and the start 
    with a lower stream of entries created as the game goes on

    A dns record is an essentially a ip/domain pair
    For the "Default" actor we create independ ip/domain pairs

    For malicious actors, ip/domain pairs should be associated with each other 
        in order to allow for pivoting. e.g. ip -> new domains -> new ips
    When creating malicious actor dns records
        Select an existing domain and pair it with a new IP  
        OR 
        Select an existing IP and pair it with a new domain
    """
    # For all non-default actors, indicators should be pivotable
    # Result is that 3x number of specified records will be created
    new_records = []

    if actor.name != "Default":
        # This is a malicious actor

        # TODO: if actor isn't default, IPs and Domains should be reused
        # listify DB results
        actor_records = [record for record in actor.dns_records]
        if not actor_records:
            # if no dns records exist, create one
            print("no actor records were found")
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
    from app.server.game_functions import log_uploader

    random.shuffle(dns_records)
    log_uploader.send_request(
        data=dns_records,
        table_name="PassiveDns")
