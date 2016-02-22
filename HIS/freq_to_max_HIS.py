#!/usr/bin/python
# -*- coding: utf-8 -*-

### Author: Edward Huang

import operator
import ast
import sys
from collections import OrderedDict

### This script takes the frequent patterns mined for the HIS data and keeps
### only the closed patterns.

def has_ele(lst, st):
    for ele in lst:
        if ele in st:
            return True
    return False

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('cp1252')

    drug_and_symptoms = []
    f = open('./data/HIS_herb_symptom_mappings.txt', 'r')
    for i, line in enumerate(f):
        drug_and_symptoms += [line.strip()]
    f.close()

    all_herbs = set([])
    f = open('./data/HIS_herbs.txt', 'r')
    for line in f:
        all_herbs.add(drug_and_symptoms[int(line.strip())])
    f.close()

    all_symptoms = set([])
    f = open('./data/HIS_symptoms.txt', 'r')
    for line in f:
        all_symptoms.add(drug_and_symptoms[int(line.strip())])
    f.close()

    max_patterns = []
    pat_sup_dct = {}

    f = open('./data/HIS_frequent_patterns.txt', 'r')
    for i, line in enumerate(f):
        print i
        # Parse file contents.
        close_bracket_index = line.index(']') + 1
        curr_pattern = line[:close_bracket_index]
        support = line[close_bracket_index:]
        # Convert the literal string interpretation of a list to an actual list.
        curr_pattern = ast.literal_eval(curr_pattern)
        # Convert the pattern to a set.
        curr_pattern = set(map(int, curr_pattern))

        # Check if we have at least one herb and one symptom.
        test_pattern = [drug_and_symptoms[ele] for ele in curr_pattern]
        if not has_ele(test_pattern, all_herbs) or not has_ele(test_pattern, all_symptoms):
            continue

        pat_sup_dct[tuple(curr_pattern)] = int(support)

        # Check if the current pattern is a subset of something we have
        # previously seen. Also find the patterns which are bad.
        isMax = True
        bad_patterns = []
        for pattern in max_patterns:
            if curr_pattern < pattern:
                isMax = False
                break
            if curr_pattern > pattern:
                bad_patterns += [pattern]
        # Delete the bad patterns from the set.
        for pattern in bad_patterns:
            max_patterns.remove(pattern)
        if isMax:
            max_patterns += [curr_pattern]
    f.close()

    # Sort the pattern dictionary by support count.
    pat_sup_dct = sorted(pat_sup_dct.items(), key=lambda x: x[1], reverse=True)

    # Write out the closed patterns.
    out = open('./results/HIS_max_patterns.txt', 'w')
    for pattern, support in pat_sup_dct:
        if set(pattern) not in max_patterns:
            continue
        pattern = [drug_and_symptoms[item] for item in pattern]
        herbs = []
        symptoms = []
        for ele in pattern:
            if ele in all_herbs:
                herbs += [ele]
            else:
                assert ele in all_symptoms
                symptoms += [ele]
        out.write(str(support) + '\t' + ','.join(herbs) + '\t' + ','.join(symptoms) + '\n')
    out.close()