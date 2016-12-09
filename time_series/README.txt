Author: Edward Huang
These scripts deal with time series TCM data.

1. This script finds the most frequent herbs, and then computes the mutual
information between each herb and the symptoms with which they co-occur.

$ python frequent_herbs_and_symptoms.py

2. This script script takes the patient records and stems the herbs and symptoms
such that the resulting elements are all in the herb-symptom dictionary.

$ python stem_patient_records.py


3.
For every pair of symptoms, find how many herbs they share in the herb-symptom
dictionary. Additionally, show how many times the pair of symptoms appear in
patient records.
$ python symptom_pair_statistics.py

____________SURVIVAL_____________
For the survival model, run
$ python create_patient_dataframes.py

Then,
$ R survival_model.R