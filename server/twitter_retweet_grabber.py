import tweepy
import pandas as pd
import itertools
import pymongo
import logging
from http import client
import urllib
from urllib.request import urlopen
import requests



def set_api():
    """
    Sets Up Authenticated API Session With Next 
    set of Tokens  
    TODO: Figure out if rather than sending tokens and authenticated each time. 
    Authenticate all, then send next better. 
    """
    token = next(TOKENS)
    auth = tweepy.OAuthHandler(token[0], token[1])
    auth.set_access_token(token[2], token[3])
    api = tweepy.API(auth,wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)
    return api 


def get_all_tweets(username,collection):
    """
    Gets last 3200 Tweets (max allowed) from a username 
    """
    api = set_api()
    for tweet in tweepy.Cursor(api.user_timeline,screen_name=username).items():
        # process status here
        insert_tweet(tweet,collection)


def insert_tweet(tweet, collection):
    """
    Checks if Tweet with same id in collection.
    Inserts tweet into Mongo collection
    """
    if collection.find({"id":tweet.id}).count()>0:
       print("already saved")
    else:
       post_id = collection.insert(tweet._json)
       print("Inserted ",post_id)


def process_retweets(tweet_id):
  """
  Gets users who retweet at tweet and insert into 
  Mongo 
  """
  api = set_api()
  for tweet in api.retweets(id=tweet_id):
    insert_tweet(tweet, retweets_collection)

def get_retweets_from_timeline():
  """
  Gets tweets with retweets from mongo 
  and processes each tweet 
  """
  ## TODO invesigate cursor timeout 
  for tweet in user_timeline_collection.find({"retweet_count":{"$gte":1}},no_cursor_timeout=True):
    process_retweets(tweet['id'])


def get_top_n_retweeters(n,collection):
    """ 
    Gets the top N retweeters from Mongo 
    """

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
                 "$limit": n
             }
     
         ]
    return [result['_id'] for result in collection.aggregate(pipeline)]


# https://stackoverflow.com/questions/21509045/mongodb-group-by-array-inner-elements
# pipeline = [
#   {"$match": { "user.screen_name": { $in: [usernames] } } },
#   {"$project": { "_id": 0, "entities.urls": 1 } },
#   {"$unwind": "$entities.urls" },

#     { 
#         "$group": {
#             "_id": "$entities.urls.expanded_url",
#             "count": {
#                 "$sum": 1
#             }
#         }

#     },
#     {
#         "$sort": {
#             "count": -1
#         }
#     },
#     {
#         "$limit": 100
#     }
 
#      ]


# [result for result in retweeter_tweets.aggregate(pipeline)]

def get_all_tweets_from_retweeters(n,collection):
    """
    For each user for the top N retweets, get their full timeline 
    """
    for username in get_top_n_retweeters(n,collection):
        get_all_tweets(username,retweeter_tweets)


def unshorten_url(url):
  # TODO check key value store: Redis 
  # https://www.npmjs.com/package/url-unshort
  # integration with APIs 
  # TODO check for bitly url
  # https://dev.bitly.com/domains.html
  # https://dev.bitly.com/links.html#v3_expand
  # # http://dev.bitly.com/best_practices.html
  #   parsed = urllib.parse.urlparse(url)
  #   h = client.HTTPConnection(parsed.netloc)
  #   resource = parsed.path
  #   if parsed.query != "":
  #       resource += "?" + parsed.query
  #   h.request('HEAD', resource )
  #   response = h.getresponse()
  #   if response.status//100 == 3 and response.getheader('Location'):
  #       return response.getheader('Location')# changed to process chains of short urls
  #   else:
  #       return url
  try:
    session = requests.Session()  # so connections are recycled
    resp = session.head(url, allow_redirects=True)
    return resp.url
  except:
      return url


def expand_url_update(current_url, expanded_url):
    for tweet in retweeter_tweets.find({},no_cursor_timeout=True):
        if len(tweet['entities']['urls'])>0:
            for i,url in enumerate(tweet['entities']['urls']):
                print(i,url)
                tweet['entities']['urls'][i][expanded_url] = unshorten_url(url[current_url])
                print(tweet)
                retweeter_tweets.update_one({'_id':tweet['_id']}, {"$set": tweet}, upsert=False)

def double_expand_urls():
  expand_url_update("expanded_url", "fully_expanded_url")
  # expand_url_update("fully_expanded_url", "fully_expanded_url2")


if __name__ == "__main__":
    client = pymongo.MongoClient('localhost', 27017)
    db = client.twitter
    user_timeline_collection = db.user_timeline
    retweets_collection = db.retweets
    retweeter_tweets = db.retweeter_tweets
    user_timeline_collection.ensure_index([('id', 1)], unique=True)
    retweets_collection.ensure_index([('id', 1)], unique=True)
    retweeter_tweets.ensure_index([('id', 1)], unique=True)

    logging.basicConfig(filename='example.log',level=logging.DEBUG)
    tokens = [line.strip() for line in open('tokens.txt','r')]
    TOKENS = itertools.cycle([x.split("|") for x in tokens])

    # MAIN LOGIC 
    # Get last 3200 tweets from Russian propaganda outlets 
    # usernames = ['SputnikNewsUS']
    # for username in usernames:
    #   print("getting {} tweets".format(username))
    #   get_all_tweets(username, user_timeline_collection)
    # # For each tweet, get all the retweets
    # print("getting retweets")
    # get_retweets_from_timeline()
    # # For the top reweeters, get all their tweets
    # print("getting tweets from retweeters")
    # get_all_tweets_from_retweeters(1000,retweets_collection)
    
    #For all the top retweeter_tweets, double expand (unshorten twice)
    #each url 
    print("expanding urls")
    double_expand_urls()






