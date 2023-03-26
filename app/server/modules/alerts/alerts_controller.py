

from app.server.utils import timing
from app.server.modules.alerts.alerts import SecurityAlert


def generate_host_alert(time: float, hostname:str, filename:str, sha256:str, severity="high") -> None:
    """
    Generates a Security Alert for malicious files generated on a host
    {
        "timestamp": 2022-10-03 12:30:00
        "alert_type": self.alert_type,
        "severity": self.severity,
        "description": "Your Antivirus detected alert #Mimikartz123 on host  ",
        "source": self.source
    }
    """

    alert = SecurityAlert(
        time=time,
        alert_type="HOST",
        severity=severity,
        description=f"Your antivirus system detected a suspicious file on host {hostname} with filename {filename}. Sha256: {sha256}"
    )

    send_alert_to_azure(alert)


def generate_email_alert(time: float, username:str, subject:str) -> None:
    """
    Generates a Security Alert for suspicious emails reported by users
    """

    alert = SecurityAlert(
        time=time,
        alert_type="Email",
        severity="med",
        description=f"Employee {username} reported a suspicious email with the subject \"{subject}\""
    )

    send_alert_to_azure(alert)
    

def send_alert_to_azure(alert):
    """
    Upload security alert object to azure
    """
    from app.server.game_functions import LOG_UPLOADER

    LOG_UPLOADER.send_request(
        data=[alert.stringify()],
        table_name="SecurityAlert")
