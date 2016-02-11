Author: Edward Huang

First, process each of the three spreadsheets to create an input file to be sent
into LDA.

>>> python preprocess_raw_data.py

Then, run lda_script.py to run LDA on the inputs we prepared.
If it is the first time running the script, we must uncomment lines 14 and 15 to
make the directories.

>>> python lda_script.py

Lastly, we run print_topics.py to output the topic modeling results.

>>> python print_topics.py