### Author: Edward Huang

import itertools
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

def read_stomach_data():
    '''
    This function reads the HIS stomach disease data, and forms a patient 
    dictionary where keys are patient ID's (line numbers) and values are lists
    of symptoms, herbs, or both, depending on the vector_type input.
    '''
    symptom_count_dct, herb_count_dct = {}, {}
    cooccurrence_count_dct = {}
    # This dictionary contains the consolidated visits for any single patient.
    # Keys are (name, birthday) pairs.
    N = 0
    f = open('./data/HIS_tuple_word.txt', 'r')
    for i, line in enumerate(f):
        # if disease not in disease_label_list[i]:
        #     continue
        (patient_disease, name, birthday, visit_date, patient_symptoms,
            patient_herbs) = line.strip('\n').split('\t')

        patient_symptoms = list(set(patient_symptoms.strip().split(':')))
        patient_herbs = list(set(patient_herbs.strip().split(':')))
        if patient_symptoms == [''] or patient_herbs == ['']:
            continue

        # Add to the master lists of symptoms and herbs.
        for symptom in patient_symptoms:
            if symptom not in symptom_count_dct:
                symptom_count_dct[symptom] = 1
            else:
                symptom_count_dct[symptom] += 1

        for herb in patient_herbs:
            # Update counts.
            if herb not in herb_count_dct:
                herb_count_dct[herb] = 1
            else:
                herb_count_dct[herb] += 1

        # Do co-occurrence computations.
        pair_list = list(itertools.combinations(list(set(patient_symptoms +
            patient_herbs)), 2))
        for pair in pair_list:
            node_a, node_b = pair
            if pair in cooccurrence_count_dct:
                cooccurrence_count_dct[pair] += 1
            elif (node_b, node_a) in cooccurrence_count_dct:
                cooccurrence_count_dct[(node_b, node_a)] += 1
            else:
                cooccurrence_count_dct[pair] = 1
        N += 1
    f.close()
    
    return symptom_count_dct, herb_count_dct, cooccurrence_count_dct, N

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: %s mi' % sys.argv[0]
        exit()
    method = sys.argv[1]

    (symptom_count_dct, herb_count_dct, cooccurrence_count_dct,
        N) = read_stomach_data()

    # Compute mutual information between every herb-symptom pair.
    herb_symp_sim_dct = {}
    num_pairs = NUM_SYMPTOMS * NUM_HERBS

    for (node_a, node_b) in cooccurrence_count_dct:
        if node_a in herb_count_dct:
            N_A = herb_count_dct[node_a]
        else:
            N_A = symptom_count_dct[node_a]

        if node_b in herb_count_dct:
            N_B = herb_count_dct[node_b]
        else:
            N_B = symptom_count_dct[node_b]

        # Count how many visits a symptom and herb appear together.
        if (node_a, node_b) in cooccurrence_count_dct:
            N_AB = cooccurrence_count_dct[(node_a, node_b)]
        elif (node_b, node_a) in cooccurrence_count_dct:
            N_AB = cooccurrence_count_dct[(node_b, node_a)]            
        else:
            N_AB = 0

        if method == 'pmi':
            sim_score = pmi(N_AB, N_A, N_B, num_pairs)
        elif method == 'mi':
            # Compute the four combinations.
            # p(A=1, B=1)
            p_11 = (N_AB + 0.25) / (N + 1)
            p_A1 = (N_A + 0.5) / (N + 1)
            p_B1 = (N_B + 0.5) / (N + 1)
            sim_score = p_11 * math.log(p_11 / p_A1 / p_B1, 2)
            # p(A=1, B=0)
            p_10 = (N_A - N_AB + 0.25) / (N + 1)
            p_B0 = 1 - p_B1
            sim_score += p_10 * math.log(p_10 / p_A1 / p_B0, 2)
            # p(A=0, B=1)
            p_01 = (N_B - N_AB + 0.25) / (N + 1)
            p_A0 = 1 - p_A1
            sim_score += p_01 * math.log(p_01 / p_A0 / p_B1, 2)
            # p(A=0, B=0)
            p_00 = (N - N_A - N_B + N_AB + 0.25) / (N + 1)
            sim_score += p_00 * math.log(p_00 / p_A0 / p_B0, 2)
        herb_symp_sim_dct[(node_a, node_b)] = sim_score

    hssd = sorted(herb_symp_sim_dct.items(), key=lambda x: x[1], reverse=True)
    
    out = open('./results/HIS_herb_symp_%s.txt' % method, 'w')
    for (node_a, node_b), sim_score in hssd:
        out.write('%s\t%s\t%f\n' % (node_a, node_b, sim_score))
    out.close()