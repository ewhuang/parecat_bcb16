#!python2
#coding:utf8
### Author: Edward Huang

from collections import OrderedDict
import csv
import numpy as np 
import operator
from scipy.spatial.distance import pdist, squareform
from scipy.stats import entropy
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.cluster import adjusted_rand_score
import sys
import time

### This script clusters on the HIS stomach data, and finds subcategories.
### Run time: 50 minutes.

def read_stomach_data(vector_type, disease):
    '''
    This function reads the HIS stomach disease data, and forms a patient 
    dictionary where keys are patient ID's (line numbers) and values are lists
    of symptoms, herbs, or both, depending on the vector_type input.
    '''

    symptom_count_dct, herb_count_dct = {}, {}
    patient_list = []
    # We only want patients suffering from the "disease" argument.
    patient_dnd_list = []
    # This dictionary contains the consolidated visits for any single patient.
    # Keys are (name, birthday) pairs.
    # Values are 2-element lists, first element=symptoms, second=herbs.
    merged_patient_dct = {}

    f = open('./data/HIS_tuple_word.txt', 'r')
    for i, line in enumerate(f):
        # if disease not in disease_label_list[i]:
        #     continue
        (patient_disease, name, birthday, visit_date, patient_symptoms,
            patient_herbs) = line.strip('\n').split('\t')
        # patient_symptoms, patient_herbs = line.strip().split('\t')
        if disease not in patient_disease:
            continue

        # Add symptoms and herbs based on the keyword.
        if vector_type == 'symptoms':
            patient_symptoms = patient_symptoms.strip().split(':')
            patient_herbs = []
            if patient_symptoms == ['']:
                continue
        elif vector_type == 'herbs':
            patient_symptoms = []
            patient_herbs = patient_herbs.strip().split(':')
            if patient_herbs == ['']:
                continue
        elif vector_type == 'both':
            patient_symptoms = patient_symptoms.strip().split(':')
            patient_herbs = patient_herbs.strip().split(':')
            if patient_symptoms == [''] or patient_herbs == ['']:
                continue

        # Merge in a patient if he is already in the dictionary.
        key = (name, birthday)
        if key in merged_patient_dct:
            merged_patient_dct[key][0] = merged_patient_dct[key][0].union(
                patient_symptoms)
            merged_patient_dct[key][1] = merged_patient_dct[key][1].union(
                patient_herbs)
        else:
            merged_patient_dct[key] = [set(patient_symptoms), set(
                patient_herbs)]

        # Add to the master lists of symptoms and herbs.
        for symptom in patient_symptoms:
            if symptom not in symptom_count_dct:
                symptom_count_dct[symptom] = 1
            else:
                symptom_count_dct[symptom] += 1

        for herb in patient_herbs:
            if herb not in herb_count_dct:
                herb_count_dct[herb] = 1
            else:
                herb_count_dct[herb] += 1

        patient_list += [patient_symptoms + patient_herbs]
        patient_dnd_list += [(patient_disease, name, birthday)]

    f.close()

    # Sanity checks.
    if vector_type == 'symptoms':
        assert herb_count_dct == {}
    elif vector_type == 'herbs':
        assert symptom_count_dct == {}
    
    return (symptom_count_dct, herb_count_dct, patient_list,
        patient_dnd_list, merged_patient_dct)

def get_master_patient_list(vector_type, disease):
    '''
    Returns a pair.
    First element: feature list, where every herb and symptom feature is in the
    medicine dictionary.
    Second element: master dictionary, containing patient records across all 3
    documents.
    '''

    (symptom_count_dct, herb_count_dct, patient_list, patient_dnd_list,
        merged_patient_dct) = read_stomach_data(vector_type, disease)
    num_patients = len(patient_list)

    # Change symptom parameters based on feature type.
    sb, sa = 5, 0.2
    if vector_type == 'symptoms':
        sb, sa = 1, 0.05
    symptom_list = [symptom for symptom in symptom_count_dct if (
        sb < symptom_count_dct[symptom] <= sa * num_patients)]

    # Change herb parameters based on feature type.
    hb, ha = 2, 0.1
    if vector_type == 'herbs':
        hb = 1
    herb_list = [herb for herb in herb_count_dct if (
        hb < herb_count_dct[herb] <= ha * num_patients)]

    feature_list = list(set(symptom_list + herb_list))

    return feature_list, patient_list, patient_dnd_list, merged_patient_dct

def get_attribute_by_patient_matrix(feature_list, master_patient_list):
    '''
    Returns a 2D list, where each element corresponds to a patient. Each element
    is a list corresponding to a feature vector.
    '''
    num_features = len(feature_list)

    # Construct the herb by patient matrix.
    patient_by_attribute_matrix = []
    for i in range(len(master_patient_list)):
        # Initialize the feature vector to a list of 0's.
        patient_vector = [0 for j in range(num_features)]

        # Fetch the attributes for the patient.
        patient_attributes = master_patient_list[i]

        # Loop through the features. If the feature appears in a patient's
        # attributes, change the corresponding element to 1.
        for feature_index, feature in enumerate(feature_list):
            if feature in patient_attributes:
                patient_vector[feature_index] = 1

        # Add the patient vector to the matrix.
        patient_by_attribute_matrix += [patient_vector]

    # Return the transpose.
    return np.matrix(patient_by_attribute_matrix).T

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
        line = line.strip('\n').split('\t')

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

