#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

### Author: Edward Huang

# Contains scripts for reading files.

# Determine if a string has numbers in it.
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

# Returns a dictionary where keys are patient ID's. The values are dictionaries.
# The internal dictionaries have keys herbs, symptoms, section, and subsection.
def get_patient_dictionary(fname):
    patient_dct = {}
    previous_line = ''
    current_patient_id = -1
    current_section, current_subsection = '', ''
    f = open(fname, 'r')
    for line in f:
        line = line.strip()
        # A new section is denoted by '第xxx章', where xxx is a number.
        if '第' in line and line.index('第') == 0 and '章' in line:
            current_section = line.split()[1]
        # A new subsection is denoted by '第xxx节', where xxx is a number.
        if '第' in line and line.index('第') == 0 and '节' in line:
            current_subsection = line[line.index('节') + len('节'):].strip()

        # A new patient is denoted by '初诊：'.
        if '初诊：' in line and line.index('初诊：') == 0:
            # Initialize the patient's visit list.
            current_patient_id += 1
            init_dct = ({'herbs' : [], 'symptoms' : [],
                'section' : current_section, 'subsection' : current_subsection})
            patient_dct[current_patient_id] = init_dct

        # If 'g' occrus multiple times in the current line, then it is an herb
        # vector.
        if line.count('g') > 2 and '诊' not in line and '年' not in line:
            patient_dct[current_patient_id]['herbs'] += [line.split('。')[0]]
            patient_dct[current_patient_id]['symptoms'] += [previous_line]
        previous_line = line[:]
    f.close()
    return patient_dct

# Cleans a list of herbs.
def get_clean_herb_list(herb_list):
    # Remove Chinese punctuation.
    herb_list = herb_list.replace('、', ',').replace('，', ',').replace('。', ',')
    herb_list = herb_list.split(',')
    clean_herb_list = []
    for herb in herb_list:
        # Skip herbs that do not have dosages.
        if 'g' not in herb:
            continue
        herb = herb[:herb.index('g')]
        if '（' in herb:
            herb = herb[:herb.index('（')]
        herb = ''.join([ch for ch in herb if not ch.isdigit() and ch != 'g'])
        clean_herb_list += [herb.strip('.')]
    return clean_herb_list

# Cleans a list of symptoms.
def get_clean_symptom_list(symptom_list):
    if '日）：' in symptom_list:
        symptom_list = symptom_list[symptom_list.index('日）：') + len('日）：'):]
    symptom_list = symptom_list.replace('、', ',').replace('，', ',').replace(
        '。', ',').replace('：', ',')
    symptom_list = symptom_list.split(',')
    clean_symptom_list = []
    for symptom in symptom_list:
        # Skip symptoms that have numerical descriptions.
        if hasNumbers(symptom) or symptom == '':
            continue
        clean_symptom_list += [symptom.strip('.')]
    return clean_symptom_list

# Clean the lists returned by the raw parsing.
def clean_data(fname):
    patient_dct = get_patient_dictionary(fname)
    for patient_id in patient_dct:
        # Cleaning the herbs.
        herb_lists = patient_dct[patient_id]['herbs']
        for i, herb_list in enumerate(herb_lists):
            herb_lists[i] = get_clean_herb_list(herb_list)
        patient_dct[patient_id]['herbs'] = herb_lists

        # Cleaning the symptoms.
        symptom_lists = patient_dct[patient_id]['symptoms']
        for i, symptom_list in enumerate(symptom_lists):
            symptom_lists[i] = get_clean_symptom_list(symptom_list)
        patient_dct[patient_id]['symptoms'] = symptom_lists
    return patient_dct

def write_out_files(run_num):
    patient_dct = clean_data('./data/raw_medical_cases_%d.txt' % run_num)
    out = open('./data/medical_data_%d.txt' % run_num, 'w')
    for patient_id in patient_dct:
        # Fetch the attributes for the current patient.
        patient_att = patient_dct[patient_id]
        symptom_lists = patient_att['symptoms']
        herb_lists = patient_att['herbs']
        assert len(symptom_lists) == len(herb_lists)
        section = patient_att['section']
        subsection = patient_att['subsection']

        for i in range(len(symptom_lists)):
            out.write(','.join(symptom_lists[i]) + '\t' +
                ','.join(herb_lists[i]) + '\t' + str(patient_id) + '\t' +
                section + '\t' + subsection + '\n')
    out.close()

for i in range(1, 4):
    write_out_files(i)