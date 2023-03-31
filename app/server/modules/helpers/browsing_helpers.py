import requests
import json
import urllib.parse
from datetime import date, timedelta, datetime
from flask import current_app
from faker import Faker
import random



def wiki_get_random_articles():
    url = 'https://en.wikipedia.org/w/api.php?action=query&list=random&rnnamespace=0&rnlimit=200&format=json'
    response = requests.get(url)
    response_json = json.loads(response.text)
    articles = []
    for article in response_json["query"]["random"]:
        articles.append(f"https://en.wikipedia.org/wiki/" + urllib.parse.quote(article["title"]))
    return articles

def news_get_top_headlines(apikey):
    today  = date.today()
    one_month_ago = today - timedelta(days=20)
    api_key = apikey
    headers = {'Authorization':api_key}
    request_url = f'https://newsapi.org/v2/top-headlines?country=us&from={one_month_ago}&to={today}'
    response = requests.get(request_url, headers=headers)
    response_json = response.json()
    top_headlines = []
    for article in response_json["articles"]:
        top_headlines.append(article['url'])
    return top_headlines

def reddit_get_subreddit(sub):
    subreddit = sub
    headers = {'User-agent':'KC7 Randomized'}
    url = f'https://www.reddit.com/r/{subreddit}/.json?limit=1000'
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    posts = []
    for post in data['data']['children']:
        posts.append(post['data']['url'])
    return posts

def youtube_get_random_videos(apikey):
    maxResults = 100
    #if you want to add your own search terms, put something in the "q" param ex. "q=cats"
    api_key = apikey
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&hl=en&maxResults={str(maxResults)}&type=video&key={api_key}'
    response = requests.get(url)
    data = json.loads(response.text)
    videos = []
    for video in data['items']:
        title = video['snippet']['title']
        video_id = video['id']['videoId']
        link = f'https://www.youtube.com/watch?v={video_id}'
        videos.append(link)
    return videos

def news_search_everything(searchterm, apikey):
    search = searchterm
    today  = date.today()
    one_month_ago = today - timedelta(days=20)
    api_key = apikey
    headers = {'Authorization':api_key}
    request_url = f'https://newsapi.org/v2/everything?q={search}&from={one_month_ago}&to={today}'
    response = requests.get(request_url, headers=headers)
    response_json = response.json()
    everything = []
    for article in response_json["articles"]:
        everything.append(article['url'])
    return everything

def generate_company_domains(company_domain):
    # to use with legit_domains
    domain = company_domain
    domainList = []
    url = domain[:domain.find('.')]
    #generate sharepoint links
    fake = Faker()
    for i in range(0,250):
        faker_dt = datetime.now()
        seed_value = int(round(faker_dt.timestamp()))
        Faker.seed(seed_value+random.randint(0,999999))
        random.seed(seed_value+random.randint(0,999999))
        uuid = fake.uuid4()
        passwd = fake.password(length=20,special_chars=False)
        both = fake.bothify(text='????-#########')
        line1 = [uuid, passwd, both]
        isbn10 = fake.isbn10()
        isbn13 = fake.isbn13()
        nums = fake.numerify(text='!!!!!!!!!!!!!!!!!!')
        line2 = [isbn10, isbn13, nums]
        tempurl = "https://" + url + "sharepoint.com/" + random.choice(line1) + "/?items=" + random.choice(line2) + "/" + random.choice(line1)
        domainList.append(tempurl)

    #generate "report"" links
    for i in range(0,250):
        faker_dt = datetime.now()
        seed_value = int(round(faker_dt.timestamp()))
        Faker.seed(seed_value+random.randint(0,999999))
        random.seed(seed_value+random.randint(0,999999))
        nums = fake.numerify(text='!!!!!!!!!!!!!!!!!!')
        tempurl = "https://reports." + domain + "/id/?auth=True&requestid=" + nums
        domainList.append(tempurl)

    #generate Slack links
    for i in range(0,500):
        faker_dt = datetime.now()
        seed_value = int(round(faker_dt.timestamp()))
        Faker.seed(seed_value+random.randint(0,999999))
        random.seed(seed_value+random.randint(0,999999))
        passwd = fake.password(length=11,lower_case=False,upper_case=True,special_chars=False)
        passwd2 = fake.password(length=11,lower_case=False,upper_case=True,special_chars=False)
        tempurl = "https/:/app.slack.com/client/" + passwd + "/" + passwd2
        domainList.append(tempurl)

    #generate Google Spreadsheets/Word/Drive
    for i in range(0,1000):
        faker_dt = datetime.now()
        seed_value = int(round(faker_dt.timestamp()))
        Faker.seed(seed_value+random.randint(0,999999))
        random.seed(seed_value+random.randint(0,999999))
        googleurls = ["docs.google.com/spreadsheets/d/", "drive.google.com/drive/u/1/folders/", "https://docs.google.com/document/d/", "https://docs.google.com/presentation/d/"]
        passwd = fake.password(length=25,special_chars=False)
        tempurl = "https://" + random.choice(googleurls) + passwd
        domainList.append(tempurl)

    #generate image links
    for i in range(0,500):
        faker_dt = datetime.now()
        seed_value = int(round(faker_dt.timestamp()))
        Faker.seed(seed_value+random.randint(0,999999))
        random.seed(seed_value+random.randint(0,999999))
        uuid = fake.uuid4()
        passwd = fake.password(length=20,special_chars=False)
        both = fake.bothify(text='????-#########')
        line1 = [uuid, passwd, both]
        isbn10 = fake.isbn10()
        isbn13 = fake.isbn13()
        nums = fake.numerify(text='!!!!!!!!!!!!!!!!!!')
        line2 = [isbn10, isbn13, nums]
        tempurl = "images." + "." + domain + "/static/" + random.choice(line1) + "/" + random.choice(line2) + "."+ fake.file_extension(category='image')
        domainList.append(tempurl)

    return domainList

