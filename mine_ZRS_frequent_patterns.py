### Author: Edward Huang

from pymining import itemmining, assocrules, perftesting
import time

### This script takes the symptoms and drugs prescribed to each patient, and
### attempts to mine the frequent patterns from these two sets across all of the
### patients in the ZRS dataset.

MIN_SUP = 2

if __name__ == '__main__':
    start_time = time.time()

    # Dictionary, with keys as patient ids, as values as lists of symptoms.
    symptom_dct = {}
    symptom_visit_nos = set([])
    # Read in the symptoms file.
    f = open('./data/ZRS_patient_symptoms.txt', 'r')
    for line in f:
        line = line.split()
        visit_no = line[0]
        symptom_dct[visit_no] = line[1:]
        symptom_visit_nos.add(visit_no)
    f.close()

    drug_dct = {}
    drug_set = set([])
    drug_visit_nos = set([])
    f = open('./data/ZRS_patient_drugs.txt', 'r')
    for i, line in enumerate(f):
        # Skip the header.
        if i == 0:
            continue
        line = line.split()
        visit_no = line[0]
        drugs = line[1:]
        drug_dct[visit_no] = drugs
        for drug in drugs:
            drug_set.add(drug)
        drug_visit_nos.add(visit_no)
    f.close()

    # There are 1887 symptom visits, but only 1618 drug visits. However, all
    # drug visits have symptom visits.
    # shared_visit_nos = drug_visit_nos.intersection(symptom_visit_nos)

    # Lump drugs and symptoms together as transactions for each visit number.
    transactions = []
    for visit_no in symptom_dct:
        # Skip visits that do not have a prescription.
        if visit_no not in drug_dct:
            continue
        symptoms = symptom_dct[visit_no]
        drugs = drug_dct[visit_no]
        curr_trans = tuple(symptoms + drugs)
        transactions += [curr_trans]

    transactions = tuple(transactions)

    # Write out the association rules.
    out = open('./results/ZRS_association_rules.txt', 'w')

    relim_input = itemmining.get_relim_input(transactions)
    item_sets = itemmining.relim(relim_input, min_support=MIN_SUP)
    rules = assocrules.mine_assoc_rules(item_sets, min_support=MIN_SUP, min_confidence=0.5)
    print rules
    for cause_set, effect_set, support, confidence in rules:
        # For each association rule, check to see if there is at least one drug
        # in the rule.
        # drug_in_rule = False
        for cause in cause_set:
            if cause in drug_set:
                drug_in_rule = True
                break
        for effect in effect_set:
            if effect in drug_set:
                drug_in_rule = True
                break
        if not drug_in_rule:
            continue
        # Write out the remaining association rules.
        for cause in cause_set:
            out.write(cause + ', ')
        out.write('->' )
        for effect in effect_set:
            out.write(effect + ', ')
        out.write('supp=%d, conf=%f\n' % (support, confidence))
    out.close

    print "---%f seconds---" % (time.time() - start_time)