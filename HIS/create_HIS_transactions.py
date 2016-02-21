#!/usr/bin/python
# -*- coding: utf-8 -*-

### Author: Edward Huang

import time

### This script takes the symptoms and drugs prescribed to each patient, and
### attempts to mine the frequent patterns from these two sets across all of the
### patients in the ZRS dataset.

MIN_SUP = 2

if __name__ == '__main__':
    start_time = time.time()

    herb_symptom_mappings = []

    transactions = []
    f = open('./data/HIS_clean_data.txt', 'r')
    for i, line in enumerate(f):
        # Skip header
        if i == 0:
            continue
        line = line.replace('，',' ').replace('。',' ').replace(',', ' ')
        line = line.replace('小', '')
        date, symptoms, herbs = line.split('\t')
        # Each row is a unique transaction.
        herbs_no_dosage = []
        for herb in herbs:
            # Skip the elements in the herb list that are dosages.
            if herb[-1] == 'g' and herb[:-1].isdigit():
                continue
            herbs_no_dosage += [herb]
        transaction = symptoms.split() + herbs_no_dosage
        # for element in transaction:
        #     if element not in herb_symptom_mappings:
        #         herb_symptom_mappings += []
        transactions += [transaction]
    f.close()

    # Write out to a CSV file.
    out = open('./data/HIS_transactions.csv', 'w')
    for transaction in transactions:
        out.write(','.join(transaction) + '\n')
    out.close()

    print "---%f seconds---" % (time.time() - start_time)