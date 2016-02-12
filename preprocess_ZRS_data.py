#!/usr/bin/python
# -*- coding: utf-8 -*-

### Author: Edward Huang

### Export the excel file to html, then copy the html (not source) to a text 
### file to begin.

import re
from collections import OrderedDict

period = '。'
comma = '，'

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

if __name__ == '__main__':
    f = open('./data/ZRS_symptoms.txt', 'r')
    symptom_text = f.readlines()
    f.close()

    id_symptoms_lst = []
    prev_id = ''
    prev_symptom = ''
    for entity in symptom_text:
        entity = entity.strip()
        if entity == '':
            continue
        if entity.isdigit():
            if prev_id != '':
                id_symptoms_lst += [(prev_id, prev_symptom)]
                prev_symptom = ''
            prev_id = entity
        else:
            prev_symptom += entity
    id_symptoms_lst += [(prev_id, prev_symptom)]

    out = open('./data/ZRS_patient_symptoms.txt', 'w')
    for patient_id, symptoms in id_symptoms_lst:
        print patient_id
        symptoms = symptoms.replace(comma, ',')
        symptoms = symptoms.replace(period, '')
        non_numeric_symptoms = []
        for symptom in symptoms.split(','):
            if not hasNumbers(symptom):
                non_numeric_symptoms += [symptom]
        out.write(patient_id + '\t')
        out.write('\t'.join(non_numeric_symptoms))
        out.write('\n')
    out.close()