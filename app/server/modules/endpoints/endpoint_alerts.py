class EndpointAlert:
    """
    A class that represents the data model for EndpointAlert events.
    EndpointAlerts are EDR-style alerts that will be surfaced about malicious activity on an endpoint.

    This functionality is not yet implemented
    """

    def __init__(self, alert_time: float, hostname: str, message: str) -> None:

        self.alert_time = alert_time
        self.hostname = hostname
        self.message = message

    def stringify(self):
        return {
            "alert_time": self.alert_time,
            "hostname": self.hostname,
            "message": self.message
        }
