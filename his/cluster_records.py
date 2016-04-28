### Author: Edward Huang

from sklearn.cluster import KMeans
from sklearn.cluster import SpectralClustering
from sklearn.metrics.cluster import adjusted_rand_score
import random
import sys
import time

### This script puts together the medical records data and clusters on them,
### evaluating based on the ground truth labels.

def read_medical_data(file_num, vector_type):
    symptom_herb_list = []
    patient_dct = {}
    f = open('./data/medical_data_%d.txt' % file_num, 'r')
    for i, line in enumerate(f):
        symptoms, herbs, patient_id, section, subsection = line.split('\t')
        # Add symptoms and herbs.
        if vector_type == 'symptoms':
            symptoms = symptoms.split(',')
            herbs = []
            symptom_herb_list += symptoms
        elif vector_type == 'herbs':
            symptoms = []
            herbs = herbs.split(',')
            symptom_herb_list += herbs
        elif vector_type == 'both':
            symptoms = symptoms.split(',')
            herbs = herbs.split(',')
            symptom_herb_list += symptoms + herbs
        # Add each patient ID transaction.
        key = (patient_id, section, subsection)
        if key in patient_dct:
            patient_dct[key] += symptoms + herbs
        else:
            patient_dct[key] = symptoms + herbs
    f.close()
    return symptom_herb_list, patient_dct

# Returns a list of good elements (symptoms or herbs) via TF-IDF.
def tf_idf(symptom_herb_list, num_visits):
    symptom_herb_set = set(symptom_herb_list)
    good_symptom_herb_vector = []
    for element in symptom_herb_set:
        if 1 < symptom_herb_list.count(element) <= (num_visits * 0.5):
            good_symptom_herb_vector += [element]
    return good_symptom_herb_vector

def main():
    if len(sys.argv) != 2:
        print 'Usage: %s symptoms/herbs/both' % sys.argv[0]
        exit()
    vector_type = sys.argv[1]

    all_symptom_herb_list = []
    patient_dcts = []
    num_visits = 0
    for i in [1, 2, 3]:
        symptom_herb_list, patient_dct = read_medical_data(i, vector_type)
        # Concatenate all of the symptoms and herbs.
        all_symptom_herb_list += symptom_herb_list
        patient_dcts += [patient_dct]
        num_visits += len(patient_dct.keys())

    good_symptom_herb_vector = tf_idf(all_symptom_herb_list, num_visits)
    print len(good_symptom_herb_vector)
    exit()
    feature_vectors = []
    section_labels = []
    subsection_labels = []
    # Each patient has a feature vector.
    for patient_dct in patient_dcts:
        for (patient_id, section, subsection) in patient_dct:
            feature_vector = []
            patient_herbs_and_symptoms = patient_dct[(patient_id, section,
                subsection)]
            for element in good_symptom_herb_vector:
                feature_vector += [patient_herbs_and_symptoms.count(element)]
            # Add the current patient vector and labels.
            feature_vectors += [feature_vector]
            section_labels += [section]
            subsection_labels += [subsection]

    # Mapping each section to an index.
    all_sections = list(set(section_labels))
    true_labels = []
    for label in section_labels:
        true_labels += [all_sections.index(label)]

    num_clusters = len(all_sections)
    # random_state = 170
    # y_pred = KMeans(n_clusters=num_clusters,
    #     random_state=random_state).fit_predict(feature_vectors)
    y_pred = SpectralClustering(n_clusters=num_clusters, eigen_solver='arpack',
        affinity="nearest_neighbors").fit_predict(feature_vectors)
    print adjusted_rand_score(true_labels, y_pred)

    # K-Means:
    # Both: 0.00257750924311
    # Symptoms: -0.0023638
    # Herbs: 0.01508
    # With TF Filtering
    # Both: 0.006406
    # Symptoms: 0.015426
    # Herbs: 0.0176714

    # Spectral Clustering:
    # Both:
    # Symptoms: 0.008744735
    # Herbs: 0.0005592639531

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
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))