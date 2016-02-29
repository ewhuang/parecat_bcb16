#!/usr/bin/python
# -*- coding: utf-8 -*-

### Author: Edward Huang

import math
import operator
import sys
from itertools import starmap, izip

### This script takes mined topics from herbs and symptoms, and computes the 
### KL-divergence between every herb-symptom pair. It normalizes each column
### of a transaction to sum to 1, as each row is originally summed to 1 (they
### are probabilities).

TOPIC_NUM = 11
SMOOTH_VAL = 0
NUM_TOPICS = 100

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

def dot_product(v1, v2):
    """                                                                                                     
    Uses a starmap (itertools) to apply the mul operator on an izipped (v1,v2)                           
    """
    assert len(v1) == len(v2)
    return sum(starmap(operator.mul, izip(v1, v2)))

# # This function reads a file (non-normalized) and gets all of the herbs or
# # symptoms that appear in the first line of that file. This is because the 
# # non-nomralized data is guaranteed to have every herb/symptom in each row.
# def get_items(element_type):
#     assert element_type in ['herb', 'symptom']
#     # Read in the line for herbs or symptoms.
#     largest_result_list = []
#     f = open('./data/%d_%s.topic%d' % (NUM_TOPICS, element_type, TOPIC_NUM), 'r')
#     for line in f:
#         curr_result_list = []
#         line = line.strip().split('\t')
#         for pair in line:
#             # Split by colon.
#             element, val = pair.split(':')
#             curr_result_list += [element]
#         if len(curr_result_list) > len(largest_result_list):
#             largest_result_list = curr_result_list[:]
#     f.close()
#     return largest_result_list

