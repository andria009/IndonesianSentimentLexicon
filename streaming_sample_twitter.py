#This program is used to find the sentiment score from twitter sample stream and the result is stored in a file every 10 minutes

from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
import json
import sys
import re
from afinn import Afinn
from collections import OrderedDict
import datetime

def calc_sentimen(txt):
    #calculate sentiment score only from ID-AFINN wordlist
    afinn = Afinn(language='id',emoticons=True)
    score1 = afinn.score(txt)

    #calculate sentiment score by combining the ID-AFINN wordlist and its tuning score
    L = {}
    with open('path_to_wordlist') as f:
        for line in f:
            word = line.split("\t")
            L[word[0]] = word[1].strip()

    score2 = 0
    words = afinn.find_all(txt)
    for word in words:
        try:
            word_score2 = L[word]
        except:
            #Since the result of tuned wordlist still limited, if no score found, we try to find it in AFINN wordlist.
            #However, for research purpose we apply word_score2 = 0 to compare the result of ID-AFINN and the tuned wordlist
            word_score2 = afinn.score_with_pattern(word)
        score2 += float(word_score2)
    return score1, score2

if __name__=="__main__":

    ACCESS_TOKEN = 'your access token'
    ACCESS_SECRET = 'your access secret'
    CONSUMER_KEY = 'your consumer key'
    CONSUMER_SECRET = 'your access token'


    oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

    while True:
        try:
            twitter_stream = TwitterStream(auth=oauth)
            iterator = twitter_stream.statuses.sample()

            count=0
            format_file = "%Y%m%d%H%M%S"
            for tweet in iterator:
                try:
                    if tweet["lang"]=="in":
                        txt = tweet["text"]
                        txt = ' '.join(re.sub("(@[A-Za-z0-9]+)|(?:\#+[\w_]+[\w\'_\-]*[\w_]+)|(\w+\/\/\S+)|http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+"," ",txt).split())
                        txt = txt.replace(";",",")
                        txt = txt.replace("\"","")
                        txt = txt.replace("\t"," ")
                        score1, score2 = calc_sentimen(txt)
                        d = OrderedDict()
                        d["id"] = tweet["user"]["id"]
                        d["datetime"] = tweet["created_at"]
                        d["location"] = tweet["user"]["location"]
                        d["coordinates"] = tweet["coordinates"]
                        d["text"] = txt
                        d["score_AFINN"]= score1
                        d["score_tuning"]= score2
                        datajson = json.dumps(d)
                        t = datetime.datetime.now()

                        #save the sentiment result in a file every 10 minutes
                        if count==0:
                            next_t = t + datetime.timedelta(minutes = 10)
                            tf = t.strftime(format_file)
                            fp = open('path_to_file_' + tf + '.json', 'w')
                        else:
                            if t<=next_t:
                                fp = open('path_to_file_' + tf + '.json', 'a')
                                fp.write("\n")
                            else:
                                next_t = t + datetime.timedelta(minutes = 10)
                                tf = t.strftime(format_file)
                                fp = open('path_to_file_' + tf + '.json', 'w')

                        fp.write(datajson)
                        fp.close()
                        print "data-" + str(count+1) + ": " + datajson
                        count += 1
                except:
                    #message has been deleted
                    e = sys.exc_info()[1]
                    print "Error: %s" % e
        except TwitterRequestError as e:
            if e.status_code < 500:
                # something needs to be fixed before re-connecting
                raise
            else:
                # temporary interruption, re-try request
                pass
        except TwitterConnectionError:
            # temporary interruption, re-try request
            pass


