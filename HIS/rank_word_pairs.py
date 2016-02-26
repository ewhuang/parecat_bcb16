### Author: Edward Huang

import sys
import math
from collections import OrderedDict
import operator

### This script goes through the original data, and for each herb, symptom pair
### we compute mutual information (or some other similarity score).

# Number of most frequent herbs and symptoms to check.
NUM_HERBS = 600
NUM_SYMPTOMS = 4000

# Pointwise mutual information.
def pmi(c_12, c_1, c_2, N):
    # N is the number of bigram herb-symptom pairs.
    # c_12 is C(w_1, w_2), c_1 = C(w_1), c_2 = C(w_2)
    if c_12 == 0:
        return float('-inf')
    return math.log(c_12, 2) + math.log(N, 2) - math.log(c_1, 2) - math.log(c_2, 2)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: %s mi' % sys.argv[0]
        exit()
    method = sys.argv[1]

    # Retrieve the inverted index.
    invert_index_dct = {}
    f = open('./data/HIS_inverted_index.txt', 'r')
    for line in f:
        element, patient_list = line.strip().split('\t')
        invert_index_dct[element] = set(patient_list.split())
    f.close()

    # Read in the herb and symptom count dictionaries.
    herb_dct = OrderedDict({})
    f = open('./data/herb_dct.txt', 'r')
    for i, line in enumerate(f):
        if len(herb_dct) == NUM_HERBS:
            break
        herb, count = line.strip().split('\t')
        if herb not in invert_index_dct:
            continue
        count = int(count)
        herb_dct[herb] = count
    f.close()

    symp_dct = OrderedDict({})
    f = open('./data/sym_dct.txt', 'r')
    for i, line in enumerate(f):
        if len(symp_dct) == NUM_SYMPTOMS:
            break
        symp, count = line.strip().split('\t')
        if symp not in invert_index_dct:
            continue
        count = int(count)
        symp_dct[symp] = count
    f.close()

    # Compute mutual information between every herb-symptom pair.
    herb_symp_sim_dct = {}
    num_pairs = NUM_SYMPTOMS * NUM_HERBS
    for herb in herb_dct:
        herb_visits = invert_index_dct[herb]
        c_herb = len(herb_visits)
        for symp in symp_dct:
            symp_visits = invert_index_dct[symp]
            c_symp = len(symp_visits)
            # Count how many visits a symptom and herb appear together.
            c_symp_and_herb = len(herb_visits.intersection(symp_visits))
            if method == 'mi':
                sim_score = pmi(c_symp_and_herb, c_herb, c_symp, num_pairs)

            herb_symp_sim_dct[(herb, symp)] = sim_score

    hssd = sorted(herb_symp_sim_dct.items(), key=lambda x: x[1], reverse=True)
    
    out = open('./results/HIS_herb_symp_%s.txt' % method, 'w')
    for (herb, symp), sim_score in hssd:
        out.write('%s\t%s\t%f\n' % (herb, symp, sim_score))
    out.close()
    # if method == 'mi':
    #     # Use mutual information function.