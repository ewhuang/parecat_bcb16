#!/usr/bin/python
# -*- coding: utf-8 -*-

### Author: Edward Huang

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


def main():
    out = open('./results/patient_symptom_and_herb_changes.txt', 'w')
    patient_dct = get_patient_dct()
    for name, dob in patient_dct:
        if len(patient_dct[(name, dob)]) == 1:
            continue
        symptoms, herbs = parse_patient(patient_dct[(name, dob)])
        if (False not in [vector == [] for vector in symptoms] or
            False not in [vector == [] for vector in herbs]):
            continue

        symptom_occurrence_dct = get_occurrence_dct(symptoms)
        herb_occurrence_dct = get_occurrence_dct(herbs)

        for symptom in symptom_occurrence_dct:
            out.write(symptom + '\t')
            out.write('\t'.join(symptom_occurrence_dct[symptom]) + '\n')
        for herb in herb_occurrence_dct:
            out.write(herb + '\t')
            out.write('\t'.join(herb_occurrence_dct[herb]) + '\n')
        out.write('\n')
    out.close()

if __name__ == '__main__':
    main()
