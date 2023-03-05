# Import internal modules
from app.server.models import Base
from app.server.modules.clock.Clock import Clock
from app import db

class DNSRecord(Base):
    """ 
    Belongs to an actor
    There should be default actor to own non-malicious infrastructure
    This is not store the database
    """

    def __init__(self, time:float, domain:str, ip:str) -> None: 
        self.time = Clock.from_timestamp_to_string(time)
        self.ip = ip 
        self.domain = domain

    def stringify(self):
        return {
            "timestamp": self.time,
            "ip":self.ip, 
            "domain": self.domain
        }

    @staticmethod
    def get_kql_repr():
        return (
            "PassiveDns",
            {
                "timestamp": "string",
                "ip":"string",
                "domain":"string"
            }
        )