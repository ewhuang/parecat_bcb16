### Author: Edward Huang

from sklearn.metrics import precision_recall_curve, roc_auc_score, auc

### This script generates predictive probabilities for herbs, symptoms, and 
### diseases.

NUM_SYMPTOMS = 3000
NUM_HERBS = 682
NUM_DISEASES = 96
CUTOFF = str(0.9)
PROBNUM = 11

# Read in the probability distribution files.
def get_distributions():
    # Get probabilities of each herb given each disease.
    p_H_given_D_matrix = []
    f = open('./data/%s_683_97_H_given_D.prob%d' % (CUTOFF, PROBNUM), 'r')
    for line in f:
        line = map(float, line.split())
        p_H_given_D_matrix += [line]
    f.close()

    # Get probabilities of each symptom given each disease.
    p_S_given_D_matrix = []
    f = open('./data/%s_3001_97_S_given_D.prob%d' % (CUTOFF, PROBNUM), 'r')
    for line in f:
        line = map(float, line.split())
        p_S_given_D_matrix += [line]
    f.close()

    # Get probabilities of each disease.
    p_D_vector = []
    f = open('./data/%s_3001_97D.prob%d' % (CUTOFF, PROBNUM), 'r')
    for line in f:
        line = float(line.strip())
        p_D_vector += [line]
    f.close()

    # The number of diseases should be equal.
    assert len(p_S_given_D_matrix) == len(p_H_given_D_matrix) == len(p_D_vector)
    return p_H_given_D_matrix, p_S_given_D_matrix, p_D_vector

# This function processes diseases, symptoms, or herbs. All sets end in a colon.
def process_list(lst):
    lst = lst.split(':')
    assert lst[-1] == ''
    lst = map(int, lst[:-1])
    # Subtract 1 from each index to convert to list indices.
    lst = [i - 1 for i in lst]
    return lst

# Read transactions from files. Keyword is either "test" or "training".
def read_transactions(keyword):
    # List of disease, symptom, herb tuples for each transaction.
    transactions = []
    # Open tuple file.
    f = open('./data/HIS_tuple_%s_%s.txt' % (keyword, CUTOFF), 'r')
    for line in f:
        line = line.strip().split('\t')
        assert len(line) == 3
        diseases, symptoms, herbs = line

        diseases = process_list(diseases)
        symptoms = process_list(symptoms)
        # Remove symptoms with index > 3000
        symptoms = [i for i in symptoms if i < NUM_SYMPTOMS]
        herbs = process_list(herbs)
        transactions += [(diseases, symptoms, herbs)]
    f.close()
    return transactions

# Baseline operations. Create p_S_given_D_matrix directly from the training
# transactions.
def get_empirical_distributions(transactions):
    # Initialize our three lists.
    p_D_vector = [0] * NUM_DISEASES
    p_S_given_D_matrix = []
    p_H_given_D_matrix = []
    for i in range(NUM_DISEASES):
        p_S_given_D_matrix += [[0] * NUM_SYMPTOMS]
        p_H_given_D_matrix += [[0] * NUM_HERBS]

    # Loop through the training transactions.
    for diseases, symptoms, herbs in transactions:
        for disease in diseases:
            p_D_vector[disease] += 1
            # Increment p(S, D) for each symptom in the transaction.
            for symptom in symptoms:
                p_S_given_D_matrix[disease][symptom] += 1
            # Increment p(h, D) for each herb in the transaction.
            for herb in herbs:
                p_H_given_D_matrix[disease][herb] += 1

    # Divide each p(h|D) and p(S|D) by the number of transactions containing D.
    for D, count in enumerate(p_D_vector):
        count = float(count)
        p_S_given_D_matrix[D] = [prob / count for prob in p_S_given_D_matrix[D]]
        p_H_given_D_matrix[D] = [prob / count for prob in p_H_given_D_matrix[D]]

    # Turn p(D) into probabilities by dividing by number of transactions.
    num_transactions = float(len(transactions))
    p_D_vector = [count / num_transactions for count in p_D_vector]
    return p_H_given_D_matrix, p_S_given_D_matrix, p_D_vector

# Given a set of symptoms, find the probability of assigning each herb to the
# symptoms.
def p_herb_given_symptoms(diseases, symptoms, p_S_given_D_matrix, p_D_vector,
    p_H_given_D_matrix):
    # Keys are herbs. Initialize the dictionary with all herbs as keys.
    herb_prob_dct = {}
    for herb in range(NUM_HERBS):
        herb_prob_dct[herb] = 0.0

    # Loop across all diseases in the transaction.
    for D in diseases:
        # Base probability: p(D) * p(S_1|D) * p(S_2|D) * ... * p(S_N|D), where
        # N is the number of symptoms in the input transaction.
        p_D = p_D_vector[D]
        base_prob = p_D

        p_S_given_D_vector = p_S_given_D_matrix[D]
        assert len(p_S_given_D_vector) == NUM_SYMPTOMS
        # For each symptom S_i, find p(S_i|D) and multiply together.
        for S in symptoms:
            base_prob *= p_S_given_D_vector[S]
        p_H_given_D_vector = p_H_given_D_matrix[D]
        assert len(p_H_given_D_vector) == NUM_HERBS
        for H, p_H_D in enumerate(p_H_given_D_vector):
            # Lastly, multiply by p(H|D).
            herb_prob_dct[H] += base_prob * p_H_D

    total_prob = sum(herb_prob_dct.values())
    if total_prob == 0:
        return 0
    for herb in herb_prob_dct:
        herb_prob_dct[herb] /= total_prob
    return herb_prob_dct

