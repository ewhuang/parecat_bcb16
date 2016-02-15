### Author: Edward Huang

# import matplotlib.pyplot as plt

### This script normalizes the drug and symptom data. It counts the occurrences
### for each drug and symptom, and then removes the ones that appear in too 
### many patient visits. Similar to inverse document frequency.

if __name__ == '__main__':
    print 'Normalizing symptoms...'
    # Makes a dictionary for symptom counts.
    visits = set([])
    symptom_count_dct = {}
    f = open('./data/ZRS_patient_symptoms.txt', 'r')
    for line in f:
        line = line.split()
        visit_no = line[0]
        visits.add(visit_no)
        symptoms = line[1:]
        for symptom in symptoms:
            if symptom in symptom_count_dct:
                symptom_count_dct[symptom] += 1
            else:
                symptom_count_dct[symptom] = 1
    f.close()

    # Skip symptoms that are too common.
    common_symptoms = set([])
    # counts = []
    for symptom in symptom_count_dct:
        count = symptom_count_dct[symptom]
        # counts += [count]
        if count > 0.1 * len(visits) or count == 1:
            common_symptoms.add(symptom)

    # plt.hist(counts, bins=xrange(0, 100, 5))
    # plt.show()

    # Write out a new file without common symptoms.
    f = open('./data/ZRS_patient_symptoms.txt', 'r')
    out = open('./data/norm_ZRS_patient_symptoms.txt', 'w')
    for line in f:
        line = line.split()
        visit_no = line[0]
        symptoms = line[1:]
        new_symptoms = []
        for symptom in symptoms:
            if symptom not in common_symptoms:
                new_symptoms += [symptom]
        out.write(visit_no + '\t' + '\t'.join(new_symptoms) + '\n')
    out.close()
    f.close()

    print 'Normalizing drugs...'
    # Makes a dictionary for drug counts.
    drug_count_dct = {}
    f = open('./data/ZRS_patient_drugs.txt', 'r')
    for i, line in enumerate(f):
        # Skip the header.
        if i == 0:
            continue
        line = line.split()
        visit_no = line[0]
        drugs = line[1:]
        for drug in drugs:
            if drug in drug_count_dct:
                drug_count_dct[drug] += 1
            else:
                drug_count_dct[drug] = 1
    f.close()

    # Skip drugs that are too common.
    common_drugs = set([])
    for drug in drug_count_dct:
        count = drug_count_dct[drug]
        if count > 0.1 * len(visits) or count == 1:
            common_drugs.add(drug)

    # Write out a new file without common drugs.
    f = open('./data/ZRS_patient_drugs.txt', 'r')
    out = open('./data/norm_ZRS_patient_drugs.txt', 'w')
    for line in f:
        if i == 0:
            continue
        line = line.split()
        visit_no = line[0]
        drugs = line[1:]
        new_drugs = []
        for drug in drugs:
            if drug not in common_drugs:
                new_drugs += [drug]
        out.write(visit_no + '\t' + '\t'.join(new_drugs) + '\n')
    out.close()
    f.close()