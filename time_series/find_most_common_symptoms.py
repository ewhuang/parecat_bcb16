

### Author: Edward Huang

import operator

### This script finds the most common symptoms across the the patient records.

def read_stemmed_records():
    '''
    Keys are (name, dob) pairs, and values are lists of visits.
    '''
    patient_record_dct = {}
    f = open('./data/stemmed_patient_records.txt', 'r')
    for i, line in enumerate(f):
        diseases, name, dob, visit_date, symptoms, herbs = line.split('\t')
        symptoms = symptoms.split(',')
        key = (name, dob)
        if key in patient_record_dct:
            patient_record_dct[key] = patient_record_dct[key].union(symptoms)
        else:
            patient_record_dct[key] = set(symptoms)
    f.close()
    return patient_record_dct

def get_symptom_count_dct(patient_record_dct):
    symptom_count_dct = {}
    for key in patient_record_dct:
        symptom_set = patient_record_dct[key]
        for symptom in symptom_set:
            if symptom in symptom_count_dct:
                symptom_count_dct[symptom] += 1
            else:
                symptom_count_dct[symptom] = 1
    sorted_x = sorted(symptom_count_dct.items(), key=operator.itemgetter(1),
        reverse=True)
    return sorted_x

def main():
    patient_record_dct = read_stemmed_records()
    symptom_count_dct = get_symptom_count_dct(patient_record_dct)

    out = open('./results/symptom_counts.txt', 'w')
    for symptom, count in symptom_count_dct:
        out.write('%s\t%d\n' % (symptom, count))
    out.close()


if __name__ == '__main__':
    main()