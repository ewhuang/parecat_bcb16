### Author: Edward Huang

import file_operations

### This script takes the patient records and stems the herbs and symptoms
### such that the resulting elements are all in the herb-symptom dictionary.

def stem_word(dictionary_words, record_word):
    '''
    Compares a word from the patient record to a word from the herb-symptom
    dictionary. If one is the substring of the other, then return the dictionary
    word. Otherwise, return the empty string.
    '''
    # Make a list, since a non-stemmed symptom might have multiple dictionary
    # symptoms contained.
    if record_word in dictionary_words:
        return [record_word]
    stem_list = []
    for dictionary_word in dictionary_words:
        if dictionary_word in record_word or record_word in dictionary_word:
            stem_list += [dictionary_word]
    return stem_list

def stem_patient_records(patient_dct, dictionary_herbs, dictionary_symptoms):
    '''
    Takes as input the patient record dictionary and the list of herbs and
    symptoms in the herb-symptom dictionary, then stems the records so that they
    only contain words form the herb-symptom dictionary.
    '''
    stemmed_patient_dct = {}
    for key in patient_dct:
        # Initialize a patient for the current patient.
        stemmed_patient_dct[key] = []
        patient_visit_list = patient_dct[key]
        for patient_visit in patient_visit_list:
            diseases, diagnosis_date, symptoms, herbs = patient_visit
            # Stem the herbs, and then stem the symptoms.
            visit_stemmed_herbs = []
            for herb in herbs:
                stemmed_herb_list = stem_word(dictionary_herbs, herb)
                visit_stemmed_herbs += stemmed_herb_list
            if visit_stemmed_herbs == []:
                continue

            visit_stemmed_symptoms = []
            for symptom in symptoms:
                stemmed_symptom_list = stem_word(dictionary_symptoms, symptom)
                visit_stemmed_symptoms += stemmed_symptom_list
            if visit_stemmed_symptoms == []:
                continue
            stemmed_patient_dct[key] += [(diseases, diagnosis_date,
                visit_stemmed_symptoms, visit_stemmed_herbs)]
    return stemmed_patient_dct

def write_patient_dct(patient_dct):
    out = open('./data/stemmed_patient_records.txt', 'w')
    for key in patient_dct:
        name, dob = key

        patient_visit_list = patient_dct[key]
        for patient_visit in patient_visit_list:
            diseases, diagnosis_date, symptoms, herbs = patient_visit

            out.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (','.join(diseases), name,
                dob, diagnosis_date, ','.join(symptoms), ','.join(herbs)))

    out.close()

def main():
    # Call the herb symptom dictionary.
    herb_symptom_dct = file_operations.get_medicine_dictionary_file()
    dictionary_herbs = list(set(herb_symptom_dct.keys()))
    # List of lists. We flatten this list.
    ds = herb_symptom_dct.values()
    dictionary_symptoms = set(list(
        [item for sublist in ds for item in sublist]))

    # Get the patient record dictionary, and stem it.
    patient_dct = file_operations.get_patient_dct()
    stemmed_patient_dct = stem_patient_records(patient_dct, dictionary_herbs,
        dictionary_symptoms)
    write_patient_dct(stemmed_patient_dct)

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))