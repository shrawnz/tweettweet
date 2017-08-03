# tweettweet
Twitter analysis done as a part of PreCog assignment.

https://tweettweet4pc.herokuapp.com/

Approach:
1. Used Tweepy to connect to the Twitter API.
2. Through the twitter api searched for tweets relevant to Modi and Kejriwal by using keywords such as "modi,bjp pm,pm modi" and "aap, aam aadmi party, kejriwal" for Modi and Kejriwal respectively.
3. Saved all the statuses received to mongodb using MongoAlchemy.
4. Filtered out relevant data by querying the dataset.
5. Used highcharts with jquery to show graphs and visualisations.


