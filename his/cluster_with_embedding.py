#!/usr/bin/env python
# -*- coding: utf-8 -*- 

### Author: Edward Huang

from collections import OrderedDict
import numpy as np
import operator
from scipy.stats import entropy
from sklearn.cluster import AgglomerativeClustering, KMeans, SpectralClustering
from sklearn.metrics.cluster import adjusted_rand_score
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
    # These two lists contain all of the unique symptoms and herbs in a
    # particular document.
    symptom_set, herb_set = [], []
    num_patient_visits = 0

    # Keys: (patient ID, section label, subsection label, document number)
    # Values: Lists of symptoms and/or herbs for the patient, depending on
    # vector_type.
    patient_dct = {}
    f = open('./data/medical_data_%d.txt' % file_num, 'r')
    for i, line in enumerate(f):
        (visit_symptoms, visit_herbs, patient_id, section,
            subsection) = line.split('\t')

        # Add symptoms and herbs based on the keyword.
        if vector_type == 'symptoms':
            visit_symptoms = visit_symptoms.split(',')
            visit_herbs = []
        elif vector_type == 'herbs':
            visit_symptoms = []
            visit_herbs = visit_herbs.split(',')
        elif vector_type == 'both':
            visit_symptoms = visit_symptoms.split(',')
            visit_herbs = visit_herbs.split(',')

        # Add to the master lists of symptoms and herbs.
        symptom_set += visit_symptoms
        herb_set += visit_herbs

        # Add each patient ID transaction.
        key = (patient_id, section, subsection, file_num)
        if key in patient_dct:
            patient_dct[key] += visit_symptoms + visit_herbs
        else:
            patient_dct[key] = visit_symptoms + visit_herbs

        # Increment the number of patient visits.
        num_patient_visits += 1

    f.close()

    return symptom_set, herb_set, patient_dct, num_patient_visits

def get_label_to_index_conversions(labels):
    '''
    Takes in a list of labels. Returns a set of true labels, mapped to indices,
    and the set of unique labels.
    '''
    # Mapping each section to an index.
    all_sections = list(set(labels))
    true_labels = []
    for label in labels:
        true_labels += [all_sections.index(label)]
    return true_labels, len(all_sections)

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
    
    similarity_dict = {}
    f = open('./results/similarity_matrix.txt', 'r')
    for i, line in enumerate(f):
        element_a, element_b, score = line.split()

        score = float(score)
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
        (symptom_list, herb_list, patient_dct,
            num_visits) = read_medical_data(i, vector_type)

        # Update master patient dictionary with current document.
        master_patient_dct.update(patient_dct)

        herb_list = get_semifrequent_terms(herb_list, 0,
            0.15 * len(patient_dct))
        symptom_list = get_semifrequent_terms(symptom_list, 1,
            0.05 * len(patient_dct))

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

def main():
    # Sorting out arguments.
    if len(sys.argv) != 6:
        print('Usage: %s symptoms/herbs/both top/section/subsection '
            'average/complete full/partial sim_threshold' % sys.argv[0])
        exit()
    vector_type = sys.argv[1]
    assert vector_type in ['symptoms', 'herbs', 'both']
    label_type = sys.argv[2]
    assert label_type in ['top', 'section', 'subsection']
    linkage = sys.argv[3]
    assert linkage in ['average', 'complete']
    # 'full' to use all herbs and symptoms. 'partial' to use only dictionary.
    abridged = (sys.argv[4] == 'partial')
    similarity_threshold = float(sys.argv[5])

    feature_list, master_patient_dct = get_master_patient_dct(vector_type,
        abridged)
    
    # Get the patient by attribute matrix.
    (attribute_by_patient_matrix, section_labels, subsection_labels,
        file_num_labels) = get_attribute_by_patient_matrix(feature_list,
        master_patient_dct)

    # Picking the type of labels.
    if label_type == 'top':
        true_labels, num_clusters = get_label_to_index_conversions(
            file_num_labels)
        assert num_clusters == 3
    elif label_type == 'section':
        true_labels, num_clusters = get_label_to_index_conversions(
            section_labels)
    elif label_type == 'subsection':
        true_labels, num_clusters = get_label_to_index_conversions(
            subsection_labels)

    # # Uncomment this block if making changes to similarity matrix.
    similarity_matrix = get_similarity_matrix(feature_list,
        similarity_threshold)
    embedded_matrix = similarity_matrix * attribute_by_patient_matrix
    # np.savetxt('./results/embedded_%s_matrix.txt' % vector_type,
    #     embedded_matrix)
    # exit()

    # embedded_matrix = np.loadtxt('./results/embedded_%s_matrix.txt' % (
    #     vector_type))

    # Change all cells greater than 1 back to 1.
    # def min_and_one(ele):
    #     if ele < 0.5:
    #         return 0
    #     return ele
    # min_and_one = np.vectorize(min_and_one)
    # embedded_matrix = min_and_one(embedded_matrix)

    # Get the list of entropies for the embedded matrix.
    entropy_list = np.apply_along_axis(entropy, axis=1, arr=embedded_matrix)

    # out = open('./results/embedding_clusters_%s_%s_%s_%s.txt' % (vector_type,
    #     label_type, similarity_method, linkage), 'w')

    # Delete the percentage% lowest entropy elements.
    for percentage in [p / 20.0 for p in range(20)]:
        num_att_to_delete = int(len(feature_list) * percentage)

        # Deleting lowest entropy attributes.
        att_indices_to_delete = entropy_list.argsort()[:num_att_to_delete]

        # First, copy the attribute by patient matrix.
        feature_vectors = np.copy(embedded_matrix)

        # Delete the lowest entropy attributes, and transpose.
        feature_vectors = np.delete(feature_vectors,
            att_indices_to_delete, axis=0).T

        # random_state = 170
        # y_pred = KMeans(n_clusters=num_clusters,
        #     random_state=random_state).fit_predict(feature_vectors)
        # print 'k-means %g' % (adjusted_rand_score(true_labels, y_pred))

        # y_pred = SpectralClustering(n_clusters=num_clusters,
        #     eigen_solver='arpack', random_state=random_state, 
        #     affinity="nearest_neighbors").fit_predict(feature_vectors)
        # print 'spectral %g' % (adjusted_rand_score(true_labels, y_pred))

        y_pred = AgglomerativeClustering(n_clusters=num_clusters,
            affinity='cosine', linkage=linkage).fit_predict(feature_vectors)
        rand_index = adjusted_rand_score(true_labels, y_pred)
        print rand_index
        # out.write(str(rand_index) + '\n')
    # out.close()

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))