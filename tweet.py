from __future__ import print_function # In python 2.7
from flask import Flask, render_template, session
from app import app
from flask.ext.mongoalchemy import MongoAlchemy
import tweepy
import sys

app.debug = True
app.config['SECRET_KEY']='23081997'
# oauth = OAuth(app)

TWITTER_CONSUMER_KEY = 'bpdE7WkpiEtWRrdBZ7h5Nhr5o'
TWITTER_CONSUMER_SECRET = 'tXW36I7IcI7sXt5QXlnwIkrT093ZADlimQKiMTSizHSEXsm7qx'
TWITTER_ACCESS_TOKEN = '3692740694-XAsTjJeSoRk2uxi5TCold3hZg9mU6HRz7AvUQMP'
TWITTER_ACCESS_TOKEN_SECRET = 'N0Mlkn1aDwK9fkzfMu3Iwih7IUuuiEJ9q6Q4yjfwc1yc5'

auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
tweepy_api = tweepy.API(auth)

app.config['MONGOALCHEMY_DATABASE'] = 'tweet'
db = MongoAlchemy(app)

# twitter = oauth.remote_app('twitter',
#     base_url='https://api.twitter.com/1/',
#     request_token_url='https://api.twitter.com/oauth/request_token',
#     access_token_url='https://api.twitter.com/oauth/access_token',
#     authorize_url='https://api.twitter.com/oauth/authenticate',
#     consumer_key='bpdE7WkpiEtWRrdBZ7h5Nhr5o',
#     consumer_secret='tXW36I7IcI7sXt5QXlnwIkrT093ZADlimQKiMTSizHSEXsm7qx'
# )

#MODELS

TWEETTYPE_TEXT = 1
TWEETTYPE_IMAGE = 2
TWEETTYPE_TEXTIMG = 3

TYPE_KEJRI = 0
TYPE_MODI = 1
class TweetModel(db.Document):
	user = db.StringField()
	content = db.StringField()
	hashtags = db.ListField(db.StringField(),allow_none=True)
	retweeted = db.BoolField()
	location = db.StringField()
	favourite = db.IntField()
	coordinates = db.TupleField(db.FloatField(),db.FloatField(),allow_none=True)
	tweetType = db.EnumField(db.IntField(),1,2,3)	#	1-Text | 2-Image | 3-Text+Image
	tweetFor = db.IntField()
	url_id = db.StringField()


@app.route("/")
def index():
	all_tweets = tweepy_api.user_timeline('shrawnz23')
	return("Hello!")

@app.route("/showType")
def showType():
	texts = TweetModel.query.filter(TweetModel.tweetType==TWEETTYPE_TEXT).all()
	both = TweetModel.query.filter(TweetModel.tweetType==TWEETTYPE_TEXTIMG).all()
	img = TweetModel.query.filter(TweetModel.tweetType==TWEETTYPE_IMAGE).all()

	cnt_text = len(texts)
	cnt_both = len(both)
	cnt_img = len(img)

	total = cnt_text + cnt_both + cnt_img
	ptage_text = (cnt_text/total)*100
	ptage_img = (cnt_img/total)*100
	ptage_both = (cnt_both/total)*100

	data = [["Text",ptage_text],["Image",ptage_img],["Text+Img",ptage_both]]

	return render_template('display.html',data=data)	

@app.route("/showHashtag")
def showHashtag():
	tweets = TweetModel.query.filter(TweetModel.tweetFor==TYPE_MODI).all()
	hash_dict = dict()
	for tweet in tweets:
		tags = tweet.hashtags
		for t in tags:
			hash_dict[t] = hash_dict.get(t, 0) + 1
	result_m = sorted(hash_dict.items(), key=lambda x: x[1],reverse=True)

	tweets = TweetModel.query.filter(TweetModel.tweetFor==TYPE_KEJRI).all()
	hash_dict = dict()
	for tweet in tweets:
		tags = tweet.hashtags
		for t in tags:
			hash_dict[t] = hash_dict.get(t, 0) + 1
	result_k = sorted(hash_dict.items(), key=lambda x: x[1],reverse=True)
	# print (result,file=sys.stderr)
	return render_template('hashtag.html',tags_m=result_m[:10],tags_k=result_k[:10])

@app.route("/showFav")
def showFav():
	original_tweets = TweetModel.query.filter(TweetModel.retweeted==False).all()
	# for tweet in original:
	return("ok")	

@app.route("/getData")
def getData():
	limit = tweepy_api.rate_limit_status()
	cnt = limit['resources']['search']['/search/tweets']['limit']
	while(cnt):
		resp = getTweetM()

	return("Done")

@app.route("/getModiData")
def getTweetM():
	all_tweets = tweepy_api.search('modi OR bjp pm OR pm modi')
	tweets=[]
	for tweet in all_tweets:
		username = tweet.user.name
		content = tweet.text
		fword = content.split(" ")[0]
		retweeted = False
		if fword=='RT':
			retweeted = True
		print (retweeted, file=sys.stderr)
		hashtags = [h['text'] for h in tweet.entities['hashtags']]
		location = tweet.user.location
		favourite = tweet.favorite_count
		coordinates=tweet.coordinates
		tweetFor = TYPE_MODI
		url_id = str(tweet.id)
		tweetType = TWEETTYPE_TEXT
		if('media' in tweet.entities):
			if content:
				tweetType = TWEETTYPE_TEXTIMG
			else:
				tweetType = TWEETTYPE_IMAGE

		model = TweetModel(user=username,content=content,retweeted=retweeted,hashtags=hashtags,location=location,favourite=favourite,\
				coordinates=coordinates,tweetType=tweetType ,tweetFor=tweetFor,url_id=url_id)
		model.save()
		tweets.append([tweet.id,username,content,hashtags,retweeted,location,favourite,coordinates,tweetType])

	# return(1)
	return render_template('index.html', tweets = tweets)

@app.route("/getKejriData")
def getTweetK():
	all_tweets = tweepy_api.search('kejriwal OR aam aadmi party OR aap delhi')
	tweets=[]
	# print (all_tweets[0], file=sys.stderr)
	for tweet in all_tweets:
		username = tweet.user.name
		content = tweet.text
		fword = content.split(" ")[0]
		retweeted = False
		if fword=='RT':
			retweeted = True
		hashtags = [h['text'] for h in tweet.entities['hashtags']]
		location = tweet.user.location
		favourite = tweet.favorite_count
		coordinates=tweet.coordinates
		tweetFor = TYPE_KEJRI
		url_id = str(tweet.id)
		tweetType = TWEETTYPE_TEXT
		if('media' in tweet.entities):
			if content:
				tweetType = TWEETTYPE_TEXTIMG
			else:
				tweetType = TWEETTYPE_IMAGE

		model = TweetModel(user=username,content=content,retweeted=retweeted,hashtags=hashtags,location=location,favourite=favourite,\
				coordinates=coordinates,tweetType=tweetType ,tweetFor=tweetFor,url_id=url_id)
		model.save()
		tweets.append([tweet.id,username,content,hashtags,retweeted,location,favourite,coordinates,tweetType])

	return render_template('index.html', tweets = tweets)

if __name__ == "__main__":
	app.run()