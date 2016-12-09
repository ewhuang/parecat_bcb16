#!/usr/bin/env python
# -*- coding: utf-8 -*- 

### Author: Edward Huang

from collections import OrderedDict
import numpy as np
from scipy.stats import entropy, ttest_ind
from sklearn.cluster import AgglomerativeClustering, KMeans, SpectralClustering
from sklearn.metrics.cluster import adjusted_rand_score, completeness_score
import random
import sys
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

def get_label_to_index_conversions(labels):
    '''
    Takes in a list of labels. Returns a set of true labels, mapped to indices,
    and the set of unique labels.
    '''
    return [labels.index(label) for label in labels]

def get_medicine_dictionary_file():
    '''
    Returns the dictionary produced by the file.
    Keys: herbs
    Values: lists of symptoms
    Also returns the list of all symptoms as a feature vector.
    '''

    # Keys are herbs, and values are the symptoms that the herbs treat.
    herb_symptom_dct = OrderedDict({})

    f = open('./data/herb_symptom_dictionary.txt', 'r')
    for i, line in enumerate(f):
        if i == 0:
            continue
        line = line.strip().split('\t')

        line_length = len(line)
        # Some symptoms don't have good English translations.
        assert line_length == 2 or line_length == 5
        if line_length == 2:
            herb, symptom = line
        elif line_length == 5:
            herb, symptom, english_symptom, db_src, db_src_id = line

        # Add to the herb dictionary.
        if herb in herb_symptom_dct:
            if symptom not in herb_symptom_dct[herb]:
                herb_symptom_dct[herb] += [symptom]
        else:
            herb_symptom_dct[herb] = [symptom]

        # Add to the symptom dictionary.
        if symptom in herb_symptom_dct:
            if herb not in herb_symptom_dct[symptom]:
                herb_symptom_dct[symptom] += [herb]
        else:
            herb_symptom_dct[symptom] = [herb]

    f.close()

    return herb_symptom_dct

def get_similarity_matrix(feature_list, similarity_threshold):
    '''
    Returns a 2D list, consisting of an herb-by-herb similarity matrix, or
    symptom-by-symptom, or both-by-both.
    '''
    # Initialize an NxN matrix.
    num_features = len(feature_list)
    # Initialize as identity matrix.
    similarity_matrix = np.identity(num_features)

    dictionary_herb_symptom_list = get_medicine_dictionary_file().keys()
    
    f = open('./results/similarity_matrix.txt', 'r')
    for i, line in enumerate(f):
        element_a, element_b, score = line.split()

        score = abs(float(score))
        if score < similarity_threshold:
            continue

        # Convert the elements to indices, and fetch their names.
        element_a = dictionary_herb_symptom_list[int(element_a) - 1]
        if element_a not in feature_list:
            continue
        
        element_b = dictionary_herb_symptom_list[int(element_b) - 1]
        if element_b not in feature_list:
            continue

        # Convert the elements to indices in the feature list.
        element_a = feature_list.index(element_a)
        element_b = feature_list.index(element_b)

        similarity_matrix[element_a, element_b] = score

    f.close()
    return similarity_matrix

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

def get_master_patient_dct(vector_type, abridged):
    '''
    Returns a pair.
    First element: feature list, where every herb and symptom feature is in the
    medicine dictionary.
    Second element: master dictionary, containing patient records across all 3
    documents.
    '''
    # Only consider these herbs and symptoms for our feature vector if using
    # abridged attributes..
    if abridged:
        dictionary_herbs_symptoms = get_medicine_dictionary_file().keys()

    # Contains the patient dictionary across all three documents.
    master_patient_dct = {}
    feature_list = []
    for i in range(1, 4):
        (symptom_list, herb_list, patient_dct) = read_medical_data(i,
            vector_type)

        # Update master patient dictionary with current document.
        master_patient_dct.update(patient_dct)

        hb = 2
        ha = 0.1
        if vector_type == 'herbs':
            hb = 1
        herb_list = get_semifrequent_terms(herb_list, hb,
            ha * len(patient_dct))

        # Optimal lower bound is different between symptom features and both
        # features.
        sb = 5
        sa = 0.2
        if vector_type == 'symptoms':
            sb = 1
            sa = 0.05

        symptom_list = get_semifrequent_terms(symptom_list, sb,
            sa * len(patient_dct))

        if abridged:
            for element in symptom_list + herb_list:
                if element in dictionary_herbs_symptoms:
                    feature_list += [element]
        else:
            feature_list += symptom_list + herb_list

    feature_list = list(set(feature_list))

    return feature_list, master_patient_dct

