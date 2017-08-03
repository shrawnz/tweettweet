from __future__ import print_function # In python 2.7
from flask import Flask, render_template, session
from app import app
from flask.ext.mongoalchemy import MongoAlchemy
import tweepy
import sys

app.debug = True
app.config['SECRET_KEY']='23081997'
# oauth = OAuth(app)


TWITTER_CONSUMER_KEYS = ['bpdE7WkpiEtWRrdBZ7h5Nhr5o','yPE1NC4UeYVtFnVe4eM5A1Zh8','8f2cgkMuF1IC8enJY6klvL8rY','o6fAZVsI0SrEeV2Gqv9zqega0']
TWITTER_CONSUMER_SECRETS = ['tXW36I7IcI7sXt5QXlnwIkrT093ZADlimQKiMTSizHSEXsm7qx','G1J61zps7G8qGMOgLfDw7bs8zzVf20pUTHNIzvKaulLqIPReB4','phY1XIegXcZ8GUowOQXHsJCKq5IXRYhDxwbJG46OkPoFV3vMn6','UQEgnufnNfoI7deKbPXV6cfkuF3cKpLmtM3IfbaIi8yQKHlt1Z']
TWITTER_ACCESS_TOKENS = ['3692740694-XAsTjJeSoRk2uxi5TCold3hZg9mU6HRz7AvUQMP','3692740694-R2swShbzcCngvVzzFLFZcjMlCzudgl3xObkdItg','3692740694-YD96Qt6ZnVn4fzepf2cOpwTzMjENAncWXtVHrQN','3692740694-eC8pagFgyyORqHzmqyICljOEC7aQGjsxTMhupyL']
TWITTER_ACCESS_TOKEN_SECRETS = ['N0Mlkn1aDwK9fkzfMu3Iwih7IUuuiEJ9q6Q4yjfwc1yc5','cXlGhbiSX9TqBXw9J77iy9i9HUq5lgPY0tIzEFwg8idKe','DDSAtSokw1151CABI6eafs7BQ19QYZzdeQtwxivOKcEPt','Vfmwr2LUrMAVqZTyn4rNXUVQrMIVYg0oyMqrgijMCO59J']

INDEX = 0
auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEYS[INDEX], TWITTER_CONSUMER_SECRETS[INDEX])
auth.set_access_token(TWITTER_ACCESS_TOKENS[INDEX], TWITTER_ACCESS_TOKEN_SECRETS[INDEX])
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
	#TYPE of TWEETS
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
	type_data = [["Text",ptage_text],["Image",ptage_img],["Text+Img",ptage_both]]
	

	#HASHTAGS
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

	return render_template('main.html',type_data=type_data,tags_m=result_m[:10],tags_k=result_k[:10])

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

@app.route("/showRetweet")
def showRetweet():
	re_tweets = TweetModel.query.filter(TweetModel.retweeted==True).all()
	orig_tweets = TweetModel.query.filter(TweetModel.retweeted==False).all()
	cnt_re = len(re_tweets)
	cnt_orig = len(orig_tweets)
	ptage_re = cnt_re/(cnt_re+cnt_orig)
	ptage_orig = cnt_orig/(cnt_re+cnt_orig)
	data = [["Retweets",ptage_re],["Original Tweets",ptage_orig]]
	return render_template('retweet.html',data=data)

@app.route("/showFav")
def showFav():
	tweets = TweetModel.query.filter(TweetModel.location.regex(r'\bdelhi\b|\bncr\b',ignore_case=True)).all()
	cnt_modi = 0
	cnt_kejri = 0
	for tweet in tweets:
		if tweet.tweetFor==TYPE_MODI:
			cnt_modi+=1
		else:
			cnt_kejri+=1
	data = [["Modi",cnt_modi],["Kejriwal",cnt_kejri]]
	return render_template('popular.html',data=data)

@app.route("/favCount")
def favCount():
	hash_cnt = dict()
	tweets = TweetModel.query.filter(TweetModel.retweeted==False)
	fav_cnt = [t.favourite for t in tweets if t.favourite>0]
	result = sorted(fav_cnt)
	for i in result:
			hash_cnt[i] = hash_cnt.get(i, 0) + 1
	# print(hash_cnt,file=sys.stderr)
	data = [ [k,v] for k, v in hash_cnt.items() ]
	return render_template('fav.html',data=data)

@app.route("/showMap")
def showMap():
	hash_location = dict()
	tweets = TweetModel.query.all()
	location = [t.location.split(' ')[-1:] for t in tweets]
	for l in location:
			hash_location[l[0]] = hash_location.get(l[0], 0) + 1
	print(hash_location,file=sys.stderr)
	return render_template('location.html',locations=hash_location)

@app.route("/getData")
def getData():

	resp = 999999999999999999999999999999
	
	while True:
		try:
			resp = getTweetM(resp)
		except tweepy.error.RateLimitError:
			print ("ERROR",file=sys.stderr)
			global INDEX
			global tweepy_api
			INDEX=(INDEX+1)%4
			print (INDEX,file=sys.stderr)
			auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEYS[INDEX], TWITTER_CONSUMER_SECRETS[INDEX])
			auth.set_access_token(TWITTER_ACCESS_TOKENS[INDEX], TWITTER_ACCESS_TOKEN_SECRETS[INDEX])
			tweepy_api = tweepy.API(auth)
			pass


	return("Done")

def getTweetM(max_id):
	all_tweets = tweepy_api.search('modi OR bjp pm OR pm modi',count=100,max_id=max_id)
	tweets=[]
	min_id = None 
	same = 0
	for tweet in all_tweets:
		url_id = str(tweet.id)
		if TweetModel.query.filter(TweetModel.url_id==str(tweet.id)).all():
			same += 1
			continue
		username = tweet.user.name
		content = tweet.text
		fword = content.split(" ")[0]
		retweeted = False
		if fword=='RT':
			retweeted = True
		print (same, file=sys.stderr)
		hashtags = [h['text'] for h in tweet.entities['hashtags']]
		location = tweet.user.location
		favourite = tweet.favorite_count
		coordinates=None
		tweetFor = TYPE_MODI
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
		min_id = url_id
	# return(1)
	return min_id

def getTweetK(max_id):
	all_tweets = tweepy_api.search('aamaadmi OR aap OR kejriwal',count=100,max_id=max_id)
	tweets=[]
	min_id = None 
	same = 0
	for tweet in all_tweets:
		url_id = str(tweet.id)
		if TweetModel.query.filter(TweetModel.url_id==str(tweet.id)).all():
			same += 1
			continue
		username = tweet.user.name
		content = tweet.text
		fword = content.split(" ")[0]
		retweeted = False
		if fword=='RT':
			retweeted = True
		print (same, file=sys.stderr)
		hashtags = [h['text'] for h in tweet.entities['hashtags']]
		location = tweet.user.location
		favourite = tweet.favorite_count
		coordinates=None
		tweetFor = TYPE_KEJRI
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
		min_id = url_id
	# return(1)
	return min_id

if __name__ == "__main__":
	app.run()