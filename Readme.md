# Indonesian Sentiment Lexicon

###File list:
1. gtranslate_afinn.py
...to translate the wordlist by using Google Translate and continued by preprocessing step
2. pre_tuning_wordlist.py
...to find the wordlist that will be included in tuning process
3. tuning_wordlist.py
...to tune the wordlist by using linear matrix equation
4. testing_sentiment.py
...to test sentiment from test data set
5. streaming_sample_twitter.py
...to find the sentiment score from twitter sample stream and the result is stored in a file every 10 minutes

###Credit:
* [FNielsen/afinn](https://github.com/fnielsen/afinn)
* [Indonesian language added](https://github.com/dataP2I/afinn)
