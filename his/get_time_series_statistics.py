#!/usr/bin/python
# -*- coding: utf-8 -*-
### Author: Edward Huang

from discontinued_herbs import *
import math

### This script provides functions for retrieving basic statistics on the time
### series data. Writes out disease complications, side effects, treatments, and
### good symptoms.

# Input is list, outputs the index of the first '1'.
def get_first_one(vector):
    return vector.index('1')

# Input is list, outputs index of the last '1'.
def get_last_one(vector):
    return (len(vector) - 1) - vector[::-1].index('1')

# Input is two symptom vectors. Outputs true if second vector is a complication
# of the first. A symptom is a complication of another if one vector's first 1
# appears after the other's first 1, and everything is the same after that.
def is_complication(symptom_a_vec, symptom_b_vec):
    a_first_one = get_first_one(symptom_a_vec)
    b_first_one = get_first_one(symptom_b_vec)
    # Second vector must first appear after the first vector.
    if b_first_one <= a_first_one:
        return False
    # Loop through the remaining visits.
    return symptom_a_vec[b_first_one:] == symptom_b_vec[b_first_one:]

# Input is an herb vector and a symptom vector. The symptom vector must not be a
# complication for another symptom. Herb's first one appears before symptom's
# first one means that the herb might have caused the symptom as a side effect.
def is_side_effect(herb_vec, symptom_vec):
    herb_first_one = get_first_one(herb_vec)
    symptom_first_one = get_first_one(symptom_vec)
    return herb_first_one < symptom_first_one

# Input is an herb vector and a symptom vector. The herb vector treats the
# symptom vector if the herb's first one appears at the same time or after the
# symptom's first one. It is a failed treatment if the herb's last one is before
# the symptom's last one. Successful otherwise.
def is_treatment(herb_vec, symptom_vec):
    herb_first_one = get_first_one(herb_vec)
    symptom_first_one = get_first_one(symptom_vec)
    herb_last_one = get_last_one(herb_vec)
    symptom_last_one = get_last_one(symptom_vec)
    if herb_first_one < symptom_first_one:
        return False
    if herb_last_one < symptom_last_one:
        return 'failure'
    return 'success'

# Takes as input two vectors (for symptoms). Adds together all of the elements,
# but if one vector is longer than the other, then simply append the remaining
# elements onto the resulting list.
def combine_vectors(vec_lst):
    len_lst = [len(vec) for vec in vec_lst]
    longest_list_length = max(len_lst)
    for i, vec in enumerate(vec_lst):
        # Perform 0 augmentation as necessary.
        vec_lst[i] = [int(ele) for ele in vec]
        vec_len = len(vec)
        if vec_len < longest_list_length:
            diff = longest_list_length - vec_len
            vec_lst[i] += [0] * diff
    # Sum together the lists, element-wise.
    result = [0] * longest_list_length
    for vec in vec_lst:
        result = [result[i] + vec[i] for i in range(longest_list_length)]
    return result
    # return [ele / float(sum(result)) for ele in result]

# Consolidates the probability vectors for the symptoms.
def write_probabilities(element_vectors, key):
    element_probs = {}
    for element in element_vectors:
        # Skip elements that were only described for one patient.
        if len(element_vectors[element]) == 1:
            continue
        element_probs[element] = combine_vectors(element_vectors[element])

    complication_vectors = {}
    complication_probability_diff = {}
    for element in element_probs:
        element_vec = element_probs[element]
        if key == 'herb' and element_vec[0] != min(element_vec):
            continue
        # Last probability greater than the first.
        diff = element_vec[-1] - element_vec[0]
        if key == 'symptom' and diff <= 0:
            continue
        complication_vectors[element] = element_vec
        complication_probability_diff[element] = diff
    # Write out to file.
    sorted_complications = sorted(complication_probability_diff.items(),
        key=operator.itemgetter(1), reverse=True)
    if key == 'herb':
        fname = './results/potent_herbs.txt'
    elif key == 'symptom':
        fname = './results/improved_symptoms.txt'
    out = open(fname, 'w')
    out.write('%s\tvisit_probabilities\tdifference_last_first\n' % key)
    for element, prob_diff in sorted_complications:
        vector_string = map(str, complication_vectors[element])
        vector_string = '[%s]' % (', '.join(vector_string))
        if len(complication_vectors[element]) <= 3:
             continue
        out.write('%s\t%s\t%g\n' % (element, vector_string, prob_diff))
    out.close()

