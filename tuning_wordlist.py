###This program is used to tune the wordlist by using linear matrix equation#####

import sys
import json
import re
from afinn import Afinn
from collections import defaultdict, OrderedDict
import numpy as np
from numpy import *


reload(sys)
sys.setdefaultencoding('utf-8')

subj = "subject"
topic = "topic"
path_text = 'path_to_data/Data/' + subj+ '/data_text/'


def normalize(mtrx,new_min, new_max):
    matrix = []
    for x in mtrx:
        new_x = (x - np.min(mtrx))*(new_max-new_min)/(np.max(mtrx)-np.min(mtrx)) + new_min
        matrix.append(new_x)
    return np.array(matrix)

if __name__ == '__main__':
    afinn = Afinn(language='id',emoticons=True)
    np.set_printoptions(threshold=np.inf, precision=1)

    #extract wordlist
    L=[]
    with open('tuning_wordlist_candidate.txt') as f:
        for line in f:
            L.append(line.strip())


    matrixA1 = []    #for algorithm's score
    matrixA2 = []    #for expert's score
    matrixB1 = []    #for algorithm's result
    matrixB2 = []    #for expert's result

    count = 0
    with open('data_for_training.json') as f:
        for line in f:
            row = json.loads(line)
            word = row["word"]
            text = row["text"]
            totscore = row["totscore"]
            elmA1 = []
            for wd in sorted(L):
                try:
                    elmA1.append(word[wd])   #ex. word = {'ingin':1}
                except KeyError:
                    elmA1.append(0)
            matrixA1.append(elmA1)

            elmB1 = []
            elmB1.append(totscore)
            matrixB1.append(elmB1)
            count += 1

    mA1 = np.array(matrixA1)
    mB1 = np.array(matrixB1)
    #normalize the AFINN score
    new_mB1 = normalize(mB1,-3,3)

    #normalize the algorithm's score in matrix A
    factor = new_mB1/mB1
    count = 0
    new_mA1 = []
    for x in mA1:
        new_mA1.append(factor[count]*x)
        count += 1
    new_mA1 = np.array(new_mA1)


    count = 0
    file_expert = "path_to_evaluation_file_from_experts.csv"
    with open(file_expert) as f:
        for line in f:
            row = line.split(";")
            id = row[1]
            text = row[3]
            words = afinn.find_all(text)
            totscore = row[4]
            numW = {}
            for word in words:
                numW[word]=words.count(word)    #find words occurence

            elmA2 = []
            for wd in sorted(L):
                try:
                    elmA2.append(numW[wd])
                except KeyError:
                    elmA2.append(0)
            matrixA2.append(elmA2)

            elmB2 = []
            elmB2.append(int(totscore))
            matrixB2.append(elmB2)
            count += 1


    mA2 = np.array(matrixA2)
    mB2 = np.array(matrixB2)

    ####begin the tuning process######

    #linear eq on expert matrix
    ls = np.linalg.lstsq(mA2, mB2)
    factor = ls[0]
    count = 0
    new_mA2 = []
    for x in mA2:
        new_mA2.append(factor[count]*x)
        count += 1
    new_mA2 = np.array(new_mA2)

    #update the wordlist score
    fp1 = open('path_to_wordlist1.txt', 'w')  #the new value is simply replace the original value
    fp2 = open('path_to_wordlist2.txt', 'w') #the new value resulting from the average value of the original and tuning value
    dA = new_mA1 - new_mA2
    dB = new_mB1 - mB2
    ls = np.linalg.lstsq(dA, dB)
    factor = normalize(ls[0],-5,5)
    new_L = {}
    new_L2 = {}
    count = 0
    for wd in sorted(L):
        new_L[wd] = factor[count]
        afinn_score = afinn.score_with_pattern(wd)
        new_L2[wd] = new_L[wd] - ((new_L[wd]-afinn_score)/2)
        fp1.write(wd + "\t" + str(new_L[wd][0])+ "\n")
        fp2.write(wd + "\t" + str(new_L2[wd][0])+ "\n")
        count += 1
    fp1.close()
    fp2.close()


    print "Finish..................."

