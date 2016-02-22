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

def has_item(lst, st):
    for ele in lst:
        if ele in st:
            return True
    return False

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('cp1252')

    start_time = time.time()
    # Reading in the index dictionary for drugs and symptoms.
    drug_symptom_counts = OrderedDict({})
    transactions = []
    # Keeps track of all of the herbs and symptoms.
    all_herbs = set([])
    all_symptoms = set([])
    f = open('./data/HIS_clean_data.txt', 'r')
    for i, line in enumerate(f):
        # Skip header
        if i == 0:
            continue
        line = line.replace('，',' ').replace('。',' ').replace(',', ' ')
        line = line.replace('小', '')
        date, symptoms, herbs = line.split('\t')
        symptoms = symptoms.split()
        # Each row is a unique transaction.
        herbs_no_dosage = []
        for herb in herbs.split():
            # Skip the elements in the herb list that are dosages.
            if not herb[0].isdigit():
                herbs_no_dosage += [herb]
        transaction = symptoms + herbs_no_dosage
        # Count the number of times each drug or symptom appears.
        for element in transaction:
            if element not in drug_symptom_counts:
                drug_symptom_counts[element] = 1
            else:
                drug_symptom_counts[element] += 1
            # Check what the element was.
            if element in herbs_no_dosage:
                all_herbs.add(element)
            else:
                all_symptoms.add(element)
        transactions += [transaction]
    f.close()

    # Get rid of symptoms or drugs that do not appear many times, or appear too
    # much.
    num_transactions = len(transactions)
    bad_elements = []
    for element in drug_symptom_counts:
        count = drug_symptom_counts[element]
        if count > 0.05 * num_transactions or count < 5:
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

    # Write out herbs and symptoms to files.
    herb_out = open('./data/HIS_herbs.txt', 'w')
    symptom_out = open('./data/HIS_symptoms.txt', 'w')
    for item in drug_and_symptoms:
        item_index = str(drug_and_symptoms.index(item))
        if item in all_herbs:
            herb_out.write(item_index + '\n')
        else:
            symptom_out.write(item_index + '\n')
    symptom_out.close()
    herb_out.close()

    # Write out the mappings between herbs/symptoms and indices.
    m_out = open('./data/HIS_herb_symptom_mappings.txt', 'w')
    for item in drug_and_symptoms:
        m_out.write(item + '\n')
    m_out.close()

    # Remove transactions that do not have at least one herb and symptom.
    bad_transactions = []
    for transaction in transactions:
        if not has_item(transaction, all_herbs) or not has_item(transaction, all_symptoms):
            bad_transactions += [transaction]
    for transaction in bad_transactions:
        transactions.remove(transaction)

    for i, transaction in enumerate(transactions):
        transactions[i] = [str(drug_and_symptoms.index(item)) for item in transaction]


    # Write out to a CSV file.
    out = open('./data/HIS_transactions.csv', 'w')
    for transaction in transactions:
        out.write(','.join(transaction) + '\n')
    out.close()

    print "---%f seconds---" % (time.time() - start_time)