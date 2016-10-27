###This program is used to find the wordlist that will be included in tuning process###

import sys
import json
import re
from afinn import Afinn
from collections import defaultdict, OrderedDict


reload(sys)
sys.setdefaultencoding('utf-8')
keyword = ["keyword_1","keyword_2","......","keyword_n"]

if __name__ == '__main__':

    W = []
    dT = defaultdict(dict)
    count = 0
    with open('path_to_Indonesian_twitter_data.json') as f:
        for line in f:
            row = json.loads(line)
            newtime = row["timestamp"]
            id = row["id"]
            txt = row["text"]
            txt = ' '.join(re.sub("(@[A-Za-z0-9]+)|(?:\#+[\w_]+[\w\'_\-]*[\w_]+)|(\w+\/\/\S+)|http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+"," ",txt).split())
            txt = txt.replace(";",",")
            txt = txt.replace("\"","")
            txt = txt.replace("\t"," ")
            if any(word in txt.lower() for word in keyword):
                afinn = Afinn(language='id',emoticons=True)
                score = afinn.score(txt)
                if score!=0:
                    count += 1
                    afinn = Afinn(language='id')
                    words = afinn.find_all(txt)
                    matched_words = len(set(words))
                    dT[txt] = {}
                    dT[txt]['matched'] = matched_words
                    dT[txt]['tot_score'] = score
                    dT[txt]['ts_tw'] = newtime
                    dT[txt]['id_tw'] = id
                    for word in words:
                        W.append(word)
                        word_score = afinn.score_with_pattern(word)
                        try:
                            dT[txt][word] += word_score  #output = dT['saya tidak ingin makan']['tidak']=-3
                        except:
                            dT[txt][word] = word_score
            ########

    #make unique wordlist
    L = list(set(W))
    #sort dT in descending order
    dT_desc = OrderedDict(sorted(dT.items(), key=lambda kv: kv[1]['matched'], reverse=True))

    num_wordlist = len(L)

    print "save the wordlist"
    fp = open('tuning_wordlist_candidate.txt', 'w')
    for word in sorted(L):
        fp.write(word + "\n")
    fp.close()

    fp = open('data_for_training.json', 'w')  #for training
    print "save twitter sentences"
    count = 0
    for text, arr_w in dT_desc.items():
        if count<num_wordlist:
            id = arr_w["id_tw"]
            datetime = arr_w["ts_tw"]
            totscore = arr_w["tot_score"]
            del arr_w['matched']
            del arr_w['tot_score']
            del arr_w['ts_tw']
            del arr_w['id_tw']
            datajson =json.dumps({"no":count+1,"id":id,"datetime":datetime,"totscore":totscore,"text":text,"word":arr_w})
            if count>0:
                fp.write("\n")
            fp.write(datajson)

        count += 1

    fp.close()

    print "Finish..................."