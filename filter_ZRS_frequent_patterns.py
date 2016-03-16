

import time

if __name__ == '__main__':
    start_time = time.time()

    # Dictionary, with keys as patient ids, as values as lists of symptoms.
    symptom_dct = {}
    # Read in the symptoms file.
    f = open('./data/ZRS_patient_symptoms.txt', 'r')
    for line in f:
        line = line.split()
        visit_no = line[0]
        symptoms = line[1:]
        for symptom in symptoms:
            if symptom in symptom_dct:
                symptom_dct[symptom] += 1
            else:
                symptom_dct[symptom] = 1
    f.close()

    drug_dct = {}
    f = open('./data/ZRS_patient_drugs.txt', 'r')
    for i, line in enumerate(f):
        # Skip the header.
        if i == 0:
            continue
        line = line.split()
        visit_no = line[0]
        drugs = line[1:]
        for drug in drugs:
            if drug in drug_dct:
                drug_dct[drug] += 1
            else:
                drug_dct[drug] = 1
    f.close()

    f = open('./results/ZRS_freq_patterns.txt', 'r')
    out = open('./results/norm_ZRS_freq_patterns.txt', 'w')
    for line in f:
        line = line.split(', ')
        patterns = line[:-1]
        freq = line[-1]

        drug_patterns = []
        symptom_patterns = []
        for entity in patterns:
            if entity in drug_dct:
                drug_patterns += [entity]
            else:
                assert (entity in symptom_dct)
                symptom_patterns += [entity]
        out.write(', '.join(drug_patterns))
        out.write(' -> ')
        out.write(', '.join(symptom_patterns) + ':%s\n' % freq)
    out.close()
    f.close()

    print "---%f seconds---" % (time.time() - start_time)