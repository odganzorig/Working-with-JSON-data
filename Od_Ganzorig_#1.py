#Name: Od Ganzorig
#Class: CS328
#Lab Assignment 1 

#!/usr/bin/python3

# Accessing the Twitter API
# This script describes the basic methodology for accessing a Twitter feed
# or something similar.

# Loading libraries needed for authentication and requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import json

# In order to use this script, you must:
# - Have a Twitter account and create an app
# - Store in keys.json a property called "twitter" whose value is an
#     object with two keys, "key" and "secret"
with open('keys.json', 'r') as f:
   keys = json.loads(f.read())['twitter']

twitter_key = keys['key']
twitter_secret = keys['secret']

# We authenticate ourselves with the above credentials
# We will demystify this process later
#
# For documentation, see http://requests-oauthlib.readthedocs.io/en/latest/api.html
# and http://docs.python-requests.org/en/master/
client = BackendApplicationClient(client_id=twitter_key)
oauth = OAuth2Session(client=client)
token = oauth.fetch_token(token_url='https://api.twitter.com/oauth2/token',
                          client_id=twitter_key,
                          client_secret=twitter_secret)

# Base url needed for all subsequent queries
base_url = 'https://api.twitter.com/1.1/'

# Particular page requested. The specific query string will be
# appended to that.
page = 'search/tweets.json'

# Depending on the query we are interested in, we append the necessary string
# As you read through the twitter API, you'll find more possibilities
req_url = base_url + page + '?q=Hanover+College&tweet_mode=extended&count=100'

# We perform a request. Contains standard HTTP information
response = oauth.get(req_url)

# Read the query results
results = json.loads(response.content.decode('utf-8'))

## Process the results
## CAUTION: The following code will attempt to read up to 10000 tweets that
## Mention Hanover College. You should NOT change this code.



tweets = results['statuses']
while True:
   if not ('next_results' in results['search_metadata']):
      break
   if len(tweets) > 10000:
      break
   next_search = base_url + page + results['search_metadata']['next_results'] + '&tweet_mode=extended'
   print(results['search_metadata']['next_results'])
   response = oauth.get(next_search)
   results = json.loads(response.content.decode('utf-8'))
   tweets.extend(results['statuses'])

## CAUTION: For the rest of this assignment, the list "tweets" contains all the
## tweets you would want to work with. Do NOT change the list or the value of "tweets".

#1
texts = [tweet['full_text'] for tweet in tweets]

#2
def get_full_text(tweet):
	if 'retweeted_status' in tweet.keys():
		return tweet['retweeted_status']['full_text']
	return tweet['full_text']

tweets_text = [get_full_text(text) for text in tweets]

#3
def get_hashtags(tweet):
	hashtag_list = []
	for i in range(len(tweet['entities']['hashtags'])):
		hashtag_list.append(tweet['entities']['hashtags'][i]['text'])
	return hashtag_list

tags_per_tweet = [get_hashtags(tweet) for tweet in tweets]
#print(tags_per_tweet)

#4 
hashtags = {}
for tweet in tags_per_tweet:
	for tag in tweet:
		if tag in hashtags:
			hashtags[tag]+=1
		else:
			hashtags[tag]=1
	
#print(hashtags)


#5
sorted_list = sorted(hashtags.items(), key=lambda x: x[1], reverse=True)
for x in sorted_list[0:6]:
	print(x[0])
	
#6
tagless_tweets = [tweet for tweet in tweets if tweet['entities']['hashtags'] == []]
#print(tagless_tweets)

#7
tag_info = {}
for tag in hashtags:
	tag_dict = {}
	tag_dict["count"] = hashtags[tag]
	tag_dict["percent"] = tag_dict["count"]/len(tweets)
	tag_dict["users"] = []
	for tweet in tweets:
		if tag in get_hashtags(tweet):
			if tweet['user']['screen_name'] not in tag_dict["users"]:
				tag_dict["users"].append(tweet['user']['screen_name'])
	tag_dict["other_tags"] = []
	for tweet in tweets:
		if tag in get_hashtags(tweet):
			for tags in get_hashtags(tweet):
				if tags != tag:
					tag_dict["other_tags"].append(tags)
	tag_info[tag] = tag_dict
#print(tag_info)

#8
with open('tag_info.json','w') as file:
	json.dump(tag_info, file)

#9
dict_per_tweet = [{"text": get_full_text(tweet), 
	"author": tweet['user']['screen_name'], 
	"date": tweet['created_at'], 
	"hashtags": [tweet['entities']['hashtags'][i]['text'] for i in range(len(tweet['entities']['hashtags']))],
	"mentions": [tweet['entities']['user_mentions'][i]['name'] for i in range(len(tweet['entities']['user_mentions']))] } for tweet in tweets]
#print(dict_per_tweet)

with open('simpler_tweets.json','w') as file:
	json.dump(dict_per_tweet, file)
