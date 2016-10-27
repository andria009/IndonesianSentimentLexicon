###This program is used to translate the wordlist by using Google Translate and continued by preprocessing step###

import sys
from bs4 import BeautifulSoup
import urllib2
import urllib
from collections import defaultdict
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

def googletrans(txt):
    data = {'sl':'en','tl':'id','text':txt}
    querystring = urllib.urlencode(data)
    request = urllib2.Request('http://www.translate.google.com' + '?' + querystring )
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11')
    opener = urllib2.build_opener()
    feeddata = opener.open(request).read()
    #print feeddata
    soup = BeautifulSoup(feeddata, "html5lib")
    html = soup.find('span', id="result_box")
    tr_text = html.get_text()
    return tr_text;

def translate_afinn():
    reload(sys)
    sys.setdefaultencoding('utf8')
    count = 0
    no = 0
    temp_data = ""
    with open("path_to_english_sentiment_wordlist.txt") as ct:
        for line in ct:
            no += 1
            count += 1
            word = line.split('\t')
            synword = word[0]
            score = word[1]
            tr_text = googletrans(synword)
            data = str(no) + "\t" + synword + "\t" + tr_text + "\t" + score
            try:
                temp_data = temp_data + data
            except:
                e = sys.exc_info()[1]
                print "Error: %s" % e

            print "data-" + str(count) + ": " + data
            if count==10:
                out = open('path_to_translated_wordlist', 'a')
                out.write(temp_data)
                out.close()
                print "written--------------\n"
                count = 0
                temp_data = ""


    if count<10:
        out = open('path_to_translated_wordlist', 'a')
        out.write(temp_data)
        out.close()
        print "written--------------\n"

    print "Finish...."
    ct.close()

def to_dict(arr_text):
    #convert list to dictionary, aligning word to its score(s)
    d = defaultdict(list)
    for k, v in arr_text:
        d[k].append(v)
    print list(d.items())

    #sort the wordlist
    sort_text =  sorted(list(d.items()),key=lambda x: x[0])
    return sort_text

def aggregate_afinn():
    #asign a single score for each word.
    arr_text = []
    count = 0
    num = 0
    with open("AFINN_ID_rev1.txt") as ct:
        for line in ct:
            num += 1
            if num>1:
                word = line.split("\t")
                en_word = word[1]
                id_word = word[2].strip()
                score = word[3].strip()
                arr_text.append([])
                arr_text[count].append(id_word.lower())
                arr_text[count].append(score)
                count += 1
    ct.close()
    sort_text =  to_dict(arr_text)

    out = open('agg_AFINN_ID.txt', 'w')
    title = "#no\tid_word\tmulti_score\tscore\n"
    out.write(title)

    #if there are multiple scores in a word, we find the maximum value
    count = 0
    for k,v in list(sort_text):
        count += 1
        data = str(count) + "\t" + str(k) + "\t" + str(v) + "\t" + str(max(v))
        print data
        out.write(data + "\n")

    print "Agregation finish...."
    out.close()

def stemming_afinn():
    #stemming the word to enrich the wordlist
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    out = open('stem_AFINN_ID.txt', 'w')
    title = "#no\tid_word\tbasic_word\tscore\n"
    out.write(title)
    arr_text = []
    count = 0
    with open("agg_AFINN_ID.txt") as ct:
        for line in ct:
            if count>0:
                word = line.split("\t")
                no = word[0]
                id_word = word[1]
                score = word[3].strip()
                out_stemmer = stemmer.stem(id_word)
                data = no + "\t" + id_word + "\t" + out_stemmer + "\t" + score
                print data
                out.write(data + "\n")
            count += 1
    ct.close()
    print "Stemming finish...."
    out.close()

def compile_afinn():
    #merge the wordlist resulting from aggregation and stemming process
    print "Now we start the the wordlist compilation ......"
    arr_text = []
    count = 0
    with open("agg_AFINN_ID.txt") as ct:
        for line in ct:
            word = line.split("\t")
            id_word = word[1]
            score = word[3].strip()
            arr_text.append([])
            arr_text[count].append(id_word)
            arr_text[count].append(score)
            count += 1
    ct.close()

    with open("stem_AFINN_ID.txt") as ct:
        for line in ct:
            word = line.split("\t")
            id_word = word[2]
            score = word[3].strip()
            arr_text.append([])
            arr_text[count].append(id_word)
            arr_text[count].append(score)
            count += 1
    ct.close()

    sort_text =  to_dict(arr_text)

    out = open('AFINN-16-ID.txt', 'w')

    #find the maximum score that will be assigned to the word
    count = 0
    for k,v in list(sort_text):
        count += 1
        data = str(count) + "\t" + str(k) + "\t" + str(v) + "\t" + str(max(v))
        print data
        out.write(str(k) + "\t" + str(max(v) + "\n"))

    print "Finish............"
    out.close()

##############main####################################
if __name__ == '__main__':
    translate_afinn()   #translate by using google translate
    aggregate_afinn()   #aggregate the same translation wordlist
    stemming_afinn()    #stemming the translation wordlist
    compile_afinn()     #merge the aggregation and stemming result