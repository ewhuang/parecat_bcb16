### Author: Edward Huang

import sys
import operator

### This script converts the output of the C fpgrowth script to readable, tab-
### separated columns of herbs, symptoms, and support counts.

if __name__ == '__main__':    
    reload(sys)
    sys.setdefaultencoding('cp1252')

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

    herb_and_symptoms = all_herbs + all_symptoms

    pattern_dct = {}
    f = open('./results/HIS_raw_max_patterns.txt', 'r')
    for i, line in enumerate(f):
        line = line.split()
        items, support = line[:-1], line[-1]

        items = tuple([herb_and_symptoms[item] for item in map(int, items)])

        # Get rid of parentheses.
        support = int(support[1:-1])
        # Add pattern and support to dictionary.
        pattern_dct[items] = support
    f.close()

    # Sort the dictionary by support value.
    pattern_dct = sorted(pattern_dct.items(), key=lambda x: x[1], reverse=True)
    out = open('./results/HIS_max_patterns.txt', 'w')
    for transaction, support in pattern_dct:
        trans_herbs = []
        trans_symps = []
        for item in transaction:
            if item in all_herbs:
                trans_herbs += [item]
            else:
                assert item in all_symptoms
                trans_symps += [item]

        if len(trans_herbs) == 0 or len(trans_symps) == 0:
            continue

        out.write(','.join(trans_herbs) + '\t' + ','.join(trans_symps) + '\t')
        out.write(str(support) + '\n')
    out.close()
