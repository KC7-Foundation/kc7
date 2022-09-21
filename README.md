![Admin Central button](readme_assets/kc7.png)

# KC7 - a cybersecurity game 

KC7 simulates an intrusion by multiple cyber threat actors against a fictitious company that spans the entire `Cyber Kill Chain`.

Players use `KQL` queries to triage logs in `Azure Data Explorer` to:
* Investigate suspicious activity in the company's environment
* Pivot on known actor indicators to uncover additional selectors and find more intrusion activity

Game players get experience triaging Web, Email, and Endpoint audit logs

### How it works 

<img src="readme_assets/how.png" width=700 >

### Here's an example scenario
<img src="readme_assets/example.png" width=700 >




## 👨🏽‍🎓 Who is this for?

* High school and college **students** who have an interest in Cybersecurity
* Anyone who wants to **reskill/change careers** into the cybersecurity field
* Cybersecurity professionals looking to **uplevel** their pivoting and analysis skills


## 🏁 Getting Started

Clone the repo

```
git clone https://github.com/kkneomis/cyber-challenger.git
```

Install the required python packages
```
pip install -r requirements.txt
```

Run the project
```python
python3 app.py
```

Access the Guid by browsing to your local server @ `http://127.0.0.1:5000/`


Browsing to the Login page: `http://127.0.0.1:5000/login` and login to the adminitator account using default creds `admin:admin`

Click on `Admin Central` in the left sidebar to get to the admin page

![Admin Central button](readme_assets/admin.png)


Click `Start Game` to begin generating logs. The logs will be printed to your console (until you  configure your Azure secrets).

![Start button](readme_assets/start.png)


## 🤠 How to contribute

Go check out the wiki for details on how the code base is structured

## 👯 Contributors

* Simeon Kakpovi
* Greg Schloemer
* Alton Henley
* Andre Murrell

