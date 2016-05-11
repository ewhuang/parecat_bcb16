### Author: Edward Huang
import sys
reload(sys)
sys.setdefaultencoding('Cp1252')

from sklearn.cluster import AgglomerativeClustering, KMeans, SpectralClustering
from sklearn.metrics.cluster import adjusted_rand_score
import random
import time

### This script puts together the medical records data and clusters on them,
### evaluating based on the ground truth labels.

def read_medical_data(file_num, vector_type):
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
        key = (patient_id, section, subsection, file_num)
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

# Returns a list of good elements (symptoms or herbs) via TF-IDF.
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

def get_labels(labels):
    # Mapping each section to an index.
    all_sections = list(set(labels))
    true_labels = []
    for label in labels:
        true_labels += [all_sections.index(label)]
    return true_labels, all_sections

def main():

    # Sorting out arguments.
    if len(sys.argv) != 3:
        print 'Usage: %s symptoms/herbs/both top/section/subsection' % sys.argv[0]
        exit()
    vector_type = sys.argv[1]
    assert vector_type in ['symptoms', 'herbs', 'both']
    label_type = sys.argv[2]
    assert label_type in ['top', 'section', 'subsection']

    # for percentage in [p / 20.0 for p in range(1, 21)]:
    for beta in range(1, 11):
        symptom_herb_list = []
        master_patient_dct = {}
        for i in [1, 2, 3]:
            symptom_list, herb_list, patient_dct = read_medical_data(i, vector_type)
            # Concatenate all of the symptoms and herbs.
            master_patient_dct.update(patient_dct)

            num_visits = len(patient_dct)
            symptom_list = get_semifrequent_terms(symptom_list, beta,
                0.05 * num_visits)
            herb_list = get_semifrequent_terms(herb_list, 0,
                0.15 * num_visits)
            symptom_herb_list += symptom_list
            symptom_herb_list += herb_list

        symptom_herb_list = list(set(symptom_herb_list))

        feature_vectors = []
        section_labels, subsection_labels = [], []
        file_num_labels = []

        # Each patient has a feature vector.
        for (patient_id, section, subsection, file_num) in master_patient_dct:
            feature_vector = []
            patient_herbs_and_symptoms = master_patient_dct[(patient_id, section,
                subsection, file_num)]
            for element in symptom_herb_list:
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
            true_labels, all_sections = get_labels(file_num_labels)
            assert all_sections == 3
        elif label_type == 'section':
            true_labels, all_sections = get_labels(section_labels)
        elif label_type == 'subsection':
            true_labels, all_sections = get_labels(subsection_labels)

        num_clusters = len(all_sections)

        # random_state = 170
        # y_pred = KMeans(n_clusters=num_clusters,
        #     random_state=random_state).fit_predict(feature_vectors)
        # print 'k-means: %f' % (adjusted_rand_score(true_labels, y_pred))

        # y_pred = SpectralClustering(n_clusters=num_clusters, eigen_solver='arpack',
        #     random_state=random_state, 
        #     affinity="nearest_neighbors").fit_predict(feature_vectors)
        # print 'spectral: %f' % (adjusted_rand_score(true_labels, y_pred))

        y_pred = AgglomerativeClustering(n_clusters=num_clusters, affinity='cosine',
            linkage='average').fit_predict(feature_vectors)
        print adjusted_rand_score(true_labels, y_pred)

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