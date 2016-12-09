### Author: Edward Huang

## Preprocessing

1.  First, process each of the three spreadsheets to create an input file to be 
    sent into LDA.

    ```bash
    $ python preprocess_raw_data.py
    ```

2.  Then, run lda_script.py to run LDA on the inputs we prepared. If it is the
    first time running the script, we must uncomment lines 14 and 15 to make the
    directories.

    ```bash
    $ python lda_script.py
    ```

3.  Use the first block to run for the original data set. Lastly, we run
    print_topics.py to output the topic modeling results.

    ```bash
    $ python print_topics.py
    ```

    Use the first block for original data.

## ZRS Data

1.  First, download the ZRS data.

    ```bash
    $ python preprocess_ZRS_data
    ```

    Outputs a file, ZRS_patient_symptoms.txt. Each symptom is sorted by a visit
    id number.

2.  The second file, ZRS_patient_drugs.txt, can simply be copied from the
    appropriate columns from the raw excel file.
    Next, we normalize the data.

    ```bash
    $ python normalize_ZRS_data.py
    ```

3.  It uses a similar technique to IDF to remove symptoms or drugs that appear
    too frequently.

    ```bash
    $ python mine_ZRS_frequent_pattersn.py
    ```

4.  Outputs a file, ZRS_freq_patterns.txt, which contains the frequent patterns
    and their support on each newline.

    ```bash
    $ python filter_ZRS_frequent_patterns.py
    ```

5.  Outputs norm_ZRS_freq_patterns.txt, which reformats each frequent pattern
    into a drug, symptom set relationship, along with their previous support.

    For topic modeling, run LDA for symptoms and drugs independently.

    ```bash
    $ python create_ZRS_lda_input.py
    ```

    ```bash
    $ python lda_script.py
    ```

    Use the second block to run for ZRS data.

6.  Lastly, print topics.
    
    ```bash
    $ python print_topics.py
    ```

    Also use the second block to run for ZRS data.

## HIS Data

1.  Takes the original HIS spreadsheet, and takes the proper columns. Sent the
    text to Sheng for interpretation, and received HIS_clean_data.txt.
    Remove the � character from the clean_data.

    ```bash
    $ python format_HIS_data.py
    ```

2.  This creates a csv file where each row is a transaction, and the items are
    the indices of the symptoms or herbs as they appeared in the raw data.
    Delete the rows that the script prints out. These rows have no herbs. Run
    the script again.

    ```bash
    $ python create_HIS_transactions.py
    ```

##  FP growth

1.  Next, we run FP Growth to find frequent patterns.

    ```bash
    $ cd python-fp-growth-master
    $ python -m fp_growth -s 5 ../HIS/data/HIS_transactions.csv > ../HIS/data/HIS_frequent_patterns.txt
    ```

2.  After finding frequent patterns, we then find the max patterns.
    
    ```bash
    $ python freq_to_max_HIS.py
    ```

    outputs a file to ./HIS/results/HIS_max_patterns.txt

##  Directly mine max patterns.

1.  To directly mine max pattern after running create_HIS_transactions.py

    ```bash
    $ cd fpgrowth-c/fp-growth/src
    $ make
    $ ../fpgrowth-c/fpgrowth/src/fpgrowth -tm -s-20 -b, ./data/HIS_transactions.csv ./results/HIS_raw_max_patterns.txt
    ```
2.  Then, clean the output.

    ```bash
    $ python clean_fpgrowth_output.py
    ```

    Outputs ./results/HIS_max_patterns.py

3.  To rank pairs of words by mutual information,

    ```bash
    $ python rank_word_pairs.py mi
    ```

4.  We can use KL divergence to compute dissimilarities between each pair of
    symptom and herb.

    ```bash
    $ python kl_divergence.py norm
    ```

    Add keyword norm to parse normalized data.

## NTU Database (unused)

```bash
$ python ntu_mine_transitive_t_scores.py
```

Run this to mine the transitive TCM-disease and gene-TCM transitive t-scores
from the NTU database.

## Effective Tagging (unused)

```bash
$ cd HIS
$ python discontinued_herbs.py
```

Writes out the time series for each patient and mines the discontinued herbs and symptoms. Currently, the definition of a discontinued element is if it does not appear in the last two patient visits. A discontinued herb treats a symptom successfully if their vectors are the same. Also writes out to file successful_discontinued_herb_symptom_pairs.txt, which contains all of the successful discontinued herbs, along with their counts, the corresponding symptom counts, and how often they count as successful treatments.

```bash
$ python onset_herbs.py
```

Finds which herbs have replaced other herbs. Basically, two herbs must combine to exactly equal a symptom vector. Also, the replaced herb's last 1 must be right before the onset herb's first one.

```bash
$ python get_time_series_statistics.py
```

Outputs files for side effect mining, disease complication mining, and herb-symptom treatment mining.


## Clustering (BCB PaReCat)

1.  Cluster on patient records using k-means, spectral, and agglomerative.

    ```bash
    $ python cluster_records.py symptoms/herbs/both tf/no_tf top/section/subsection
    ```

2.  To create the matrix for embedding.
    
    ```bash
    $ python create_herb_symptom_embedding_matrix.py
    ```

3.  Uses the similarity scores from the embedding vectors to improve clustering.

    ```bash
    $ python cluster_with_embedding.py symptoms/herbs/both top/section/subsection average/complete full/partial sim_threshold
    ```

4.  Clusters on the stomach disease data, and finds the symptoms and herbs.

    ```bash
    $ python stomach_data_clustering.py symptoms/herbs/both average/complete    sim_threshold num_clusters
    ```

    The best parameters are already tuned.