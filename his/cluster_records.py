### Author: Edward Huang

from sklearn.cluster import KMeans

### This script puts together the medical records data and clusters on them,
### evaluating based on the ground truth labels.

def read_medical_data(file_num):
    symptom_herb_set = set([])
    patient_dct = {}
    f = open('./data/medical_data_%d.txt' % file_num, 'r')
    for i, line in enumerate(f):
        if i > 10:
            continue
        symptoms, herbs, patient_id, section, subsection = line.split('\t')
        # Add symptoms and herbs.
        symptoms = symptoms.split(',')
        symptom_herb_set = symptom_herb_set.union(symptoms)
        herbs = herbs.split(',')
        symptom_herb_set = symptom_herb_set.union(herbs)
        # Add each patient ID transaction.
        if (patient_id, section, subsection) in patient_dct:
            patient_dct[(patient_id, section, subsection)] += symptoms + herbs
        else:
            patient_dct[(patient_id, section, subsection)] = symptoms + herbs
    f.close()
    return symptom_herb_set, patient_dct

def main():
    feature_vectors = []
    section_labels = []
    subsection_labels = []
    all_symptom_herb_vector = set([])
    patient_dcts = []
    # for i in [1, 2, 3]:
    for i in [1]:
        symptom_herb_set, patient_dct = read_medical_data(i)
        # Concatenate all of the symptoms and herbs.
        all_symptom_herb_vector = all_symptom_herb_vector.union(
            symptom_herb_set)
        patient_dcts += [patient_dct]
    # Each patient has a feature vector.
    # out = open('test.txt', 'w')
    # out.write(','.join(all_symptom_herb_vector) + '\n')

    for patient_dct in patient_dcts:
        for (patient_id, section, subsection) in patient_dct:
            feature_vector = []
            patient_herbs_and_symptoms = patient_dct[(patient_id, section,
                subsection)]
            for element in all_symptom_herb_vector:
                feature_vector += [patient_herbs_and_symptoms.count(element)]
            # out.write(','.join(patient_herbs_and_symptoms) + '\n')
            # out.write(','.join(map(str, feature_vector)))
            # Add the current patient vector and labels.
            feature_vectors += [feature_vector]
            section_labels += [section]
            subsection_labels += [subsection]
    # out.close()

    num_clusters = len(set(section_labels))
    random_state = 170
    y_pred = KMeans(n_clusters=num_clusters,
        random_state=random_state).fit_predict(feature_vectors)

if __name__ == '__main__':
    main()