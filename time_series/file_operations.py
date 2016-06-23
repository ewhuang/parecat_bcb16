#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import OrderedDict

def get_medicine_dictionary_file():
    '''
    Returns the dictionary produced by the file.
    Keys: herbs
    Values: lists of symptoms
    Also returns the list of all symptoms as a feature vector.
    '''

    # Keys are herbs, and values are the symptoms that the herbs treat.
    herb_symptom_dct = OrderedDict({})

    f = open('./data/herb_symptom_dictionary.txt', 'r')
    for i, line in enumerate(f):
        if i == 0:
            continue
        line = line.strip('\n').split('\t')

        line_length = len(line)
        # Some symptoms don't have good English translations.
        assert line_length == 2 or line_length == 5
        if line_length == 2:
            herb, symptom = line
        elif line_length == 5:
            herb, symptom, english_symptom, db_src, db_src_id = line

        # Add to the herb dictionary.
        if herb in herb_symptom_dct:
            if symptom not in herb_symptom_dct[herb]:
                herb_symptom_dct[herb] += [symptom]
        else:
            herb_symptom_dct[herb] = [symptom]

        # Add to the symptom dictionary.
        if symptom in herb_symptom_dct:
            if herb not in herb_symptom_dct[symptom]:
                herb_symptom_dct[symptom] += [herb]
        else:
            herb_symptom_dct[symptom] = [herb]

    f.close()

    return herb_symptom_dct

def get_patient_dct():
    '''
    Returns dictionary, where keys are (name, DOB) pairs and values are tuples
    containing the diseases, diagnosis dates, symptoms, and herbs of each visit.
    '''
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
        key, value = (name, dob), (diseases, diagnosis_date, symptoms, herbs)
        if key in patient_dct:
            patient_dct[key] += [value]
        else:
            patient_dct[key] = [value]
    f.close()
    return patient_dct