def get_attribute_by_patient_matrix(feature_list, master_patient_dct):
    '''
    Returns a 2D list, where each element corresponds to a patient. Each element
    is a list corresponding to a feature vector.
    '''
    num_features = len(feature_list)

    # Contains the annotations for each patient. These are the ground truth.
    section_labels, subsection_labels, file_num_labels = [], [], []

    # Construct the herb by patient matrix.
    patient_by_attribute_matrix = []
    for key in master_patient_dct:
        # Initialize the feature vector to a list of 0's.
        patient_vector = [0 for i in range(num_features)]

        # Fetch the attributes for the patient.
        patient_id, section, subsection, file_num = key
        patient_attributes = master_patient_dct[key]

        # Loop through the features. If the feature appears in a patient's
        # attributes, change the corresponding element to 1.
        for feature_index, feature in enumerate(feature_list):
            if feature in patient_attributes:
                patient_vector[feature_index] = 1

        # Add the patient vector to the matrix.
        patient_by_attribute_matrix += [patient_vector]

        section_labels += [section]
        subsection_labels += [subsection]
        file_num_labels += [file_num]

    # Return the transpose.
    return (np.matrix(patient_by_attribute_matrix).T, section_labels,
        subsection_labels, file_num_labels)

def get_top_k_elements_per_row_sim_mat(similarity_matrix, k):
    '''
    Introduces another parameter, k, where we only keep the top k similarity
    scores per row in the similarity matrix.
    '''
    for i, row in enumerate(similarity_matrix):
        k = len(row) - k
        kth_largest = np.partition(row, k)[k]
        similarity_matrix[i] = [ele if ele >= kth_largest else 0 for ele in row]
    return similarity_matrix

def upper_bound_matrix(embedded_matrix):
    '''
    Makes the maximum value of a value in the similarity matrix 1.
    '''
    for i, row in enumerate(embedded_matrix):
        embedded_matrix[i] = [ele if ele <= 1 else 1 for ele in row]
    return embedded_matrix

def average_f_measure(true_labels, y_pred):
    '''
    Outputs the list of F1 scores for each cluster.
    '''
    f1_list = []
    for cluster_label in set(true_labels):
        current_true_cluster = [i for i, e in enumerate(true_labels
            ) if e == cluster_label]
        best_cluster_f = 0
        # Get the best predicted cluster for each true cluster.
        for pred_cluster_label in set(y_pred):
            current_pred_cluster = [i for i, e in enumerate(y_pred
                ) if e == pred_cluster_label]
            true_positive = float(len(set(current_true_cluster).intersection(
                current_pred_cluster)))
            precision = true_positive / len(current_pred_cluster)
            recall = true_positive / len(current_true_cluster)
            if precision == 0 and recall == 0:
                continue
            else:
                f_1 = 2 * precision * recall / (precision + recall)
            best_cluster_f = max(f_1, best_cluster_f)
        f1_list += [f_1]

    y = [0.03200000000000001, 0.0440251572327044, 0.011627906976744186, 0.11764705882352941, 0.010416666666666666, 0.2, 0.033057851239669415, 0.02390438247011952, 0.0075187969924812035, 0.04878048780487805, 0.018518518518518517, 0.013157894736842106, 0.04166666666666667, 0.007246376811594203, 0.010526315789473684, 0.007380073800738007, 0.013513513513513514, 0.11764705882352941, 0.125, 0.04347826086956521, 0.11764705882352941, 0.09090909090909093, 0.0392156862745098, 0.07142857142857142, 0.013245033112582783, 0.028368794326241138, 0.23529411764705882, 0.017241379310344827, 0.013157894736842105, 0.007407407407407408, 0.046511627906976744, 0.07407407407407407, 0.0641025641025641, 0.25, 0.015384615384615385, 0.28571428571428575, 0.014705882352941178, 0.026143790849673203, 0.08333333333333334, 0.015267175572519083, 0.1818181818181818, 0.013157894736842105, 0.17857142857142858, 0.013245033112582783, 0.017094017094017096, 0.038834951456310676, 0.11764705882352942, 0.07407407407407407, 0.1818181818181818, 0.11111111111111112, 0.01904761904761905]

    print np.mean(f1_list), 'with embedding'

    print np.mean(y), 'without embedding'

    print ttest_ind(f1_list, y)[1] / 2.0

