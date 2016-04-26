### Author: Edward Huang

from sklearn.cluster import KMeans
from sklearn.metrics.cluster import adjusted_rand_score
import random

### This script puts together the medical records data and clusters on them,
### evaluating based on the ground truth labels.

def read_medical_data(file_num):
    symptom_herb_set = set([])
    patient_dct = {}
    f = open('./data/medical_data_%d.txt' % file_num, 'r')
    for i, line in enumerate(f):
        symptoms, herbs, patient_id, section, subsection = line.split('\t')
        # Add symptoms and herbs.
        symptoms = symptoms.split(',')
        symptom_herb_set = symptom_herb_set.union(symptoms)
        # herbs = herbs.split(',')
        # symptom_herb_set = symptom_herb_set.union(herbs)
        # Add each patient ID transaction.
        if (patient_id, section, subsection) in patient_dct:
            # patient_dct[(patient_id, section, subsection)] += symptoms + herbs
            patient_dct[(patient_id, section, subsection)] += symptoms
            # patient_dct[(patient_id, section, subsection)] += herbs
        else:
            # patient_dct[(patient_id, section, subsection)] = symptoms + herbs
            patient_dct[(patient_id, section, subsection)] = symptoms
            # patient_dct[(patient_id, section, subsection)] = herbs
    f.close()
    return symptom_herb_set, patient_dct

def main():
    feature_vectors = []
    section_labels = []
    subsection_labels = []
    all_symptom_herb_vector = set([])
    patient_dcts = []
    for i in [1, 2, 3]:
        symptom_herb_set, patient_dct = read_medical_data(i)
        # Concatenate all of the symptoms and herbs.
        all_symptom_herb_vector = all_symptom_herb_vector.union(
            symptom_herb_set)
        patient_dcts += [patient_dct]

    # Each patient has a feature vector.
    for patient_dct in patient_dcts:
        for (patient_id, section, subsection) in patient_dct:
            feature_vector = []
            patient_herbs_and_symptoms = patient_dct[(patient_id, section,
                subsection)]
            for element in all_symptom_herb_vector:
                feature_vector += [patient_herbs_and_symptoms.count(element)]
            # Add the current patient vector and labels.
            feature_vectors += [feature_vector]
            section_labels += [section]
            subsection_labels += [subsection]
    # out.close()

    all_sections = list(set(section_labels))
    true_labels = []
    for label in section_labels:
        true_labels += [all_sections.index(label)]

    num_clusters = len(all_sections)
    random_state = 170
    y_pred = KMeans(n_clusters=num_clusters,
        random_state=random_state).fit_predict(feature_vectors)
    print adjusted_rand_score(true_labels, y_pred)
    # 0.00257750924311, symptom + herb features
    # Symptoms: -0.0023638
    # Herbs: 0.01508

    # # Random clustering.
    # rand_score_sum = []
    # for i in range(1000):
    #     random_labels = []
    #     for i in range(len(section_labels)):
    #         random_labels += [random.choice(range(num_clusters))]
    #     rand_score_sum += [adjusted_rand_score(section_labels, random_labels)]
    # print float(sum(rand_score_sum)) / len(rand_score_sum)
    # # -1.06003e-05

if __name__ == '__main__':
    main()