### Author: Edward Huang

from collections import Counter
from datetime import datetime
import lifelines
import time

date_format = '%Y-%m-%d'

def read_stemmed_records():
    '''
    Keys are (name, dob) pairs, and values are lists of visits.
    '''
    patient_record_dct = {}
    f = open('./data/stemmed_patient_records.txt', 'r')
    for i, line in enumerate(f):
        ### TODO
        if i == 7:
            break
        diseases, name, dob, visit_date, symptoms, herbs = line.split('\t')
        key = (name, dob)
        if key in patient_record_dct:
            patient_record_dct[key] += [(diseases, visit_date, symptoms, herbs)]
        else:
            patient_record_dct[key] = [(diseases, visit_date, symptoms, herbs)]
    f.close()
    return patient_record_dct

def build_survival_model(patient_record):
    '''
    Given a patient record of multiple visits, this function creates an entity
    for each initial symptom, and determines if it "dies" or not, along with 
    the observation time.
    '''
    duration = 0
    prev_date = ''
    initial_symptoms = []

    for i, visit in enumerate(patient_record):
        diseases, visit_date, symptoms, herbs = visit
        diseases = diseases.split(',')
        symptoms = symptoms.split(',')
        herbs = herbs.split(',')

        # Keep track of the duration elapsed for each symptom.
        curr_date = datetime.strptime(visit_date, date_format)
        if i != 0:
            duration += (curr_date - prev_date).days
        else:
            initial_symptoms = symptoms
        prev_date = curr_date
        print duration



def main():
    patient_record_dct = read_stemmed_records()
    for key in patient_record_dct.keys():
        # Skip patients that do not have multiple visits.
        if len(patient_record_dct[key]) == 1:
            continue
        build_survival_model(patient_record_dct[key])
    
if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))