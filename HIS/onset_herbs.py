### Author: Edward Huang

from discontinued_herbs import *
import operator

### This script looks at a patient and gets a timeline for his medical history.
### We can see, for each patient, his set of symptoms and herbs. We want to see
### what happens when an herb is introduced in the middle of a patient's visit
### records, what type of symptoms and herbs it treats and replaces,
### respectively.

# This function takes an herb vector of 1's and 0's as input, and determines if
# the herb an onset herb, i.e. starts a 0.
def is_onset(vec):
    return vec[0] == '0'
def get_first_one(vector):
    return vector.index('1')

# If an herb is an onset herb, figure out when it stopped occurring.
def add_onset(dct, element, vector):
    if is_onset(vector):
        first_one = get_first_one(vector)
        dict_increment(dct, first_one, [element])

def main():
    # Keys are (onset herb, replaced herb, treated symptom) tuples. Keys are
    # counts.
    onset_treated_symptoms_dct = {}

    patient_dct = get_patient_dct()

    out = open('./results/onset_herb_replacements.txt', 'w')
    out.write('onset\treplaced\ttreated_symptom\tcount\n')
    for name, dob in patient_dct:
        # Skip patients that only have one visit.
        if len(patient_dct[(name, dob)]) == 1:
            continue
        symptoms, herbs = parse_patient(patient_dct[(name, dob)])
        if (False not in [vector == [] for vector in symptoms] or
            False not in [vector == [] for vector in herbs]):
            continue

        symptom_occurrence_dct = get_occurrence_dct(symptoms)
        herb_occurrence_dct = get_occurrence_dct(herbs)

        onset_herbs = []
        # Keys are indices of a vector's last one, and values are lists of herbs
        # corresponding to those indices. If a key is 2, then an herb with
        # vector [0, 1, 1, 0, 0] would be in the list of values for that key.
        last_one_dct = {}

        # Keys are herbs, and values are lists of herbs that the keys replace.
        onset_replaced_herbs_dct = {}

        for herb in herb_occurrence_dct:
            herb_vec = herb_occurrence_dct[herb]
            first_one = get_first_one(herb_vec)
            if is_onset(herb_vec):
                onset_herbs += [(herb, first_one)]
            dict_increment(last_one_dct, get_last_one(herb_vec), [herb])

        for herb, first_one in onset_herbs:
            # If the last 1 of herb A occurs right before an onset herb's first
            # 1, then the onset herb potentially replaces herb A.
            previous_visit = first_one - 1
            if previous_visit in last_one_dct:
                onset_replaced_herbs_dct[herb] = last_one_dct[previous_visit]

        # An onset herb successfully replaces one of its replaced herbs if 
        # the two vectors combined successfully treats a symptom.
        for onset_herb in onset_replaced_herbs_dct:
            replaced_herbs = onset_replaced_herbs_dct[onset_herb]
            for replaced_herb in replaced_herbs:
                # If an onset herb's vector OR'd with a replaced herb vector
                # equals a symptom vector, then the onset herb successfully
                # replaces a replaced herb in treating the symptom.
                onset_int = int(''.join(herb_occurrence_dct[onset_herb]), 2)
                replaced_int = int(''.join(herb_occurrence_dct[replaced_herb]),
                    2)
                herb_int = onset_int | replaced_int
                for symptom in symptom_occurrence_dct:
                    symptom_vec = symptom_occurrence_dct[symptom]
                    # Skip symptoms that aren't cured.
                    if symptom_vec[-1] != '0':
                        continue
                    if herb_int == int(''.join(symptom_vec), 2):
                        dict_increment(onset_treated_symptoms_dct,
                            (onset_herb, replaced_herb, symptom), 1)

    sorted_tuples = sorted(onset_treated_symptoms_dct.items(),
        key=operator.itemgetter(1), reverse=True)
    for (onset_herb, replaced_herb, symptom), count in sorted_tuples:
        out.write('%s\t%s\t%s\t%d\n' % (onset_herb, replaced_herb, symptom,
            count))

if __name__ == '__main__':
    main()