def get_most_similar_patients(distance_matrix):
    '''
    Returns the indices and distances of the most similar patient records.
    '''
    distance_dct = {}
    for i, row in enumerate(distance_matrix):
        for j, distance in enumerate(row):
            if np.isnan(distance) or distance < 0.00001 or (j, i
                ) in distance_dct:
                continue
            distance_dct[(i, j)] = distance
    sorted_distances = sorted(distance_dct.items(), key=operator.itemgetter(1))
    return sorted_distances

def write_similar_patients(sorted_distances, disease, patient_dnd_list,
    merged_patient_dct):
    out = open('./results/most_similar_stomach_patient_pairs_%s.txt' %
        disease, 'w')
    out.write('disease\tname\tdate_of_birth\tsymptoms\therbs\tcosine\n')

    # Determines the number of pairs to write out.
    pair_counter = 0
    for (i, j), distance in sorted_distances:
        if pair_counter == 30:
            break

        disease_i, name_i, birthday_i = patient_dnd_list[i]
        disease_j, name_j, birthday_j = patient_dnd_list[j]

        # Skip records that are of the same patient.
        if name_i == name_j and birthday_i == birthday_j:
            continue

        symptoms_i, herbs_i = merged_patient_dct[(name_i, birthday_i)]
        symptoms_j, herbs_j = merged_patient_dct[(name_j, birthday_j)]

        out.write('%s\t%s\t%s\t%s\t%s\t%g\n' % (disease_i, name_i, birthday_i,
            ','.join(symptoms_i), ','.join(herbs_i), 1 - distance))
        out.write('%s\t%s\t%s\t%s\t%s\t%g\n' % (disease_j, name_j, birthday_j,
            ','.join(symptoms_j), ','.join(herbs_j), 1 - distance))
        out.write('\n')

        pair_counter += 1
    out.close()

def create_cluster_dct(predicted_labels):
    '''
    Takes in the set of predicted labels from agglomerative clustering and
    creates a dictionary where keys are cluster labels, and values are lists of
    patients in the corresponding cluster keys.
    '''
    cluster_dct = {}
    for i, label in enumerate(predicted_labels):
        if label in cluster_dct:
            cluster_dct[label] += [i]
        else:
            cluster_dct[label] = [i]
    return cluster_dct

def write_clusters(cluster_dct, disease, patient_dnd_list, merged_patient_dct):
    '''
    Writes out the clusters to file.
    '''
    out = open('./results/stomach_%d_clusters_%s.txt' % (len(cluster_dct),
        disease), 'w')
    out.write('cluster_id\tdisease\tname\tdate_of_birth\tsymptoms\therbs\n')
    for clus_id in cluster_dct:    
        # Don't write a patient more than once per cluster. This happens
        # because a patient might have multiple visits. We only want to
        # write out the set of all symptoms and/or herbs across all visits.
        previously_written_patients = []

        patient_cluster = cluster_dct[clus_id]

        for patient_id in patient_cluster:
            # Fetch the attributes for the current patient.
            patient_disease, name, birthday = patient_dnd_list[patient_id]
            key = (name, birthday)
            if key in previously_written_patients:
                continue
            previously_written_patients += [key]

            symptoms, herbs = merged_patient_dct[key]

            out.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (clus_id, patient_disease,
                name, birthday, ','.join(symptoms), ','.join(herbs)))
        out.write('\n')
    out.close()

def main():
    reload(sys)
    sys.setdefaultencoding('cp1252')
    # Sorting out arguments.
    if len(sys.argv) != 4:
        print('Usage: %s symptoms/herbs/both sim_threshold num_clusters'
            % sys.argv[0])
        exit()
    vector_type = sys.argv[1]
    assert vector_type in ['symptoms', 'herbs', 'both']
    similarity_threshold = float(sys.argv[2])
    num_clusters = int(sys.argv[3])

    # This is the disease to cluster on. We ignore patients who do not have
    # this disease.
    disease = '慢性胃炎'

    (feature_list, master_patient_list, patient_dnd_list, merged_patient_dct
        ) = get_master_patient_list(vector_type, disease)

    # Get the patient by attribute matrix.
    attribute_by_patient_matrix = get_attribute_by_patient_matrix(feature_list,
        master_patient_list)

    # Uncomment this block if making changes to similarity matrix.
    similarity_matrix = get_similarity_matrix(feature_list,
        similarity_threshold)

    # Embed the similarity scores into the patient records.
    embedded_matrix = similarity_matrix * attribute_by_patient_matrix

    # Get the list of entropies for the embedded matrix.
    entropy_list = np.apply_along_axis(entropy, axis=1, arr=embedded_matrix)

    # Delete the percentage% lowest entropy elements.
    num_att_to_delete = int(len(feature_list) * 0.05)

    # Deleting lowest entropy attributes.
    att_indices_to_delete = entropy_list.argsort()[:num_att_to_delete]

    # First, copy the attribute by patient matrix.
    feature_vectors = np.copy(embedded_matrix)
    # Delete the lowest entropy attributes, and transpose.
    feature_vectors = np.delete(feature_vectors, att_indices_to_delete,
        axis=0).T

    # Get the most similar pairs of patient records.
    distance_matrix = squareform(pdist(feature_vectors, metric='cosine'))

    sorted_distances = get_most_similar_patients(distance_matrix)
    write_similar_patients(sorted_distances, disease, patient_dnd_list,
        merged_patient_dct)

    # Clustering methods.
    y_pred = AgglomerativeClustering(n_clusters=num_clusters,
        affinity='cosine', linkage='average').fit_predict(feature_vectors)

    cluster_dct = create_cluster_dct(y_pred)
    write_clusters(cluster_dct, disease, patient_dnd_list, merged_patient_dct)

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))