def generate_partner_domains(partner_domains):
    # to use with partner domains (add to legit_domains)
    # only gets "sharepoint" stuff for now
    domains = partner_domains
    domainList = []
    for partner in domains:
        url = partner[:partner.find('.')]
        #generate sharepoint links
        fake = Faker()
        for i in range(0,100):
            faker_dt = datetime.now()
            seed_value = int(round(faker_dt.timestamp()))
            Faker.seed(seed_value+random.randint(0,999999))
            random.seed(seed_value+random.randint(0,999999))
            uuid = fake.uuid4()
            passwd = fake.password(length=20,special_chars=False)
            both = fake.bothify(text='????-#########')
            line1 = [uuid, passwd, both]
            isbn10 = fake.isbn10()
            isbn13 = fake.isbn13()
            nums = fake.numerify(text='!!!!!!!!!!!!!!!!!!')
            line2 = [isbn10, isbn13, nums]
            tempurl = "https://" + url + "sharepoint.com/" + random.choice(line1) + "/?items=" + random.choice(line2) + "/" + random.choice(line1)
            domainList.append(tempurl)
    return domainList





def generate_company_traffic(company_domain):
    # to use with randomized_domains
    domain = company_domain
    domainList = []
    url = domain[:domain.find('.')]
    fake = Faker()

    #generate "workspace"" links
    for i in range(0,500):
        faker_dt = datetime.now()
        seed_value = int(round(faker_dt.timestamp()))
        Faker.seed(seed_value+random.randint(0,999999))
        random.seed(seed_value+random.randint(0,999999))
        uuid = fake.uuid4()
        isbn10 = fake.isbn10()
        tempurl = "https://www." + domain + "/workspace/?auth=True&sessionid=" + uuid + "/" + isbn10 + "/"
        domainList.append(tempurl)   

    #generate dashboard links
    for i in range(0,250):
        faker_dt = datetime.now()
        seed_value = int(round(faker_dt.timestamp()))
        Faker.seed(seed_value+random.randint(0,999999))
        random.seed(seed_value+random.randint(0,999999))
        uuid = fake.uuid4()
        passwd = fake.password(length=20,special_chars=False)
        tempurl = "https://prod." + domain + "/dashboard/?auth=True&" + uuid + "/" + passwd + "/"
        domainList.append(tempurl)   

    #generate "pulse" links:
    for i in range(0,500):
        faker_dt = datetime.now()
        seed_value = int(round(faker_dt.timestamp()))
        Faker.seed(seed_value+random.randint(0,999999))
        random.seed(seed_value+random.randint(0,999999))
        uuid = fake.uuid4()
        passwd = fake.password(length=20,special_chars=False)
        both = fake.bothify(text='????-#########')
        line1 = [uuid, passwd, both]
        isbn10 = fake.isbn10()
        isbn13 = fake.isbn13()
        nums = fake.numerify(text='!!!!!!!!!!!!!!!!!!')
        line2 = [isbn10, isbn13, nums]
        tempurl = "https://security-cloudapps." + domain + "/pulse/?id=" + both + "&request=" + nums + "/" + uuid + "&" + random.choice(line1) + "/" + random.choice(line2)
        domainList.append(tempurl)

    #generate image links
    for i in range(0,250):
        faker_dt = datetime.now()
        seed_value = int(round(faker_dt.timestamp()))
        Faker.seed(seed_value+random.randint(0,999999))
        random.seed(seed_value+random.randint(0,999999))
        uuid = fake.uuid4()
        passwd = fake.password(length=20,special_chars=False)
        both = fake.bothify(text='????-#########')
        line1 = [uuid, passwd, both]
        isbn10 = fake.isbn10()
        isbn13 = fake.isbn13()
        nums = fake.numerify(text='!!!!!!!!!!!!!!!!!!')
        line2 = [isbn10, isbn13, nums]
        tempurl = "images." + "." + domain + "/static/" + random.choice(line1) + "/" + random.choice(line2) + "."+ fake.file_extension(category='image')
        domainList.append(tempurl)

    #generate asset links
    for i in range(0,500):
        faker_dt = datetime.now()
        seed_value = int(round(faker_dt.timestamp()))
        Faker.seed(seed_value+random.randint(0,999999))
        random.seed(seed_value+random.randint(0,999999))
        uuid = fake.uuid4()
        passwd = fake.password(length=20,special_chars=False)
        both = fake.bothify(text='????-#########')
        line1 = [uuid, passwd, both]
        isbn10 = fake.isbn10()
        isbn13 = fake.isbn13()
        nums = fake.numerify(text='!!!!!!!!!!!!!!!!!!')
        line2 = [isbn10, isbn13, nums]
        tempurl = "assets." + "." + domain + "/static/" + random.choice(line1) + "/" + random.choice(line2) + "."+ fake.file_extension(category='text')
        domainList.append(tempurl)

    return domainList
