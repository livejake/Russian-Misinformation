from flask import Flask,json
import pymongo
from pymongo import MongoClient
mongo = MongoClient().twitter
collection = mongo.retweeter_tweets

app = Flask(__name__)

@app.route("/")
def hello():
    tweets = list(collection.find( { "entities.urls.expanded_url": { "$exists": "true"} }).limit(25000))
    for tweet in tweets:
      del tweet["_id"]

    response = app.response_class(
        response=json.dumps(tweets),
        status=200,
        mimetype='application/json'
    )
    return response

if __name__ == "__main__":
    app.run(debug=True)
