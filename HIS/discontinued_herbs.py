#!/usr/bin/python
# -*- coding: utf-8 -*-

### Author: Edward Huang

import itertools
import operator

### This script looks at a patient and gets a timeline for his medical history.
### We can see, for each patient, his set of symptoms and herbs. So, if a
### symptom no longer occurs, we want to see what herbs are also removed.

def get_patient_dct():
    # A patient key is given by both the fake name and the date of birth.
    patient_dct = {}
    f = open('./data/HIS_tuple_word.txt', 'r')
    for i, line in enumerate(f):
        diseases, name, dob, diagnosis_date, symptoms, herbs = line.split('\t')
        # Always ends with a colon, so the last element of the split will be
        # the empty string.
        diseases = diseases.split(':')[:-1]
        diagnosis_date = diagnosis_date.split('，')[1][:len('xxxx-xx-xx')]
        symptoms = symptoms.split(':')[:-1]
        herbs = herbs.split(':')[:-1]
        # Add the listing to the dictionary.
        key, value = (name, dob), [diseases, diagnosis_date, symptoms, herbs]
        if key in patient_dct:
            patient_dct[key] += [value]
        else:
            patient_dct[key] = [value]
    f.close()
    return patient_dct

# Returns True if date_1 is earlier than date_2.
def earlier_date(date_1, date_2):
    date_1 = date_1.split('-')
    date_2 = date_2.split('-')
    for i in range(len(date_1)):
        if int(date_2[i]) < int(date_1[i]):
            return False
    return True

# Takes a patient record, and returns the symptom records and herb records.
def parse_patient(patient_vectors):
    assert len(patient_vectors) > 1
    symptom_vectors = []
    herb_vectors = []
    for vector in patient_vectors:
        diseases, diagnosis_date, symptoms, herbs = vector
        symptom_vectors += [symptoms]
        herb_vectors += [herbs]
    return symptom_vectors, herb_vectors

# Get the dictionary of unique symptoms and herbs for each patient, with values
# being lists of 0's or 1's. 0's correspond to an herb not appearing in that
# visit, and 1's correspond to an herb appearing in the visit. Same thing for
# symptoms. Elements can be either herbs or symptoms.
def get_occurrence_dct(elements):
    # First, get the set of unique symptoms and herbs.
    element_occurrence_dct = {}
    for curr_visit_elements in elements:
        for element in curr_visit_elements:
            element_occurrence_dct[element] = []

    # Run through the vectors a second time and record appearances.
    for curr_visit_elements in elements:
        for element in element_occurrence_dct:
            if element in curr_visit_elements:
                element_occurrence_dct[element] += ['1']
            else:
                element_occurrence_dct[element] += ['0']
    return element_occurrence_dct

# This function takes an herb vector of 1's and 0's as input, and determines if
# the herb has been discontinued, i.e. ends with 0's.
def is_discontinued(vec):
    return vec[-1] == '0' and vec[-2] == '0'
def get_last_one(vector):
    return (len(vector) - 1) - vector[::-1].index('1')

# Increment a key in a dictionary by value. If it doesn't exist, initialize to
# value.
def dict_increment(dct, key, value):
    if key in dct:
        dct[key] += value
    else:
        dct[key] = value

# If an element is discontinued, figure out when it stopped occurring.
def add_discontinued(dct, element, vector):
    if is_discontinued(vector):
        last_one = get_last_one(vector)
        dict_increment(dct, last_one, [element])

# Write the results out to file.
def write_successful_herb_symptom_pairs(success_count, failure_count,
    herb_appearances, symptom_appearances):
    sorted_x = sorted(success_count.items(), key=operator.itemgetter(1),
        reverse=True)
    out = open('./results/successful_discontinued_herb_symptom_pairs.txt', 'w')
    out.write('herb\therb_count\tsymptom\tsymptom_count\tsuccesses\tfailures\n')
    for (herb, symptom), count in sorted_x:
        out.write('%s\t%d\t%s\t%d\t%d\t%d\n' % (herb,
            herb_appearances.count(herb), symptom,
            symptom_appearances.count(symptom), count, failure_count[(herb,
                symptom)]))
    out.close()

def main():
    success_count, failure_count = {}, {}
    herb_appearances, symptom_appearances = [], []

    patient_dct = get_patient_dct()
    out = open('./results/patient_symptom_and_herb_changes.txt', 'w')
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

        # Keys are indices of last 1's, and values are lists of herbs.
        discontinued_herbs = {}
        for herb in herb_occurrence_dct:
            herb_vec = herb_occurrence_dct[herb]
            out.write(herb + '\t' + '\t'.join(herb_vec) + '\n')
            herb_appearances += [herb]
            add_discontinued(discontinued_herbs, herb, herb_vec)

        discontinued_symptoms = {}
        for symptom in symptom_occurrence_dct:
            symptom_vec = symptom_occurrence_dct[symptom]
            out.write(symptom + '\t' + '\t'.join(symptom_vec) + '\n')
            symptom_appearances += [symptom]
            add_discontinued(discontinued_symptoms, symptom, symptom_vec)
        out.write('\n')

        # Match discontinued herbs with symptoms.
        for last_one in discontinued_herbs:
            if last_one not in discontinued_symptoms:
                continue
            discontinued_herb_symptom = ([discontinued_herbs[last_one]] +
                [discontinued_symptoms[last_one]])
            # Get every possible matching between a discontinued herb and a 
            # discontinued symptom.
            for pair in list(itertools.product(*discontinued_herb_symptom)):
                herb, symptom = pair
                # if (herb_occurrence_dct[herb].index('1') ==
                    # symptom_occurrence_dct[symptom].index('1')):
                if herb_occurrence_dct[herb] == symptom_occurrence_dct[symptom]:
                    dict_increment(success_count, pair, 1)
                    if pair not in failure_count:
                        failure_count[pair] = 0
                else:
                    dict_increment(failure_count, pair, 1)
    out.close()

    write_successful_herb_symptom_pairs(success_count, failure_count,
        herb_appearances, symptom_appearances)


if __name__ == '__main__':
    main()
