import json
import requests
import api_info
import sqlite3
import re

#Name: Amanda Gomez
#API: News


#Caching
CACHE_FNAME = "dump.json" #creating json file
try:
    cache_file = open(CACHE_FNAME,'r')
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)
except: #if file is created, dont do anything
    CACHE_DICTION = {}

#caching links- News
def getWithCaching(baseURL, params={}):
    #using requests to fill in full url with access token and baseurl
  req = requests.Request(method = 'GET', url =baseURL, params = sorted(params.items()))
  prepped = req.prepare()
  fullURL = prepped.url#prepares url from params and base url
  #check to see if url is in cache
  if fullURL not in CACHE_DICTION:#adds url to dictionary
      response = requests.Session().send(prepped) #send prepped url to dictionary
      CACHE_DICTION[fullURL] = response.text#adds url to dictionary
      cache_file = open(CACHE_FNAME, 'w')
      cache_file.write(json.dumps(CACHE_DICTION))#puts url info into cache
      cache_file.close()
  return CACHE_DICTION[fullURL]

#News API
def get_headline(word):
    if word in CACHE_DICTION:#if word already in CACHE_DICTION, don't add it, print 'cached'
        print('cached')
        ndata=CACHE_DICTION[word]
    else:
        print('making new request')
        newskey= api_info.key #takes news key from api_info
        nresponse= getWithCaching('https://newsapi.org/v2/everything?q={}&from2017-12-10&sortBy=popularity&apiKey={}'.format(word,newskey))#add params to base url
        ndata=json.loads(nresponse)
        CACHE_DICTION[word]=ndata#adds data from selected url to CACHE_DICTION
        jsd2= json.dumps(CACHE_DICTION)#places data into CACHE_DICTION
        cache_file= open(CACHE_FNAME, 'w')#opens cached file
        cache_file.write(jsd2)#writes data to CACHE_FNAME
        cache_file.close()#closes file
    return ndata
n=get_headline('dog')#grabs data for all headlines containing 'dog'
#Creation of Articles table in SQL
conn= sqlite3.connect('News_db.sqlite')
cur= conn.cursor()

cur.execute('DROP TABLE IF EXISTS Articles')#if Articles table exists, don't add another table
cur.execute('CREATE TABLE Articles (title TEXT, author TEXT, description TEXT, url TEXT, time_published TEXT)')
#create Articles table with title, author, description, url, time_published columns

for s in n:
    stuff='INSERT OR IGNORE INTO Articles (title, author, description, url, time_published) VALUES (?,?,?,?,?)'#inserts values into columns
    for y in range(10):#takes first 20 articles in data and returns given values
        tup= n['articles'][y]['title'],n['articles'][y]['author'],n['articles'][y]['description'],n['articles'][y]['url'],n['articles'][y]['publishedAt']
        #finds titles, authors, descriptions, urls, and date published
        cur.execute(stuff,tup)#Adds data to table Articles

conn.commit()#publishes data to SQL table

