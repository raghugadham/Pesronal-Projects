import re
import sys
import webbrowser
import tweepy
import HTMLParser
import pymysql as mdb
import plotly.plotly as py
from nltk.corpus import stopwords
from numpy import unicode
from textblob import TextBlob
py.plotly.tools.set_credentials_file(username='raghugadam', api_key='XXXXXrEPLACE WITH YOUR KEY')
#reload(sys)
sys.setdefaultencoding('utf-8')

url = "http://localhost/mine/mine.php#"
html_parser = HTMLParser.HTMLParser()
def fig5(hp, lp, hn, ln, n):
    fig5 = {
        'data': [
            {
                'labels': ['High Positive', 'Low Positive', 'High Negative', 'Low Negative', 'Neutral'],
                'values': [hp,lp,hn,ln,n],
                'type': 'pie',
            }],
        'layout': {'title': 'Sentiment Analysis values'}
    }
    py.plot(fig5)
def fig3(p, ne, n):
    fig3 = {
        'data': [
            {
                'labels': ['Positive', 'Negative', 'Neutral'],
                'values': [p,ne,n],
                'type': 'pie',
            }],
        'layout': {'title': 'Sentiment Analysis values'}
    }
    py.plot(fig3)

con = mdb.connect('localhost', 'root', '', 'sentiment');
cur = con.cursor()
cur.execute("SELECT VERSION()")
ver = cur.fetchone()
print("Database version : %s " % ver)
cur = con.cursor()
cur.execute("DROP TABLE IF EXISTS sentiment")
cur.execute("CREATE TABLE sentiment( Name VARCHAR(250), Tweet VARCHAR(2000), polarity VARCHAR(20), type VARCHAR(1))")

# Replace the API_KEY and API_SECRET with your application's key and secret.
consumer_key = 'XXXXXrEPLACE WITH YOUR KEY'
consumer_secret = 'XXXXXrEPLACE WITH YOUR KEY'
access_token = 'XXXXXrEPLACE WITH YOUR KEY'
access_token_secret = 'XXXXXrEPLACE WITH YOUR KEY'
auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth, wait_on_rate_limit=True,
                   wait_on_rate_limit_notify=True)
if (not api):
    print ("Can't Authenticate")

searchQuery = '#trump'  # this is what we're searching for
maxTweets = 10000  # Some arbitrary large number
tweetsPerQry = 100  # this is the max the API permits
# If results from a specific ID onwards are reqd, set since_id to that ID.
# else default to no lower limit, go as far back as API allows
sinceId = None

