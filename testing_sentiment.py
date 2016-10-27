from __future__ import division
import sys
import re
from afinn import Afinn
from collections import OrderedDict
import datetime
import numpy as np


def normalize(mtrx,new_min, new_max):
    matrix = []
    for x in mtrx:
        new_x = (x - np.min(mtrx))*(new_max-new_min)/(np.max(mtrx)-np.min(mtrx)) + new_min
        matrix.append(new_x)
    return np.array(matrix)

def pos_neg(mtrx):
    arr_mtrx=[]
    for x in mtrx:
        if x>0:
            arr_mtrx.append("positive")
        elif x<0:
            arr_mtrx.append("negative")
        else:
            arr_mtrx.append("neutral")

    return arr_mtrx

def accuracy_posneg(mtrxA, mtrxB):
    #mtrx A = actual, mtrxB = predicted
    count = 0
    _true = 0
    _false = 0
    for x in mtrxB:
        #print x + "-" + mtrxA[count]
        if x==mtrxA[count]:
            _true += 1
        else:
            _false += 1
        count += 1
    all = int(_true) + int(_false)
    acc = float(_true/all)*100
    print "Accuracy: " + str(acc) + "%"
    return acc

def prec_recall_posneg(mtrxA, mtrxB):
    #mtrx A = actual, mtrxB = predicted
    count = 0
    TP = 0
    TN = 0
    FP = 0
    FN = 0
    for x in mtrxB:
        #print x + "-" + mtrxA[count]
        if x==mtrxA[count]:
            if str(x)=="positive" or str(x)=="neutral":
                TP += 1
            else:
                TN += 1
        else:
            if str(x)=="positive" or str(x)=="neutral":
                FP += 1
            else:
                FN += 1
        count += 1
    all = count
    #if most sentiments are negatives
    precision = (TN/(TN+FN))*100
    recall = (TN/(TN+FP))*100

    #if most sentiments are positives
    #precision = (TP/(TP+FP))*100
    #recall = (TP/(TP+FN))*100
    return precision,recall

def calc_sentimen(txt):
    afinn = Afinn(language='id',emoticons=True)
    score0 = afinn.score(txt)
    #wordlist - the value is from linier matrix eq which simply replace the original value
    L1 = {}
    with open('path_to_wordlist1.txt') as f:
        for line in f:
            word = line.split("\t")
            L1[word[0]] = word[1].strip()

    #wordlist - the value resulting from the average value of the original and tuning value
    L2 = {}
    with open('path_to_wordlist2.txt') as f:
        for line in f:
            word = line.split("\t")
            L2[word[0]] = word[1].strip()

    score1 = 0
    score2 = 0
    words = afinn.find_all(txt)
    for word in words:
        try:
            word_score1 = L1[word]
            word_score2 = L2[word]
        except:
            word_score1 = 0
            word_score2 = 0
        score1 += float(word_score1)
        score2 += float(word_score2)
    return score0, score1, score2

if __name__=="__main__":

    matrix0 = []
    matrixF1 = []
    matrixF2 = []
    matrixA = []
    dT = {}

    fp = open('testing_result.txt', 'w')

    with open('path_to_testing_data.txt') as f:
        for line in f:
            word = line.split(";")
            no = word[0]
            id = word[1]
            dt = word[2]
            txt = word[3].strip()
            expert_score = word[4]
            score0, score1, score2 = calc_sentimen(txt)
            dT[id] = {}
            dT[id]['score0'] = score0
            dT[id]['score1'] = score1
            dT[id]['score2'] = score2
            dT[id]['exp_score'] = expert_score

            elm0 = []
            elm0.append(score0)
            matrix0.append(elm0)
            elmF1 = []
            elmF1.append(dT[id]['score1'])
            matrixF1.append(elmF1)
            elmF2 = []
            elmF2.append(dT[id]['score2'])
            matrixF2.append(elmF2)
            elmA = []
            elmA.append(dT[id]['expert_score'])
            matrixA.append(elmA)

            data = str(no) + ";" + str(id) + ";" + dt + ";" + txt + ";" + str(expert_score) + ";" + str(score0) + ";" + str(score1) + ";" + str(score2)
            print data
            fp.write(data + "\n")

    fp.close()

    matrix0 = np.array(matrix0)
    norm_matrix0 = normalize(matrix0,-3,3)
    matrixF1 = np.array(matrixF1)
    norm_matrixF1 = normalize(matrixF1,-3,3)
    matrixF2 = np.array(matrixF2)
    norm_matrixF2 = normalize(matrixF2,-3,3)
    matrixF3 = np.array(matrixF3)
    norm_matrixF3 = normalize(matrixF3,-3,3)
    matrixA = np.array(matrixA)

    #calculate precision: positive - negative
    pnA1 = pos_neg(matrixA1)
    pn0 = pos_neg(matrix0)
    pnF1 = pos_neg(matrixF1)
    pnF2 = pos_neg(matrixF2)
    T0 = accuracy_posneg(pnA1, pn0)
    TF1 = accuracy_posneg(pnA1, pnF1)
    TF2 = accuracy_posneg(pnA1, pnF2)
    PR0,RE0 = prec_recall_posneg(pnA1, pn0)
    PR1,RE1 = prec_recall_posneg(pnA1, pnF1)
    PR2,RE2 = prec_recall_posneg(pnA1, pnF2)
    F1measure0 = 2*PR0*RE0/(PR0+RE0)
    F1measure1 = 2*PR1*RE1/(PR1+RE1)
    F1measure2 = 2*PR2*RE2/(PR2+RE2)
    print "Baseline-AFINN_ID --> accuracy: " + str(T0) + "%, precision: " + str(PR0) + "%, recall: " + str(RE0) + "%, F1 measure: " + str(F1measure0) + "%"
    print "Tuning-AFINN_ID --> accuracy:  " + str(TF1) + "%, precision: " + str(PR1) + "%, recall: " + str(RE1) + "%, F1 measure: " + str(F1measure1) + "%"
    print "Tuning-avg-AFINN_ID --> accuracy:  " + str(TF2) + "%, precision: " + str(PR2) + "%, recall: " + str(RE2) + "%, F1 measure: " + str(F1measure2) + "%"

    print "Finish........"


