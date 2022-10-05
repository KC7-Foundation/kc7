
from unittest import result
from app.server.modules.clock.Clock import Clock 


class AuthenticationEvent:

    def __init__(self, timestamp:float, hostname:str, src_ip:str, user_agent:str, username:str, result:str) -> None:

        self.timestamp = timestamp
        self.hostname = hostname
        self.src_ip = src_ip
        self.user_agent = user_agent
        self.username = username
        self.result = result
        

    def stringify(self) -> dict:
        return {
            "timestamp": Clock.from_timestamp_to_string(self.timestamp),
            "hostname": self.hostname,
            "src_ip": self.src_ip,
            "user_agent": self.user_agent,
            "username": self.username,
            "result": self.result
        }

    @staticmethod
    def get_kql_repr() -> tuple:
        """Returns table:str, columns:dict"""
        return (
            'AuthenticationEvents',  # table name in KQL
            {                     # dict representation of column names:types
                'timestamp': 'string',
                'hostname': 'string',
                'src_ip': 'string',
                'user_agent': 'string',
                'username': 'string',
                'result': 'int'
            }
        )

    