def main():
    # Sorting out arguments.
    if len(sys.argv) != 4:
        print('Usage: %s symptoms/herbs/both top/section/subsection'
            ' similarity_threshold' % sys.argv[0])
        exit()
    vector_type = sys.argv[1]
    assert vector_type in ['symptoms', 'herbs', 'both']
    label_type = sys.argv[2]
    assert label_type in ['top', 'section', 'subsection']
    # linkage = sys.argv[3]
    # assert linkage in ['average', 'complete']
    # # 'full' to use all herbs and symptoms. 'partial' to use only dictionary.
    # abridged = (sys.argv[4] == 'partial')
    similarity_threshold = float(sys.argv[3])

    feature_list, master_patient_dct = get_master_patient_dct(vector_type,
        False)
    
    # Get the patient by attribute matrix.
    (attribute_by_patient_matrix, section_labels, subsection_labels,
        file_num_labels) = get_attribute_by_patient_matrix(feature_list,
        master_patient_dct)

    # Picking the type of labels.
    if label_type == 'top':
        true_labels = get_label_to_index_conversions(file_num_labels)
    elif label_type == 'section':
        true_labels = get_label_to_index_conversions(section_labels)
    elif label_type == 'subsection':
        true_labels = get_label_to_index_conversions(subsection_labels)

    num_clusters = len(set(true_labels))

    # Uncomment this block if making changes to similarity matrix.
    similarity_matrix = get_similarity_matrix(feature_list,
        similarity_threshold)

    # similarity_matrix = get_top_k_elements_per_row_sim_mat(
    #     similarity_matrix, top_k)

    embedded_matrix = similarity_matrix * attribute_by_patient_matrix

    # embedded_matrix = upper_bound_matrix(np.array(embedded_matrix))

    # np.savetxt('./results/embedded_%s_matrix.txt' % vector_type,
    #     embedded_matrix)
    # exit()

    # embedded_matrix = np.loadtxt('./results/embedded_%s_matrix.txt' % (
    #     vector_type))

    # Get the list of entropies for the embedded matrix.
    entropy_list = np.apply_along_axis(entropy, axis=1, arr=embedded_matrix)

    # Delete the percentage% lowest entropy elements.
    # for percentage in [p / 20.0 for p in range(20)]:
    for percentage in [0.0]:
        num_att_to_delete = int(len(feature_list) * percentage)

        # Deleting lowest entropy attributes.
        att_indices_to_delete = entropy_list.argsort()[:num_att_to_delete]

        # First, copy the attribute by patient matrix.
        feature_vectors = np.copy(embedded_matrix)

        # Delete the lowest entropy attributes, and transpose.
        feature_vectors = np.delete(feature_vectors,
            att_indices_to_delete, axis=0).T

        # random_state = 5191993
        # y_pred = KMeans(n_clusters=num_clusters,
        #     random_state=random_state).fit_predict(feature_vectors)
        # print 'k-means %g' % (adjusted_rand_score(true_labels, y_pred))

        # y_pred = SpectralClustering(n_clusters=num_clusters,
        #     eigen_solver='arpack', random_state=random_state, 
        #     affinity="cosine").fit_predict(feature_vectors)
        # print 'spectral %g' % (adjusted_rand_score(true_labels, y_pred))

        y_pred = AgglomerativeClustering(n_clusters=num_clusters,
            affinity='cosine', linkage='average').fit_predict(
            feature_vectors)
        # cluster_dct = {}
        # for i, cluster_label in enumerate(y_pred):
        #     section_label = section_labels[i]
        #     subsection_label = subsection_labels[i]
        #     patient = (section_label, subsection_label)
        #     if cluster_label in cluster_dct:
        #         cluster_dct[cluster_label] += [patient]
        #     else:
        #         cluster_dct[cluster_label] = [patient]

        # out = open('./results/embedding_patient_clusters.txt', 'w')
        # for cluster_label in cluster_dct:
        #     patient_cluster = cluster_dct[cluster_label]
        #     for section_label, subsection_label in patient_cluster:
        #         out.write('%s,%s\t' % (section_label, subsection_label))
        #     out.write('\n')
        # out.close()


        rand_index = adjusted_rand_score(true_labels, y_pred)
        # if rand_index >= 0.292420:
        print rand_index, percentage
        average_f_measure(true_labels, y_pred)
        # compl_score = completeness_score(true_labels, y_pred)
        # print compl_score
        # out.write(str(rand_index) + '\n')
    # out.close()

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))