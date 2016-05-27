#!/usr/bin/python
# -*- coding: utf-8 -*-

### Author: Edward Huang

import time
import sys
import csv
from collections import OrderedDict

### This script takes the symptoms and herbs prescribed to each patient, and
### attempts to mine the frequent patterns from these two sets across all of
### the patients in the HIS dataset. Also creates an inverted index.
### Run time: 20 seconds.

def get_dictionary_elements(element_type):
    # Keeps track of all of the herbs and symptoms. This is mined by Sheng.
    all_elements = []
    f = open('./data/%s_dct.txt' % element_type, 'r')
    for i, line in enumerate(f):
        element, count = line.strip().split('\t')
        all_elements += [element]
    f.close()
    return all_elements

def get_transactions_and_inverse_index(all_herbs, all_symptoms):
    # Inverted index creation.
    invert_index_dct = {}
    transactions = []
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

        # Add element to the inverted index.
        for element in current_symptoms + current_herbs:
            if element in invert_index_dct:
                invert_index_dct[element] += [str(i)]
            else:
                invert_index_dct[element] = [str(i)]
        transactions += [(current_symptoms, current_herbs)]
    f.close()
    return transactions, invert_index_dct

def main():
    reload(sys)
    sys.setdefaultencoding('cp1252')

    all_herbs = get_dictionary_elements('herb')
    all_symptoms = get_dictionary_elements('sym')

    transactions, invert_index_dct = get_transactions_and_inverse_index(
        all_herbs, all_symptoms)

    # Write out to a CSV file.
    out = open('./data/HIS_transactions_words.csv', 'w')
    for i, transaction in enumerate(transactions):
        symptoms, herbs = transaction
        if len(symptoms) == 0 or len(herbs) == 0:
            print i
            continue
        out.write(','.join(symptoms) + '\t' + ','.join(herbs) + '\n')
    out.close()

    # Change the herbs and symptoms to their corresponding indices.
    herb_and_symptoms = all_herbs + all_symptoms
    for i, transaction in enumerate(transactions):
        transaction = transaction[0] + transaction[1]
        transactions[i] = [str(herb_and_symptoms.index(item)
            ) for item in transaction]

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

if __name__ == '__main__':
    start_time = time.time()
    main()
    print "---%f seconds---" % (time.time() - start_time)