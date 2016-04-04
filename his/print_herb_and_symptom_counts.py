#!/usr/bin/python
# -*- coding: utf-8 -*-

### Author: Edward Huang

import time
import sys
import csv
from collections import OrderedDict

### This script gets basic statistics from the HIS data.

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('cp1252')

    start_time = time.time()

    # Keeps track of all of the herbs and symptoms. This is mined by Sheng.
    all_herbs = []
    f = open('./data/herb_dct.txt', 'r')
    for i, line in enumerate(f):
        herb, count = line.strip().split('\t')
        all_herbs += [herb]
    f.close()

    all_symptoms = []
    f = open('./data/sym_dct.txt', 'r')
    for i, line in enumerate(f):
        symp, count = line.strip().split('\t')
        all_symptoms += [symp]
    f.close()

    herb_counts = []
    symp_counts = []

    f = open('./data/HIS_clean_data.txt', 'r')
    for i, line in enumerate(f):
        # Skip header
        if i == 0:
            continue
        line = line.replace('，',' ').replace('。',' ')
        line = line.replace('、', ' ').replace('颗粒', '').replace('免煎', '')
        line = line.replace('小', '').replace('中药:', '')
        date, symptoms, herbs = line.split('\t')
        symptoms = symptoms.split()
        # Each row is a unique transaction.
        current_herbs = []
        # Remove herbs not mined.
        for herb in herbs.split('  '):
            herb = herb.strip()
            if herb in all_herbs:
                current_herbs += [herb]
        herb_counts += [len(current_herbs)]

        current_symptoms = []
        # Remove symptoms not mined.
        for symptom in symptoms:
            if symptom in all_symptoms:
                current_symptoms += [symptom]
        symp_counts += [len(current_symptoms)]
    f.close()

    print len(herb_counts), len(symp_counts)
    print 'herb: ', sum(herb_counts) / float(len(herb_counts))
    print 'symptoms: ', sum(symp_counts) / float(len(symp_counts))

    print "---%f seconds---" % (time.time() - start_time)