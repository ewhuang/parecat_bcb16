Author: Edward Huang
These scripts deal with time series TCM data.

1. This script finds the most frequent herbs, and then computes the mutual
information between each herb and the symptoms with which they co-occur.

$ python frequent_herbs_and_symptoms.py

2. This script script takes the patient records and stems the herbs and symptoms
such that the resulting elements are all in the herb-symptom dictionary.

$ python stem_patient_records.py
