Author: Edward Huang

First, process each of the three spreadsheets to create an input file to be sent
into LDA.

>>> python preprocess_raw_data.py

Then, run lda_script.py to run LDA on the inputs we prepared.
If it is the first time running the script, we must uncomment lines 14 and 15 to
make the directories.

>>> python lda_script.py

Use the first block to run for the original data set.

Lastly, we run print_topics.py to output the topic modeling results.

>>> python print_topics.py

Use the first block for original data.
__________________________________ZRS Data______________________________________
First, download the ZRS data.

$ python preprocess_ZRS_data

Outputs a file, ZRS_patient_symptoms.txt. Each symptom is sorted by a visit
id number.

The second file, ZRS_patient_drugs.txt, can simply be copied from the
appropriate columns from the raw excel file.
Next, we normalize the data.

$ python normalize_ZRS_data.py

It uses a similar technique to IDF to remove symptoms or drugs that appear too
frequently.

$ python mine_ZRS_frequent_pattersn.py

Outputs a file, ZRS_freq_patterns.txt, which contains the frequent patterns and
their support on each newline.

$ python filter_ZRS_frequent_patterns.py

Outputs norm_ZRS_freq_patterns.txt, which reformats each frequent pattern into
a drug, symptom set relationship, along with their previous support.

For topic modeling, run LDA for symptoms and drugs independently.

$ python create_ZRS_lda_input.py

$ python lda_script.py
Use the second block to run for ZRS data.

Lastly,
$ python print_topics.py
Also use the second block to run for ZRS data.

__________________________________HIS Data______________________________________

First,

$ python format_HIS_data.py

Takes the original HIS spreadsheet, and takes the proper columns. Sent the text
to Sheng for interpretation, and received HIS_clean_data.txt.

$ python create_HIS_transactions.py

