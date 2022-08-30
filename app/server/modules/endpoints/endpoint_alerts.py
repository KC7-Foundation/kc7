class EndpointAlert:

    def __init__(self, alert_time:float, hostname:str, message:str) -> None:

        self.alert_time = alert_time
        self.hostname = hostname
        self.message = message

    def stringify(self):
        return {
            "alert_time": self.alert_time,
            "hostname": self.hostname,
            "message": self.message
        }