# If results only below a specific ID are, set max_id to that ID.
# else default to no upper limit, start from the most recent tweet matching the search query.
max_id = -100000
tweets = []
tweetCount = 0
ptweets =[]
ntweets = []
ntlweets =[]
ptlweets = []
neutweets = []
print("Downloading max {0} tweets".format(maxTweets))
#with open(fName, 'w') as f:
while tweetCount < maxTweets:
            try:
                if (max_id <= 0):
                    if (not sinceId):
                        new_tweets = api.search(q=searchQuery, count=tweetsPerQry)
                    else:
                        new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                                since_id=sinceId, lang='en')
                else:
                    if (not sinceId):
                        new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                                max_id=str(max_id - 1))
                    else:
                        new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                                max_id=str(max_id - 1),
                                                since_id=sinceId)
                if not new_tweets:
                    print("No more tweets found")
                    break
                #for tweet in new_tweets:
                    # f.write(jsonpickle.encode(tweet._json, unpicklable=False) +
                     #       '\n')
                for tweet in new_tweets:
                    # print(self.api.get_user())
                    # empty dictionary to store required params of a tweet
                    parsed_tweet = {}
                    # saving text of tweet
                    stop_words = set(stopwords.words("english"))
                    parsed_tweet['text'] = tweet.text
                    parsed_tweet['user'] = tweet.user.name
                    #print(parsed_tweet['text'])
                    tweetss = re.sub(r'http://.*', '', tweet.text)
                    tweetss = re.sub(r'#\w+ ?', '', tweet.text)
                    tweetss = re.sub(r'http\S+', '', tweet.text)
                    tweetss = re.sub(r"http\S+", "", tweet.text)
                    tweetss = re.sub(r"https\S+", "", tweet.text)
                    tweetss = re.sub(r'^https?:\/\/.*[\r\n]*', '', tweet.text, flags=re.MULTILINE)
                    tweetss = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', tweet.text)
                    tweetss = html_parser.unescape(tweetss)
                    analysis = TextBlob(' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweetss).split()))

                    try:
                        s = unicode(tweetss)
                    except UnicodeDecodeError:
                        s = str(tweetss).encode('string_escape')
                        s = unicode(tweetss)

                    if 0.0 < analysis.sentiment.polarity <= 0.5:
                        parsed_tweet['sentiment'] = 'low_positive'
                        ptlweets.append(tweet)
                        polar = str(analysis.sentiment.polarity)
                        use = str(parsed_tweet['user']).encode('ascii', 'ignore')
                        txt = str(parsed_tweet['text']).encode('ascii', 'ignore')
                        insert_query = "INSERT INTO sentiment (Name, tweet, polarity, type) VALUES (%s, %s, %s, %s)"
                        cur.execute(insert_query, (use,txt,polar,1))

                    elif analysis.sentiment.polarity == 0:
                        parsed_tweet['sentiment'] = 'neutral'
                        neutweets.append(tweet)
                        polar = str(analysis.sentiment.polarity)
                        use = (parsed_tweet['user']).encode('ascii', 'ignore')
                        txt = (parsed_tweet['text']).encode('ascii', 'ignore')
                        insert_query = "INSERT INTO sentiment (Name, tweet, polarity, type) VALUES (%s, %s, %s, %s)"
                        cur.execute(insert_query, (use, txt, polar, 2))

                    elif analysis.sentiment.polarity > 0.5:
                        parsed_tweet['sentiment'] = 'high_positive'
                        ptweets.append(tweet)
                        polar = str(analysis.sentiment.polarity)
                        use = (parsed_tweet['user']).encode('ascii', 'ignore')
                        txt = (parsed_tweet['text']).encode('ascii', 'ignore')
                        insert_query = "INSERT INTO sentiment (Name, tweet, polarity, type) VALUES (%s, %s, %s, %s)"
                        cur.execute(insert_query, (use, txt, polar, 3))

                    elif -0.5 <= analysis.sentiment.polarity < 0.0:
                        parsed_tweet['sentiment'] = 'low_negative'
                        ntlweets.append(tweet)
                        polar = str(analysis.sentiment.polarity)
                        use = (parsed_tweet['user']).encode('ascii', 'ignore')
                        txt = (parsed_tweet['text']).encode('ascii', 'ignore')
                        insert_query = "INSERT INTO sentiment (Name, tweet, polarity, type) VALUES (%s, %s, %s, %s)"
                        cur.execute(insert_query, (use, txt, polar, 4))

                    elif analysis.sentiment.polarity < -0.5:
                        parsed_tweet['sentiment'] = 'high_negative'
                        ntweets.append(tweet)
                        polar = str(analysis.sentiment.polarity)
                        use = (parsed_tweet['user']).encode('ascii', 'ignore')
                        txt = (parsed_tweet['text']).encode('ascii', 'ignore')
                        insert_query = "INSERT INTO sentiment (Name, tweet, polarity, type) VALUES (%s, %s, %s, %s)"
                        cur.execute(insert_query, (use, txt, polar, 5))

                    # saving sentiment of tweet
                    # appending parsed tweet to tweets list
                    if tweet.retweet_count > 0:
                        # if tweet has retweets, ensure that it is appended only once
                        if parsed_tweet not in tweets:
                            tweets.append(parsed_tweet)
                    else:
                        tweets.append(parsed_tweet)
                tweetCount += len(new_tweets)
                #print("Downloaded {0} tweets".format(tweetCount))
                max_id = new_tweets[-1].id
            except tweepy.TweepError as e:
                # Just exit if any error
                print("some error : " + str(e))
                break

print("Downloaded {0} tweets ".format(tweetCount))

print("High Positive tweets percentage: {} %".format(100 * len(ptweets) / len(tweets)))
print("Low Positive tweets percentage: {} %".format(100 * len(ptlweets) / len(tweets)))
hp = format(100 * len(ptweets) / len(tweets))
lp = format(100 * len(ptlweets) / len(tweets))
p = int(hp) + int(lp)

# picking negative tweets from tweets
print("High Negative tweets percentage: {} %".format(100 * len(ntweets) / len(tweets)))
print("Low Negative tweets percentage: {} %".format(100 * len(ntlweets) / len(tweets)))
hn = format(100 * len(ntweets) / len(tweets))
ln = format(100 * len(ntlweets) / len(tweets))
ne = int(hn) + int(ln)

# percentage of neutral tweets
print("Neutral tweets percentage: {} % \
".format(100 * (len(tweets) - len(ntweets) - len(ptweets)- len(ntlweets) - len(ptlweets)) / len(tweets)+1))
n = format(100 * (len(tweets) - len(ntweets) - len(ptweets)- len(ntlweets) - len(ptlweets)) / len(tweets)+1)

#Graphical Representation
fig3 = fig3(p,ne,n)
fig5 = fig5(hp,lp,hn,ln,n)

#To open webbrowser
webbrowser.open(url)