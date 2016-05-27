### Author: Edward Huang
import sys
reload(sys)
sys.setdefaultencoding('Cp1252')

from sklearn.cluster import AgglomerativeClustering, KMeans, SpectralClustering
from sklearn.metrics.cluster import adjusted_rand_score, completeness_score
import numpy as np
import random
import time

### This script puts together the medical records data and clusters on them,
### evaluating based on the ground truth labels.

def read_medical_data(file_num, vector_type):
    '''
    Takes in a file number and a vector type. Reads the medical data for the
    given file number, and outputs a dictionary where the elements for a 
    patient contains the vector_type. Can be herbs, symptoms, or both.
    '''
    all_symptom_list, all_herb_list = [], []
    patient_dct = {}
    f = open('./data/medical_data_%d.txt' % file_num, 'r')
    for line in f:
        (patient_symptoms, patient_herbs, patient_id, section,
            subsection) = line.split('\t')

        # Add symptoms and herbs based on the keyword.
        if vector_type == 'symptoms':
            patient_symptoms = patient_symptoms.split(',')
            patient_herbs = []
        elif vector_type == 'herbs':
            patient_symptoms = []
            patient_herbs = patient_herbs.split(',')
        elif vector_type == 'both':
            patient_symptoms = patient_symptoms.split(',')
            patient_herbs = patient_herbs.split(',')

        # Add to the master lists of symptoms and herbs.
        all_symptom_list += patient_symptoms
        all_herb_list += patient_herbs

        # Add each patient ID transaction.
        key = (patient_id.strip(), section.strip(), subsection.strip(),
            file_num)
        if key in patient_dct:
            patient_dct[key] += patient_symptoms + patient_herbs
        else:
            patient_dct[key] = patient_symptoms + patient_herbs
    f.close()

    # Sanity checks.
    if vector_type == 'symptoms':
        assert all_herb_list == []
    elif vector_type == 'herbs':
        assert all_symptom_list == []

    return all_symptom_list, all_herb_list, patient_dct

def get_semifrequent_terms(feature_list, lower_bound, upper_bound):
    '''
    Takes in a list of elements, and a lower bound and upper bound.
    Returns elements that have number of appearances between the two bounds.    
    '''
    symptom_herb_set = set(feature_list)
    good_symptom_herb_vector = []
    for element in symptom_herb_set:
        if lower_bound < feature_list.count(element) <= upper_bound:
            good_symptom_herb_vector += [element]
    return good_symptom_herb_vector

def get_label_to_index_conversions(labels):
    '''
    Takes in a list of labels. Returns a set of true labels, mapped to indices,
    and the set of unique labels.
    '''
    return [labels.index(label) for label in labels]

def cluster_patient_records(label_type, vector_type, sb, sa, hb, ha):
    '''
    Clusters on the patient records. sa sb are symptom alpha and symptom beta,
    the upper and lower bounds for filtering out symptoms. Similar for ha and
    hb.
    '''
    feature_list = []
    master_patient_dct = {}
    for i in range(1, 4):
        symptom_list, herb_list, patient_dct = read_medical_data(i,
            vector_type)
        master_patient_dct.update(patient_dct)

        # Filter out rare and common symptoms and herbs.
        num_visits = len(patient_dct)
        symptom_list = get_semifrequent_terms(symptom_list, sb, sa * num_visits)
        herb_list = get_semifrequent_terms(herb_list, hb, ha * num_visits)
        feature_list += symptom_list + herb_list

    feature_list = list(set(feature_list))

    feature_vectors = []
    file_num_labels, section_labels, subsection_labels = [], [], []

    # Each patient has a feature vector.
    for key in master_patient_dct:
        (patient_id, section, subsection, file_num) = key
        feature_vector = []
        patient_herbs_and_symptoms = master_patient_dct[key]

        for element in feature_list:
            if element in patient_herbs_and_symptoms:
                feature_vector += [1]
            else:
                feature_vector += [0]
        # Add the current patient vector and labels.
        feature_vectors += [feature_vector]
        section_labels += [section]
        subsection_labels += [subsection]
        file_num_labels += [file_num]

    # Picking the type of labels.
    if label_type == 'top':
        true_labels = get_label_to_index_conversions(file_num_labels)
    elif label_type == 'section':
        true_labels = get_label_to_index_conversions(section_labels)
    elif label_type == 'subsection':
        true_labels = get_label_to_index_conversions(subsection_labels)

    num_clusters = len(set(true_labels))

    random_state = 5191993
    y_pred = KMeans(n_clusters=num_clusters,
        random_state=random_state).fit_predict(feature_vectors)
    print 'k-means: %f' % (adjusted_rand_score(true_labels, y_pred))

    y_pred = SpectralClustering(n_clusters=num_clusters, eigen_solver='arpack',
        random_state=random_state, 
        affinity="cosine").fit_predict(feature_vectors)
    print 'spectral: %f' % (adjusted_rand_score(true_labels, y_pred))

    y_pred = AgglomerativeClustering(n_clusters=num_clusters, affinity='cosine',
        linkage='average').fit_predict(feature_vectors)
    print adjusted_rand_score(true_labels, y_pred), sb, sa, hb, ha

def main():

    # Sorting out arguments.
    if len(sys.argv) < 3:
        print 'Usage: %s symptoms/herbs/both top/section/subsection both_hb' % (
            sys.argv[0])
        exit()
    vector_type = sys.argv[1]
    assert vector_type in ['symptoms', 'herbs', 'both']
    label_type = sys.argv[2]
    assert label_type in ['top', 'section', 'subsection']
    # For efficiency issues.
    if len(sys.argv) == 4:
        assert vector_type == 'both'
        both_hb = int(sys.argv[3])

    ## This block for tuning purposes.
    # if vector_type == 'herbs':
    #     for hb in range(6):
    #         for ha in np.arange(0.05, 0.3, 0.025):
    #             cluster_patient_records(label_type, vector_type, 0, 0, hb, ha)
    # elif vector_type == 'symptoms':
    #     for sb in range(6):
    #         for sa in np.arange(0.05, 0.25, 0.5):
    #             cluster_patient_records(label_type, vector_type, sb, sa, 0, 0)
    # elif vector_type == 'both':
    #     for sb in range(6):
    #         for sa in np.arange(0.05, 0.25, 0.05):
    #             for ha in np.arange(0.05, 0.25, 0.05):
    #                 cluster_patient_records(label_type, vector_type, sb, sa,
    #                     both_hb, ha)

    cluster_patient_records(label_type, vector_type, 5, 0.2, 2, 0.1)

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