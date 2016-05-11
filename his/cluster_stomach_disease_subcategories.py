#!python2
#coding:utf8
### Author: Edward Huang

from collections import OrderedDict
import csv
import operator
from sklearn.cluster import AgglomerativeClustering
import time

### This script clusters on the HIS stomach data, and finds subcategories.
### Run time: 50 minutes.

def get_count_dct(keyword, lower_bound, upper_bound):
    '''
    Returns a list of all of the herbs or symptoms, important for index mapping.
    Also returns an herb count dictionary.
    '''
    attribute_count_dct = OrderedDict({})
    f = open('./data/%s_dct.txt' % keyword, 'r')
    for i, line in enumerate(f):
        attribute, count = line.strip().split('\t')
        count = int(count)

        # Skip out-of-bounds attributes.
        if count <= lower_bound or count >= upper_bound:
            continue

        attribute_count_dct[attribute] = count

    f.close()
    return attribute_count_dct

def get_feature_matrix(feature_list):
    feature_matrix = []

    f = open('./data/HIS_transactions_words.csv', 'r')
    for i, line in enumerate(f):
        if i == 2000:
            break
        attribute_list = line.split(',')

        feature_vector = [1 if (attribute in attribute_list
            ) else 0 for attribute in feature_list]

        feature_matrix += [feature_vector]
    f.close()

    return feature_matrix

def get_attribute_cluster(feature_matrix, feature_list, symptom_count_dct):
    '''
    Gets the symptom and herb clusters from a set of feature vectors.
    '''
    symptom_cluster = {}
    herb_cluster = {}
    for feature_vector in feature_matrix:
        for index, element in enumerate(feature_vector):
            if element == 1:
                chinese_element = feature_list[index]
                if chinese_element in symptom_count_dct:
                    if chinese_element in symptom_cluster:
                        symptom_cluster[chinese_element] += 1
                    else:
                        symptom_cluster[chinese_element] = 1
                else:
                    if chinese_element in herb_cluster:
                        herb_cluster[chinese_element] += 1
                    else:
                        herb_cluster[chinese_element] = 1

    return symptom_cluster, herb_cluster

def get_agg_cluster_dct(feature_matrix, num_clusters):
    '''
    Performs agglomerative clustering on the feature matrix. Also takes in the
    number of clusters as input.
    Returns dictionary.
    Keys: Cluster numbers.
    Values: Lists of feature vectors.
    '''
    cluster_labels = AgglomerativeClustering(n_clusters=num_clusters,
            affinity='cosine', linkage='average').fit_predict(feature_matrix)

    # Construct first level patient record clustering.
    cluster_dct = {}
    for feature_index, cluster_id in enumerate(cluster_labels):
        if cluster_id in cluster_dct:
            cluster_dct[cluster_id] += [feature_matrix[feature_index]]
        else:
            cluster_dct[cluster_id] = [feature_matrix[feature_index]]
    return cluster_dct

def main():
    herb_count_dct = get_count_dct('herb', 0, 1000)
    symptom_count_dct = get_count_dct('sym', 1, 1000)
    symptom_list = symptom_count_dct.keys()

    feature_list = herb_count_dct.keys() + symptom_list

    feature_matrix = get_feature_matrix(feature_list)

    # Cluster first level.
    num_first_level_clusters = 50
    first_cluster_dct = get_agg_cluster_dct(feature_matrix,
        num_first_level_clusters)

    # Initialize files.
    herb_out = open('./results/stomach_disease_herb_clusters.csv', 'w')
    symptom_out = open('./results/stomach_disease_symptom_clusters.csv', 'w')    
    h = csv.writer(herb_out, delimiter='\t')
    s = csv.writer(symptom_out, delimiter='\t')

    sorted_symptom_count_dct = sorted(symptom_count_dct.items(), key=operator.itemgetter(1), reverse=True)
    sorted_herb_count_dct = sorted(herb_count_dct.items(), key=operator.itemgetter(1), reverse=True)

    # Cluster again on the clusters from first level.
    for i in range(num_first_level_clusters):
        if len(first_cluster_dct[i]) > 50:
            # Further break down large clusters.
            num_second_level_clusters = 50
            second_cluster_dct = get_agg_cluster_dct(first_cluster_dct[i],
                num_second_level_clusters)

            for j in range(num_second_level_clusters):
                symptom_cluster, herb_cluster = get_attribute_cluster(
                    second_cluster_dct[j], feature_list, symptom_count_dct)
                # Sort the clusters.
                sorted_symptoms = sorted(symptom_cluster.items(), key=operator.itemgetter(1), reverse=True)
                sorted_herbs = sorted(herb_cluster.items(), key=operator.itemgetter(1), reverse=True)
                
                symptom_cluster = []
                for symptom, count in sorted_symptoms:
                    symptom_cluster += [symptom + ':%d' % count]

                herb_cluster = []
                for herb, count in sorted_herbs:
                    herb_cluster += [herb + ':%d' % count]

                h.writerow(['2'] + herb_cluster)
                s.writerow(['2'] + symptom_cluster)
        else:
            # If a cluster has fewer than 50 records, then just write out those
            # cluster elements.
            symptom_cluster, herb_cluster = get_attribute_cluster(
                first_cluster_dct[i], feature_list, symptom_count_dct)

            # Sort the clusters.
            sorted_symptoms = sorted(symptom_cluster.items(),
                key=operator.itemgetter(1), reverse=True)
            sorted_herbs = sorted(herb_cluster.items(),
                key=operator.itemgetter(1), reverse=True)
            
            symptom_cluster = []
            for symptom, count in sorted_symptoms:
                symptom_cluster += [symptom + ':%d' % count]

            herb_cluster = []
            for herb, count in sorted_herbs:
                herb_cluster += [herb + ':%d' % count]

            h.writerow(['1'] + herb_cluster)
            s.writerow(['1'] + symptom_cluster)

    symptom_out.close()
    herb_out.close()

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))