# Import internal modules
from app.server.modules.actors.Actor import Actor
from app.server.models import db
from app.server.modules.infrastructure.DNSRecord import DNSRecord
from app.server.modules.infrastructure.Infrastructure import Domain, IP
from app.server.modules.logging.uploadLogs import LogUploader
from app.server.utils import *
from app.server.modules.clock.Clock import Clock

# Import external modules
from flask import current_app
from datetime import datetime, date, time
import random
import tldextract

def difficulty_to_dns_threads(difficulty):
    """
    Takes difficulty as EASY, MEDIUM, or HARD
    Return number of DNS "threads" to generate
    """
    mapping = {
        "EASY": 2,
        "MEDIUM": 5,
        "HARD":10
    }

    try:
        return mapping.get(difficulty.upper())
    except:
        raise Exception("Invalid difficulty assigned")


@timing
def gen_passive_dns(actor: Actor, current_date: date, count_of_records: int = 1000) -> None:
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
    # print(f"Generting {count_of_records} records for actor {actor}")
    new_records = []

    if not actor.is_default_actor and actor.generates_infrastructure:
        # This is a malicious actor

        # TODO: Check if this actor is actually supposed to generate infra
        base_time = datetime.timestamp(Clock.generate_bimodal_timestamp(start_date=current_date, start_hour=actor.activity_start_hour, day_length=actor.workday_length_hours))
        for i in range(count_of_records):
            if actor.domains_list and actor.ips:            
                if random.random() < current_app.config['RATE_DOMAIN_RESOLVES_TO_NEW_IP']:
                    # half the time
                    #choose an existing domain and give it a new ip
                    new_ip =IP(actor=actor)
                    timestamp = Clock.delay_time_by(base_time, factor="days", is_negative=True)

                    new_record = DNSRecord(
                        time=timestamp,
                        domain = actor.get_domain(), 
                        ip = new_ip.address
                    )
                    db.session.add(new_ip)
                else:
                    # the other half the time
                    # choose an existing ip and give it a new domain
                    new_domain = Domain(actor=actor)
                    timestamp = Clock.delay_time_by(base_time, factor="days", is_negative=True)

                    new_record = DNSRecord(
                        time=timestamp,
                        domain = new_domain.name, 
                        ip=random.choice(actor.ips_list)
                    )
                    db.session.add(new_domain)
            else:
                ### ONLY WHEN NO DOMAINS EXISTS
                ### CREATE THREE IP/DOMAIN PAIRS
                num_threads = difficulty_to_dns_threads(actor.difficulty)
                for i in range(num_threads):  # This shoudl be defined on the actor
                    domain = Domain(actor=actor)
                    ip = IP(actor=actor)
                    timestamp = Clock.delay_time_by(base_time, factor="days", is_negative=True)

                    new_record = DNSRecord(
                        time=timestamp,
                        domain=domain.name, 
                        ip=ip.address
                    )

                    db.session.add(domain)
                    db.session.add(ip)
                    new_records.append(new_record.stringify())
                db.session.commit()

            db.session.add(new_record) 
            new_records.append(new_record.stringify())
    else:
        # this is the default actor
        # Time of day doesn't matter for default PDNS
        rand_time = time(
                hour=random.randint(0,23),
                minute=random.randint(0,59),
                second=random.randint(0,59)
            )
        default_datetime = datetime.timestamp(datetime.combine(current_date,rand_time))
        for i in range(count_of_records):
            #better randomization + fix for tldextract
            curr_dt = datetime.now()
            seed_value = int(round(curr_dt.timestamp()))
            random.seed(seed_value+random.randint(0,999999))
            ext = tldextract.extract(Domain(actor=actor).name)
            url = '.'.join(ext[:3])
            record = DNSRecord(
                time = Clock.delay_time_by(default_datetime, factor="days", is_negative=True),
                domain=url,
                ip=IP(actor=actor).address
            )
            new_records.append(record.stringify())
            db.session.add(record)
        db.session.commit()

    upload_dns_records_to_azure(new_records)
        


def upload_dns_records_to_azure(dns_records):
    """
    take array of dns_record db objects or json objects
    writes to azure
    """
    from app.server.game_functions import LOG_UPLOADER

    random.shuffle(dns_records)
    for record in dns_records:
        LOG_UPLOADER.send_request(
            data=record,
            table_name="PassiveDns")