def p_disease_given_symptoms(symptoms, p_S_given_D_matrix, p_D_vector):
    disease_prob_dct = {}
    for D in range(len(p_D_vector)):
        p_D = p_D_vector[D]
        base_prob = p_D

        p_S_given_D_vector = p_S_given_D_matrix[D]
        assert len(p_S_given_D_vector) == NUM_SYMPTOMS        
        # Get p(S_i|D) for each symptom S_i in the transaction.
        for S in symptoms:
            base_prob *= p_S_given_D_vector[S]

        # Add the probability to the dictionary.
        assert D not in disease_prob_dct
        disease_prob_dct[D] = base_prob
    # Get the sum of all values, which will serve as normalization.
    total_prob = sum(disease_prob_dct.values())
    if total_prob == 0:
        return 0
    for disease in disease_prob_dct:
        disease_prob_dct[disease] /= total_prob
    return disease_prob_dct

def get_auc_metrics(prob_dct, test_set):
    p_test, p_hat = [], []
    for element in prob_dct:
        if element in test_set:
            p_test += [1]
        else:
            p_test += [0]
        p_hat += [prob_dct[element]]

    auroc = roc_auc_score(p_test, p_hat)
    precision,recall, thresholds = precision_recall_curve(p_test, p_hat)
    auprc = auc(recall,precision)
    return auroc, auprc

def compute_all_auc(test_transactions, p_H_given_D_matrix, p_S_given_D_matrix,
    p_D_vector, p_H_given_D_matrix_train, p_S_given_D_matrix_train,
    p_D_vector_train):
    all_h_auroc, all_h_auprc, all_d_auroc, all_d_auprc = [], [], [], []
    all_h_auroc_train, all_h_auprc_train = [], []
    all_d_auroc_train, all_d_auprc_train = [], []

    for diseases, symptoms, herbs in test_transactions:
        herb_prob_dct = p_herb_given_symptoms(diseases, symptoms,
                p_S_given_D_matrix, p_D_vector, p_H_given_D_matrix)
        if herb_prob_dct == 0: continue
        disease_prob_dct = p_disease_given_symptoms(symptoms,
                p_S_given_D_matrix, p_D_vector)
        if disease_prob_dct == 0: continue
        herb_prob_dct_train = p_herb_given_symptoms(diseases, symptoms,
            p_S_given_D_matrix_train, p_D_vector_train,
            p_H_given_D_matrix_train)
        if herb_prob_dct_train == 0: continue
        disease_prob_dct_train = p_disease_given_symptoms(symptoms,
                p_S_given_D_matrix_train, p_D_vector_train)
        if disease_prob_dct_train == 0: continue

        h_auroc, h_auprc = get_auc_metrics(herb_prob_dct, herbs)
        d_auroc, d_auprc = get_auc_metrics(disease_prob_dct, diseases)
        h_auroc_train, h_auprc_train = get_auc_metrics(herb_prob_dct_train,
            herbs)
        d_auroc_train, d_auprc_train = get_auc_metrics(disease_prob_dct_train,
            diseases)
        all_h_auroc += [h_auroc]
        all_h_auprc += [h_auprc]
        all_d_auroc += [d_auroc]
        all_d_auprc += [d_auprc]
        all_h_auroc_train += [h_auroc_train]
        all_h_auprc_train += [h_auprc_train]
        all_d_auroc_train += [d_auroc_train]
        all_d_auprc_train += [d_auprc_train]
    print 'AUPRC p(h|S) %s: %f' % (CUTOFF,
        sum(all_h_auprc) / len(all_h_auprc))
    print 'AUROC p(h|S) %s: %f' % (CUTOFF,
        sum(all_h_auroc) / len(all_h_auroc))
    print 'AUPRC p(D|S) %s: %f' % (CUTOFF,
        sum(all_d_auprc) / len(all_d_auprc))
    print 'AUROC p(D|S) %s: %f' % (CUTOFF,
        sum(all_d_auroc) / len(all_d_auroc))
    print 'Baseline AUPRC p(h|S) %s: %f' % (CUTOFF,
        sum(all_h_auprc_train) / len(all_h_auprc_train))
    print 'Baseline AUROC p(h|S) %s: %f' % (CUTOFF,
        sum(all_h_auroc_train) / len(all_h_auroc_train))
    print 'Baseline AUPRC p(D|S) %s: %f' % (CUTOFF,
        sum(all_d_auprc_train) / len(all_d_auprc_train))
    print 'Baseline AUROC p(D|S) %s: %f' % (CUTOFF,
        sum(all_d_auroc_train) / len(all_d_auroc_train))

if __name__ == '__main__':
    # Test data with distributions from Sheng.
    test_transactions = read_transactions('test')
    p_H_given_D_matrix, p_S_given_D_matrix, p_D_vector = get_distributions()

    # Training data with empirical distributions.
    train_transactions = read_transactions('training')
    p_H_given_D_matrix_train, p_S_given_D_matrix_train,\
        p_D_vector_train = get_empirical_distributions(train_transactions)

    print 'Full transactions'
    compute_all_auc(test_transactions, p_H_given_D_matrix, p_S_given_D_matrix,
        p_D_vector, p_H_given_D_matrix_train, p_S_given_D_matrix_train,
        p_D_vector_train)

    print 'Transactions with at least two diseases'
    trans_two_dis = []
    for transaction in test_transactions:
        diseases, symptoms, herbs = transaction
        if len(diseases) > 1:
            trans_two_dis += [transaction]
    compute_all_auc(trans_two_dis, p_H_given_D_matrix, p_S_given_D_matrix,
        p_D_vector, p_H_given_D_matrix_train, p_S_given_D_matrix_train,
        p_D_vector_train)


