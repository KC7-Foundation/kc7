import random 

from app.server.modules.organization.Company import Company, Employee
from app.server.modules.actors.Actor import Actor

#If it's the Employee table, update the guide! 
def populate_guide():
    from app.server.game_functions import PARTNER_DOMAINS

    actors = Actor.query.all()
    company = Company.query.get(1)

    #Append to guide
    COMPANY_DOMAIN = company.domain
    
    with open('app/server/modules/constants/template_guide.txt','r') as f:
        data = f.read()
        data = data.replace('{{COMPANY_NAME}}',company.name)
        partner_int = 1
        for partner in PARTNER_DOMAINS: 
            temp_name = "PARTNER_DOMAIN_" + str(partner_int)
            try: 
                if partner_int == 1: 
                    PARTNER_DOMAIN_1 = temp_name
                elif partner_int == 2:
                    PARTNER_DOMAIN_2 = temp_name
                elif partner_int == 3:
                    PARTNER_DOMAIN_3 = temp_name
                elif partner_int == 4:
                    PARTNER_DOMAIN_4 = temp_name
            except:
                print('Error adding PARTNER_DOMAIN variable')
            data = data.replace('{{' + temp_name + '}}',partner)
            partner_int = partner_int + 1
        with open (company.domain+".md", "w") as w: 
            w.write(data)

        #ADD Keyword
    for actor in actors:
        if not actor.is_default_actor:
            try:
                RANDOM_ACTOR_KEYWORD = random.choice(actor.sender_themes)
                RANDOM_ACTOR_DOMAIN = random.choice(actor.domains_list)
                with open(COMPANY_DOMAIN+".md",'r') as f:
                    data = f.read()
                    data = data.replace('{{RANDOM_ACTOR_KEYWORD}}', RANDOM_ACTOR_KEYWORD)
                    data = data.replace('{{RANDOM_ACTOR_DOMAIN}}', RANDOM_ACTOR_DOMAIN)
                with open (COMPANY_DOMAIN+".md",'r') as w:
                    w.write(data)
            except Exception as e:
                print(f'COULDNT ADD RANDOM KEYWORDS: {e}')

    user1_int = random.randint(0,50)
    user2_int = random.randint(51,75)
    user3_int = random.randint(76,100)
    user4_int = random.randint(101,150)
    
    COMPANY_USER_1_NAME = Employee.query.get(user1_int).name
    COMPANY_USER_1_FNAME = COMPANY_USER_1_NAME.split(" ")[0]
    COMPANY_USER_1_EMAIL = Employee.query.get(user1_int).email_addr
    COMPANY_USER_2_NAME = Employee.query.get(user2_int).name
    COMPANY_USER_2_EMAIL = Employee.query.get(user2_int).email_addr
    COMPANY_USER_3_NAME = Employee.query.get(user4_int).name
    COMPANY_USER_3_IP = Employee.query.get(user3_int).ip_addr
    COMPANY_USER_4_NAME = Employee.query.get(user4_int).name
    COMPANY_USER_4_IP = Employee.query.get(user4_int).ip_addr

    #Create new guide
    with open(COMPANY_DOMAIN+".md",'r') as f:
        data = f.read()
        data = data.replace('{{COMPANY_DOMAIN}}', COMPANY_DOMAIN)
        data = data.replace('{{COMPANY_USER_1_NAME}}', COMPANY_USER_1_NAME)
        data = data.replace('{{COMPANY_USER_1_FNAME}}', COMPANY_USER_1_FNAME)
        data = data.replace('{{COMPANY_USER_1_EMAIL}}', COMPANY_USER_1_EMAIL)
        data = data.replace('{{COMPANY_USER_2_NAME}}', COMPANY_USER_2_NAME)
        data = data.replace('{{COMPANY_USER_3_NAME}}', COMPANY_USER_3_NAME)
        data = data.replace('{{COMPANY_USER_3_IP}}', COMPANY_USER_3_IP)
        data = data.replace('{{COMPANY_USER_4_NAME}}',COMPANY_USER_4_NAME)
        with open (COMPANY_DOMAIN+".md", "w") as w: 
            w.write(data)
    # with open ("questions.txt","a") as file:
    #     #Q2
    #     file.write('Question 2 - Total Employees: ' + str(len(Employee.query.all())) + "\n")
        # Q3
        # file.write('Question 3 - 192.168.2.191 IP: ' + str(data_table_df.loc[data_table_df['ip_addr'] == '192.168.2.191','name'].values[0])+ "\n")  
