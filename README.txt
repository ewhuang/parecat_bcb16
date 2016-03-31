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

This creates a csv file where each row is a transaction, and the items are the
indices of the symptoms or herbs as they appeared in the raw data.

______________________
Next, we run FP Growth to find frequent patterns.
$ cd python-fp-growth-master
$ python -m fp_growth -s 5 ../HIS/data/HIS_transactions.csv > ../HIS/data/HIS_frequent_patterns.txt

After finding frequent patterns, we then find the max patterns.
$ python freq_to_max_HIS.py
outputs a file to ./HIS/results/HIS_max_patterns.txt
______________________
To directly mine max pattern after running create_HIS_transactions.py
$ cd fpgrowth-c/fp-growth/src
$ make
$ ../fpgrowth-c/fpgrowth/src/fpgrowth -tm -s-20 -b, ./data/HIS_transactions.csv ./results/HIS_raw_max_patterns.txt

Then, clean the output.
$ python clean_fpgrowth_output.py
Outputs ./results/HIS_max_patterns.py

To rank pairs of words by mutual information,
$ python rank_word_pairs.py mi

We can use KL divergence to compute dissimilarities between each pair of symptom
and herb.
$ python kl_divergence.py norm
Add keyword norm to parse normalized data.

_____________NTU DATABASE_____________
$ python ntu_mine_transitive_t_scores.py
Run this to mine the transitive TCM-disease and gene-TCM transitive t-scores
from the NTU database.

____________EFFECTIVE TAGGING_____________
$ cd HIS
$ python discontinued_herbs.py
Writes out the time series for each patient and mines the discontinued herbs and
symptoms.
Currently, the definition of a discontinued element is if it does not appear
in the last two patient visits. A discontinued herb treats a symptom
successfully if their vectors are the same.
Also writes out to file successful_discontinued_herb_symptom_pairs.txt, which
contains all of the successful discontinued herbs, along with their counts, 
the corresponding symptom counts, and how often they count as successful
treatments.

$ python onset_herbs.py