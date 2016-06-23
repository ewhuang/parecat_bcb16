#!/usr/bin/python
# -*- coding: utf-8 -*-

### Author: Edward Huang

from collections import Counter
import file_operations
import math
import operator

### This script reads the time series data and find the most frequent herbs,
### and the symptoms that correspond the most to these herbs.

def get_frequent_herbs(patient_dct):
    # One dictionary counting the herbs, one for the symptoms for each herb.
    herb_count_dct = {}
    herb_symptom_dct = {}
    symptom_count_dct = {}

    for key in patient_dct:
        patient_visit_list = patient_dct[key]
        for patient_visit in patient_visit_list:
            diseases, diagnosis_date, symptoms, herbs = patient_visit
            for herb in herbs:
                # Track the herb count for each herb.
                if herb not in herb_count_dct:
                    herb_count_dct[herb] = 1
                    herb_symptom_dct[herb] = symptoms[:]
                else:
                    herb_count_dct[herb] += 1
                    herb_symptom_dct[herb] += symptoms[:]
            for symptom in symptoms:
                if symptom not in symptom_count_dct:
                    symptom_count_dct[symptom] = 1
                else:
                    symptom_count_dct[symptom] += 1

    n = sum(symptom_count_dct.values()) + sum(herb_count_dct.values())
    # Get the most frequent herbs.
    frequent_herbs = sorted(herb_count_dct.items(), key=operator.itemgetter(1),
        reverse=True)[:100]
    # Get the top symptoms for each of the top herbs.
    out = open('./results/frequent_herbs_and_symptoms.txt', 'w')
    out.write('herb\tsymptoms\n')
    for herb, herb_count in frequent_herbs:
        # Keys are symptoms.
        co_occurrence_dct = Counter(herb_symptom_dct[herb])
        pmi_dct = {}
        for symptom in co_occurrence_dct:
            co_occurrence_count = co_occurrence_dct[symptom]
            symptom_count = symptom_count_dct[symptom]
            if symptom_count < 10:
                continue
            pmi_dct[symptom] = math.log(co_occurrence_count * n / 
                float(herb_count * symptom_count), math.e)

        frequent_symptoms = sorted(pmi_dct.items(),
            key=operator.itemgetter(1), reverse=True)[:100]
        # out.write(herb + ',' + str(herb_count) + '\t')
        out.write(herb + '\t')
        for symptom, pmi in frequent_symptoms:
            # out.write(symptom + ',' + str(co_occurrence_dct[symptom]) + ',' + str(symptom_count_dct[symptom]) + ',' + str(pmi) + '\t')
            out.write(symptom + ',' + str(pmi) + '\t')
        out.write('\n\n')
    out.close()
    
def main():
    patient_dct = file_operations.get_patient_dct()
    frequent_herbs = get_frequent_herbs(patient_dct)

if __name__ == '__main__':
    main()