if __name__ == '__main__':
    norm = ''
    if len(sys.argv) == 2:
        norm = sys.argv[1] + '_'

    # # The normalized file does not have all the herbs and symptoms. Read them
    # # from the non-normalized files.
    # all_herbs = get_items('herb')
    # all_symps = get_items('symptom')

    # Keys are herbs/symptoms, values are lists of probabilities.
    herb_values = {}
    symp_values = {}

    # # Initialize the probabilities for each herb and symptom.
    # for herb in all_herbs:
    #     herb_values[herb] = []
    # for symp in all_symps:
    #     symp_values[symp] = []

    herb_f = open('./data/%d_%sherb.topic%d' % (
        NUM_TOPICS, norm, TOPIC_NUM), 'r')
    symp_f = open('./data/%d_%ssymptom.topic%d' % (
        NUM_TOPICS, norm, TOPIC_NUM), 'r')

    line_counter = 0
    while True:
        herb_line = herb_f.readline()
        symp_line = symp_f.readline()

        if herb_line == '' or symp_line == '':
            assert herb_line == '' and symp_line == ''
            assert line_counter == NUM_TOPICS
            break

        hl = herb_line.strip().split('\t')
        sl = symp_line.strip().split('\t')

        # # Keep track of all the herbs and symptoms we have in each row.
        # curr_herbs = all_herbs[:]
        # curr_symps = all_symps[:]

        # Read in the line for herbs.
        for pair in hl:
            # Split by colon.
            herb, val = pair.split(':')
            # If first time seeing herb, initialize list to NUM_TOPICS number of
            # smoothing values.
            if herb not in herb_values:
                herb_values[herb] = [SMOOTH_VAL] * NUM_TOPICS
            # Maintain the list of values for each herb.
            val = float(val)
            if herb_values[herb][line_counter] != SMOOTH_VAL:
                herb_values[herb][line_counter] += val
            else:
                herb_values[herb][line_counter] = val

        # Read in the line for symptoms.
        for pair in sl:
            # Split by colon.
            symp, val = pair.split(':')
            # If first time seeing symp, initialize list to NUM_TOPICS number of
            # smoothing values.
            if symp not in symp_values:
                symp_values[symp] = [SMOOTH_VAL] * NUM_TOPICS
            # Maintain the list of values for each symp.
            val = float(val)
            if symp_values[symp][line_counter] != SMOOTH_VAL:
                symp_values[symp][line_counter] += val
            else:
                symp_values[symp][line_counter] = val

        # If we have any symptoms or herbs left over, then we fill it in with
        # # 1e-05.
        # for herb in curr_herbs:
        #     herb_values[herb] += [SMOOTH_VAL]
        # for symp in curr_symps:
        #     symp_values[symp] += [SMOOTH_VAL]

        line_counter += 1

    symp_f.close()
    herb_f.close()

    # Don't normalize for dot product.
    # # Normalize the probabilities for each herb and symptom to sum to 1.
    # for herb in herb_values:
    #     probs = herb_values[herb]
    #     assert len(probs) == NUM_TOPICS
    #     total_prob = sum(probs)
    #     herb_values[herb] = [i / total_prob for i in probs]

    # for symp in symp_values:
    #     probs = symp_values[symp]
    #     # if len(probs) != NUM_TOPICS:
    #     #     # We might have 200 probabilities because of parsing issues.
    #     #     assert len(probs) == NUM_TOPICS * 2
    #     #     # If we have 200 probabilities, then we must add up every other
    #     #     # probability.
    #     #     probs = [probs[i] + probs[i + 1] for i in range(0, len(
    #     #         probs), 2)]
    #     assert len(probs) == NUM_TOPICS
    #     total_prob = sum(probs)
    #     symp_values[symp] = [i / total_prob for i in probs]

    # Now, compute get the dot product.
    dot_dct = {}
    for herb in herb_values:
        hv = herb_values[herb]
        for symp in symp_values:
            sv = symp_values[symp]
            dot_dct[(herb, symp)] = dot_product(hv, sv)

    # Writing out to file.
    dot_dct = sorted(dot_dct.items(), key=lambda x: x[1], reverse=True)
    out = open('./results/%d_%sdot.topic%d' % (
        NUM_TOPICS, norm, TOPIC_NUM), 'w')
    for (herb, symp), dp in dot_dct:
        out.write('%s\t%s\t%f\n' % (herb, symp, dp))
    out.close()

    # # Now, compute the KL-divergence between every herb-symptom pair.
    # # Formula: D_KL(P||Q) = sum of P(i) * log(P(i) / Q(i)) for all i.
    # kl_div_dct = {}
    # for herb in herb_values:
    #     hv = herb_values[herb]
    #     for symp in symp_values:
    #         sv = symp_values[symp]
    #         assert len(hv) == len(sv)
    #         kl_div = 0.0
    #         for i in range(len(hv)):
    #             svi = sv[i]
    #             kl_div += svi * math.log(svi / hv[i], math.e)
    #         kl_div_dct[(herb, symp)] = kl_div

    # # Retrieve the inverted index, with values converted to counts.
    # sym_dct = {}
    # f = open('./data/sym_dct.txt', 'r')
    # for line in f:
    #     line = line.strip().split('\t')
    #     sym_dct[line[0]] = float(line[1])
    # f.close()

    # herb_dct = {}
    # f = open('./data/herb_dct.txt', 'r')
    # for line in f:
    #     line = line.strip().split('\t')
    #     herb_dct[line[0]] = float(line[1])
    # f.close()

    # Writing out to file.
    # kl_div_dct = sorted(kl_div_dct.items(), key=lambda x: x[1])
    # out = open('./results/100_%skl_div.topic%d' % (norm, TOPIC_NUM), 'w')
    # for (herb, symp), kl in kl_div_dct:
    #     # Add frequency to kl-divergence.
    #     # val = kl + herb_dct[herb] + sym_dct[symp]
    #     out.write('%s\t%s\t%f\n' % (herb, symp, kl))
    # out.close()

    # # Checks cosine similarity between every pair of symptoms.
    # for symp1 in symp_values:
    #     symp1v = symp_values[symp1]
    #     for symp2 in symp_values:
    #         symp2v = symp_values[symp2]
    #         if cosine_similarity(symp1v, symp2v) < 0.9:
    #             print symp1, symp2