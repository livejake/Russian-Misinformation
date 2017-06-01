import twitter
import pandas as pd
import itertools
from pymongo import MongoClient
import logging

mongo = MongoClient().twitter
mongo.posts.ensure_index([('id', 1)], unique=True)
logging.basicConfig(filename='example.log',level=logging.DEBUG)

tokens = [line.strip() for line in open('tokens.txt','r')]
TOKENS = itertools.cycle([x.split("|") for x in tokens])

def set_api(TOKENS):
  token = next(TOKENS)
  # print(token)
  api = twitter.Api(consumer_key=token[0],
    consumer_secret=token[1],
    access_token_key=token[2],
    access_token_secret=token[3])
  return api 

api =set_api(TOKENS)

data = {}
max_id = None
total = 0
while True:
  try:
      api =set_api(TOKENS)
      statuses = api.GetUserTimeline(screen_name='SputnikNewsUS', count=200, max_id=max_id)
  except:
      print "Gateway error... trying again"
      time.sleep(20)
      api =set_api(TOKENS)
      statuses = api.GetUserTimeline(screen_name='SputnikNewsUS',  count=200, max_id=max_id)
      continue
  time.sleep(5)
  newCount = ignCount = 0
  for s in statuses:
      if s.id in data:
          ignCount += 1
      else:
          data[s.id] = s
          newCount += 1
  total += newCount
  userTweetData = data.values()
  # if total<=200:
  #     break
  print >> sys.stderr, "Fetched %d/%d/%d new/old/total." % (newCount, ignCount, total)
  if newCount == 0:
    break
  max_id = min([s.id for s in statuses]) - 1

# api = set_api(TOKENS)
# statuses = api.GetUserTimeline(screen_name='SputnikNewsUS',count=200)

status_ids = data.keys()
collection = mongo.posts
for tweet_id in status_ids:
  api = set_api(TOKENS)
  try:
    for retweet in api.GetRetweets(statusid=tweet_id,count=100):
        if collection.find({'id': retweet.id}, {'_id': 1}).limit(1).count():
          print("STOPPPED DUP")
          logging.info('in db post_id = {}'.format(_id))
          continue # print(retweet)
        collection.insert(retweet.AsDict(),check_keys=False)
  except:
    # time.sleep(3600)
    api = set_api(TOKENS)
    for retweet in api.GetRetweets(statusid=tweet_id,count=100):
      if collection.find({'id': retweet.id}, {'_id': 1}).limit(1).count():
        print("STOPPPED DUP")
        logging.info('in db post_id = {}'.format(_id))
        continue # print(retweet)
      collection.insert(retweet.AsDict(),check_keys=False)

user_info =[]
for retweet in retweets:
  if hasattr(retweet, 'user'):
    user_info.append([retweet.user.screen_name]) 
    print(retweet.user.screen_name)



data=pd.DataFrame.from_records(user_info)


### GET TOP TWITTER NAMES 


pipeline = [
        {
            "$group": {
                "_id": "$user.screen_name",
                "count": {
                    "$sum": 1
                }

            }
        },
        {
            "$sort": {
                "count": -1
            }
        },
        {
            "$limit": 25
        }

    ]

top_twitter_usernames =[] 
for result in collection.aggregate(pipeline):
  top_twitter_usernames.append(result['_id'])

latest_tweets = mongo.latest_tweets
for name in top_twitter_usernames:
  api = set_api(TOKENS)
  for tweet in api.GetUserTimeline(screen_name=name, count=10):
    latest_tweets.insert(tweet.AsDict())

from http import client
import urllib
def unshorten_url(url):
    parsed = urllib.parse.urlparse(url)
    h = client.HTTPConnection(parsed.netloc)
    resource = parsed.path
    if parsed.query != "":
        resource += "?" + parsed.query
    h.request('HEAD', resource )
    response = h.getresponse()
    if response.status//100 == 3 and response.getheader('Location'):
        return response.getheader('Location')# changed to process chains of short urls
    else:
        return url





def expand_url_update(current_url, expanded_url):
  for tweet in latest_tweets.find():
  if len(tweet['urls'])>0:
    for i,url in enumerate(tweet['urls']):
      tweet['urls'][i][expanded_url] = unshorten_url(url[current_url])
      latest_tweets.update_one({'_id':tweet['_id']}, {"$set": tweet}, upsert=False
        
expand_url_update("expanded_url", "fully_expanded_url")
expand_url_update("fully_expanded_url", "fully_expanded_url2")




