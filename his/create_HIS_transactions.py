#!/usr/bin/python
# -*- coding: utf-8 -*-

### Author: Edward Huang

import time
import sys
import csv
from collections import OrderedDict

### This script takes the symptoms and herbs prescribed to each patient, and
### attempts to mine the frequent patterns from these two sets across all of the
### patients in the HIS dataset. Also creates an inverted index.

MIN_SUPP = 20

def has_item(lst, st):
    for ele in lst:
        if ele in st:
            return True
    return False

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('cp1252')

    start_time = time.time()

    # Reading in the index dictionary for herbs and symptoms.
    herb_symptom_counts = OrderedDict({})
    transactions = []

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

    # Inverted index creation.
    invert_index_dct = {}

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

        current_symptoms = []
        # Remove symptoms not mined.
        for symptom in symptoms:
            if symptom in all_symptoms:
                current_symptoms += [symptom]

        transaction = current_symptoms + current_herbs
        # Add element to the inverted index.
        for element in transaction:
            if element in invert_index_dct:
                invert_index_dct[element] += [str(i)]
            else:
                invert_index_dct[element] = [str(i)]
        transactions += [transaction]
    f.close()

    # Remove transactions that do not have at least one herb and symptom.
    bad_transactions = []
    for transaction in transactions:
        if not has_item(transaction, all_herbs) or not has_item(transaction, all_symptoms):
            bad_transactions += [transaction]
    for transaction in bad_transactions:
        transactions.remove(transaction)

    # Write out to a CSV file.
    out = open('./data/HIS_transactions_words.csv', 'w')
    for i, transaction in enumerate(transactions):
        out.write(','.join(transaction) + '\n')
    out.close()

    # Change the herbs and symptoms to their corresponding indices.
    herb_and_symptoms = all_herbs + all_symptoms
    for i, transaction in enumerate(transactions):
        transactions[i] = [str(herb_and_symptoms.index(item)) for item in transaction]

    # Write out to a CSV file.
    out = open('./data/HIS_transactions.csv', 'w')
    for i, transaction in enumerate(transactions):
        out.write(','.join(transaction) + '\n')
    out.close()

    # Write out the inverted index.
    out = open('./data/HIS_inverted_index.txt', 'w')
    for element in invert_index_dct:
        out.write(element + '\t' + ' '.join(invert_index_dct[element]) + '\n')
    out.close()

    print "---%f seconds---" % (time.time() - start_time)