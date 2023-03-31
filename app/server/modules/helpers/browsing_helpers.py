import requests
import json
import urllib.parse
from datetime import date, timedelta, datetime
from flask import current_app


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