#!/usr/bin/python
# -*- coding: utf-8 -*-

### Author: Edward Huang

import math
import operator
import sys

### This script takes mined topics from herbs and symptoms, and computes the 
### KL-divergence between every herb-symptom pair. It normalizes each column
### of a transaction to sum to 1, as each row is originally summed to 1 (they
### are probabilities).

TOPIC_NUM = 2
SMOOTH_VAL = 1e-05

# Computes cosine similarity between two lists of floats.
def cosine_similarity(v1,v2):
    "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
    sumxx, sumxy, sumyy = 0, 0, 0
    for i in range(len(v1)):
        x = v1[i]; y = v2[i]
        sumxx += x*x
        sumyy += y*y
        sumxy += x*y
    return sumxy/math.sqrt(sumxx*sumyy)

# This function reads a file (non-normalized) and gets all of the herbs or
# symptoms that appear in the first line of that file. This is because the 
# non-nomralized data is guaranteed to have every herb/symptom in each row.
def get_items(element_type):
    assert element_type in ['herb', 'symptom']
    f = open('./data/100_%s.topic%d' % (element_type, TOPIC_NUM), 'r')
    # Read in a single line, and analyze it.
    line = f.readline().strip().split('\t')
    # Read in the line for herbs or symptoms.
    result_list = []
    for pair in line:
        # Split by colon.
        herb, val = pair.split(':')
        result_list += [herb]
    f.close()
    return result_list

if __name__ == '__main__':
    norm = ''
    if len(sys.argv) == 2:
        norm = sys.argv[1] + '_'

    # The normalized file does not have all the herbs and symptoms. Read them
    # from the non-normalized files.
    all_herbs = get_items('herb')
    all_symps = get_items('symptom')

    # Keys are herbs/symptoms, values are lists of probabilities.
    herb_values = {}
    symp_values = {}

    # Initialize the probabilities for each herb and symptom.
    for herb in all_herbs:
        herb_values[herb] = []
    for symp in all_symps:
        symp_values[symp] = []

    herb_f = open('./data/100_%sherb.topic%d' % (norm, TOPIC_NUM), 'r')
    symp_f = open('./data/100_%ssymptom.topic%d' % (norm, TOPIC_NUM), 'r')

    while True:
        herb_line = herb_f.readline()
        symp_line = symp_f.readline()

        if herb_line == '' or symp_line == '':
            assert herb_line == '' and symp_line == ''
            break

        hl = herb_line.strip().split('\t')
        sl = symp_line.strip().split('\t')

        # Keep track of all the herbs and symptoms we have in each row.
        curr_herbs = all_herbs[:]
        curr_symps = all_symps[:]
        # Read in the line for herbs.
        for pair in hl:
            # Split by colon.
            herb, val = pair.split(':')
            # Maintain the list of values for each herb.
            herb_values[herb] += [float(val)]
            curr_herbs.remove(herb)

        # Read in the line for symptoms.
        for pair in sl:
            # Split by colon.
            symp, val = pair.split(':')
            # Maintain the list of values for each symptom.
            symp_values[symp] += [float(val)]
            curr_symps.remove(symp)

        # If we have any symptoms or herbs left over, then we fill it in with
        # 1e-05.
        for herb in curr_herbs:
            herb_values[herb] += [SMOOTH_VAL]
        for symp in curr_symps:
            symp_values[symp] += [SMOOTH_VAL]

    symp_f.close()
    herb_f.close()

    # Normalize the probabilities for each herb and symptom to sum to 1.
    for herb in herb_values:
        probs = herb_values[herb]
        total_prob = sum(probs)
        herb_values[herb] = [i / total_prob for i in probs]

    for symp in symp_values:
        probs = symp_values[symp]
        if len(probs) != 100:
            # We might have 200 probabilities because of parsing issues.
            assert len(probs) == 200
            # If we have 200 probabilities, then we must add up every other
            # probability.
            probs = [probs[i] + probs[i + 1] for i in range(0, len(
                probs), 2)]
            assert len(probs) == 100
        total_prob = sum(probs)
        symp_values[symp] = [i / total_prob for i in probs]

    # Now, compute the KL-divergence between every herb-symptom pair.
    # Formula: D_KL(P||Q) = sum of P(i) * log(P(i) / Q(i)) for all i.
    kl_div_dct = {}
    for herb in herb_values:
        hv = herb_values[herb]
        for symp in symp_values:
            sv = symp_values[symp]
            assert len(hv) == len(sv)
            kl_div = 0.0
            for i in range(len(hv)):
                svi = sv[i]
                kl_div += svi * math.log(svi / hv[i], math.e)
            kl_div_dct[(herb, symp)] = kl_div

    # Writing out to file.
    kl_div_dct = sorted(kl_div_dct.items(), key=lambda x: x[1])
    out = open('./results/100_%skl_div.topic%d' % (norm, TOPIC_NUM), 'w')
    for (herb, symp), val in kl_div_dct:
        out.write('%s\t%s\t%f\n' % (herb, symp, val))
    out.close()

    # # Checks cosine similarity between every pair of symptoms.
    # for symp1 in symp_values:
    #     symp1v = symp_values[symp1]
    #     for symp2 in symp_values:
    #         symp2v = symp_values[symp2]
    #         if cosine_similarity(symp1v, symp2v) < 0.9:
    #             print symp1, symp2