
from unittest import result
from app.server.modules.clock.Clock import Clock 


class AuthenticationEvent:

    def __init__(self, creation_time:float, hostname:str, src_ip:str, user_agent:str, username:str, result:str) -> None:

        self.creation_time = creation_time
        self.hostname = hostname
        self.src_ip = src_ip
        self.user_agent = user_agent
        self.username = username
        self.result = result
        

    def stringify(self) -> dict:
        return {
            "creation_time": Clock.from_timestamp_to_string(self.creation_time),
            "hostname": self.hostname,
            "src_ip": self.src_ip,
            "user_agent": self.user_agent,
            "result": self.result
        }

    @staticmethod
    def get_kql_repr() -> tuple:
        """Returns table:str, columns:dict"""
        return (
            'AuthenticationEvents',  # table name in KQL
            {                     # dict representation of column names:types
                'creation_time': 'string',
                'hostname': 'string',
                'src_ip': 'string',
                'user_agent': 'string',
                'username': 'string',
                'result': 'int'
            }
        )

    