def main():
    # Keys are pairs of symptom-herbs or herb-herbs. Values are counts of these
    # relationships.
    # complication_dct = {}
    side_effect_dct = {}
    successful_treatment_dct = {}
    failed_treatment_dct = {}
    herb_counts = {}
    symptom_counts = {}
    # Keys are symptoms, values are sums of time series across all patient
    # visits.
    symptom_vectors = {}
    herb_vectors = {}
    # Initialize patient visits.
    patient_dct = get_patient_dct()
    for name, dob in patient_dct:
        # Skip patients that only have one visit.
        if len(patient_dct[(name, dob)]) == 1:
            continue
        symptoms, herbs = parse_patient(patient_dct[(name, dob)])
        if (False not in [vector == [] for vector in symptoms] or
            False not in [vector == [] for vector in herbs]):
            continue

        symptom_occurrence_dct = get_occurrence_dct(symptoms)
        herb_occurrence_dct = get_occurrence_dct(herbs)

        # _________DISEASE COMPLICATIONS________
        # # Keep track of disease complications. These symptoms cannot be the
        # # symptoms in side effect relationships.
        # disease_complications = set([])
        # # First find the disease complications.
        # for symptom_a in symptom_occurrence_dct:
        #     symptom_a_vec = symptom_occurrence_dct[symptom_a]
        #     for symptom_b in symptom_occurrence_dct:
        #         symptom_b_vec = symptom_occurrence_dct[symptom_b]
        #         key = (symptom_a_vec, symptom_b_vec)
        #         if is_complication(symptom_a_vec, symptom_b_vec):
        #             key = (symptom_a, symptom_b)
        #             if key in complication_dct:
        #                 complication_dct[key] += 1
        #             else:
        #                 complication_dct[key] = 1
        #             disease_complications.add(symptom_b)

        # _________SIDE EFFECTS AND TREATMENTS________
        for symptom in symptom_occurrence_dct:
            # Increment symptom appearances.
            if symptom not in symptom_counts:
                symptom_counts[symptom] = 1
            else:
                symptom_counts[symptom] += 1
            # # Don't consider symptoms that are disease complications.
            # if symptom in disease_complications:
            #     continue
            symptom_vec = symptom_occurrence_dct[symptom]
            # Symptom probability bookkeeping.
            if symptom not in symptom_vectors:
                symptom_vectors[symptom] = [symptom_vec]
            else:
                symptom_vectors[symptom] += [symptom_vec]
            for herb in herb_occurrence_dct:
                herb_vec = herb_occurrence_dct[herb]
                key = (herb, symptom)
                if is_side_effect(herb_vec, symptom_vec):
                    if key in side_effect_dct:
                        side_effect_dct[key] += 1
                    else:
                        side_effect_dct[key] = 1
                # Check if the herb is meant to treat the symptom.
                is_treated = is_treatment(herb_vec, symptom_vec)
                if is_treated == False:
                    continue
                elif is_treated == 'success':
                    if key in successful_treatment_dct:
                        successful_treatment_dct[key] += 1
                    else:
                        successful_treatment_dct[key] = 1
                elif is_treated == 'failure':
                    if key in failed_treatment_dct:
                        failed_treatment_dct[key] += 1
                    else:
                        failed_treatment_dct[key] = 1

        # Increment herb appearances.
        for herb in herb_occurrence_dct:
            if herb not in herb_counts:
                herb_counts[herb] = 1
            else:
                herb_counts[herb] += 1
            herb_vec = herb_occurrence_dct[herb]
            # Symptom probability bookkeeping.
            if herb not in herb_vectors:
                herb_vectors[herb] = [herb_vec]
            else:
                herb_vectors[herb] += [herb_vec]

    # # Normalize the complication counts.
    # normalized_complication_dct = {}
    # for (symptom_a, symptom_b) in complication_dct:
    #     symptom_a_count = float(symptom_counts[symptom_a])
    #     symptom_b_count = float(symptom_counts[symptom_b])
    #     normalized_complication_dct[(symptom_a, symptom_b)] = complication_dct[(
    #         symptom_a, symptom_b)] / math.sqrt(symptom_a_count *
    #         symptom_b_count)

    # # Write out disease complications.
    # sorted_complications = sorted(normalized_complication_dct.items(),
    #     key=operator.itemgetter(1), reverse=True)
    # out = open('./results/disease_complications.txt', 'w')
    # out.write('original\toriginal_count\tcomplication\tcomplication_count\
    #     \tnormalized_count\n')
    # for (symptom_a, symptom_b), normalized_count in sorted_complications:
    #     if complication_dct[(symptom_a, symptom_b)] < 5:
    #         continue
    #     out.write('%s\t%d\t%s\t%d\t%f\n' % (symptom_a,
    #         symptom_counts[symptom_a], symptom_b, symptom_counts[symptom_b],
    #         normalized_count))
    # out.close()

    # Normalize the side effect counts.
    normalized_side_effect_dct = {}
    for (herb, symptom) in side_effect_dct:
        herb_count = float(herb_counts[herb])
        symptom_count = float(symptom_counts[symptom])
        normalized_side_effect_dct[(herb, symptom)] = side_effect_dct[(herb,
            symptom)] / math.sqrt(herb_count * symptom_count)

    # Write out herb side effects.
    sorted_side_effects = sorted(normalized_side_effect_dct.items(),
        key=operator.itemgetter(1), reverse=True)
    out = open('./results/side_effects.txt', 'w')
    out.write('herb\therb_count\tsymptom\tsymptom_count\tnormalized_count\n')
    for (herb, symptom), normalized_count in sorted_side_effects:
        if side_effect_dct[(herb, symptom)] < 5:
            continue
        out.write('%s\t%d\t%s\t%d\t%f\n' % (herb, herb_counts[herb], symptom,
            symptom_counts[symptom], normalized_count))
    out.close()

    # Sort by successes - failures.
    success_minus_failure_dct = {}
    for key in successful_treatment_dct:
        herb, symptom = key
        difference = successful_treatment_dct[key]
        if key in failed_treatment_dct:
            difference -= failed_treatment_dct[key]
        herb_count = float(herb_counts[herb])
        symptom_count = float(symptom_counts[symptom])
        # Normalize counts.
        denom = math.sqrt(herb_count * symptom_count)
        success_minus_failure_dct[key] = difference / denom
    # Write out treatment successes and failures.
    sorted_treatments = sorted(success_minus_failure_dct.items(),
        key=operator.itemgetter(1), reverse=True)
    out = open('./results/herb_treatments_successes_and_failures.txt', 'w')
    # Write header line.
    out.write('herb\therb_count\tsymptom\tsymptom_count\tsuccess_count\t')
    out.write('failure_count\tdifference/sqrt(hc*sc)\n')
    for (herb, symptom), count in sorted_treatments:
        success_count = successful_treatment_dct[(herb, symptom)]
        if success_count < 5:
            continue
        failure_count = 0
        if (herb, symptom) in failed_treatment_dct:
            failure_count = failed_treatment_dct[(herb, symptom)]
        out.write('%s\t%d\t%s\t%d\t%d\t%d\t%f\n' % (herb, herb_counts[herb],
            symptom, symptom_counts[symptom], success_count, failure_count,
            count))
    out.close()

    write_probabilities(symptom_vectors, 'symptom')
    write_probabilities(herb_vectors, 'herb')

if __name__ == '__main__':
    main()
