### Author: Edward Huang

import sys
import operator

### This script converts the output of the C fpgrowth script to readable, tab-
### separated columns of herbs, symptoms, and support counts.

if __name__ == '__main__':    
    reload(sys)
    sys.setdefaultencoding('cp1252')

    herb_symptom_mappings = []
    f = open('./data/HIS_herb_symptom_mappings.txt', 'r')
    for line in f:
        herb_symptom_mappings += [line.strip()]
    f.close()

    all_herbs = set([])
    f = open('./data/HIS_herbs.txt', 'r')
    for line in f:
        all_herbs.add(line.strip())
    f.close()

    all_symptoms = set([])
    f = open('./data/HIS_symptoms.txt', 'r')
    for line in f:
        all_symptoms.add(line.strip())
    f.close()

    pattern_dct = {}
    f = open('./results/HIS_raw_max_patterns.txt', 'r')
    for i, line in enumerate(f):
        line = line.split()
        items, support = tuple(line[:-1]), line[-1]
        # Convert each item to a an int.
        # items = tuple([herb_symptom_mappings[item] for item in map(int, items)])

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
        trans_herbs = [herb_symptom_mappings[herb] for herb in map(int, trans_herbs)]
        trans_symps = [herb_symptom_mappings[symp] for symp in map(int, trans_symps)]

        if len(trans_herbs) == 0 or len(trans_symps) == 0:
            continue

        out.write(','.join(trans_herbs) + '\t' + ','.join(trans_symps) + '\t')
        out.write(str(support) + '\n')
    out.close()
