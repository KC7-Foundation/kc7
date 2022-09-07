
from app import application

if __name__ == '__main__':
    application.run(debug=True)


# * KC1: Inbound browsing (recon)
# * KC2: File malware / metadata - Dummy EDR/Alerts
# - KC3: User receives phishing email / user clicks link
# - KC4: User downloads file
# * KC5: File initiates process?
# * KC6: User machine begins to beacon to C2
# * KC7: Data exfil from user machine / Data encryption / Lateral movement?


# Outstanding tasks

# 1. Legitimate file download (noise)
# 2. User account authentication (implement cred phishing in links)
# 3. C2 - victim machines beacons to actor IP (recorded in outbound browsing)
# 4. Inbound browsing of company web pages (trivial - according to Greg)
# *
# * Actor downloads file from file server (inbound browsing logs)
# 5. Abstract actor confics to YAML? files