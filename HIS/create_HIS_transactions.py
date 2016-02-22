#!/usr/bin/python
# -*- coding: utf-8 -*-

### Author: Edward Huang

import time
import sys
import csv
from collections import OrderedDict

### This script takes the symptoms and drugs prescribed to each patient, and
### attempts to mine the frequent patterns from these two sets across all of the
### patients in the ZRS dataset.

MIN_SUP = 2

if __name__ == '__main__':
    start_time = time.time()
    reload(sys)
    sys.setdefaultencoding('cp1252')

    drug_symptom_counts = OrderedDict({})
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
        for herb in herbs.split():
            # Skip the elements in the herb list that are dosages.
            if herb[0].isdigit():
                continue
            herbs_no_dosage += [herb]
        transaction = symptoms.split() + herbs_no_dosage
        # Count the number of times each drug or symptom appears.
        for element in transaction:
            if element not in drug_symptom_counts:
                drug_symptom_counts[element] = 1
            else:
                drug_symptom_counts[element] += 1
        transactions += [transaction]
    f.close()

    # Get rid of symptoms or drugs that do not appear many times, or appear too
    # much.
    num_transactions = len(transactions)
    bad_elements = []
    for element in drug_symptom_counts:
        count = drug_symptom_counts[element]
        if count > 0.1 * num_transactions or count < 5:
            bad_elements += [element]
    for bad_element in bad_elements:
        del drug_symptom_counts[bad_element]

    # Delete the actual bad symptoms or drugs from each transaction.
    for i, transaction in enumerate(transactions):
        for element in bad_elements:
            while element in transaction:
                transactions[i].remove(element)

    # Change the drugs and symptoms to their corresponding indices.
    drug_and_symptoms = drug_symptom_counts.keys()
    for i, transaction in enumerate(transactions):
        transactions[i] = [str(drug_and_symptoms.index(item)) for item in transaction]

    # Write out to a text file. Convert to CSV file after.
    out = open('./data/HIS_transactions.csv', 'w')
    for transaction in transactions:
        out.write(','.join(transaction) + '\n')
    out.close()

    print "---%f seconds---" % (time.time() - start_time)