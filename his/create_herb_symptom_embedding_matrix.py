### Author: Edward Huang

from collections import OrderedDict
import time

### This script constructs the matrix ready for embedding.
### Run time: 4 seconds.

def import_dictionary_file():
    '''
    Returns the dictionary produced by the file.
    Keys: herbs
    Values: lists of symptoms
    Also returns the list of all symptoms as a feature vector.
    '''

    # Keys are herbs, and values are the symptoms that the herbs treat.
    herb_symptom_dct = OrderedDict({})

    f = open('./data/herb_symptom_dictionary.txt', 'r')
    for i, line in enumerate(f):
        if i == 0:
            continue
        line = line.strip().split('\t')

        line_length = len(line)
        # Some symptoms don't have good English translations.
        assert line_length == 2 or line_length == 5
        if line_length == 2:
            herb, symptom = line
        elif line_length == 5:
            herb, symptom, english_symptom, db_src, db_src_id = line

        # Add to the herb dictionary.
        if herb in herb_symptom_dct:
            if symptom not in herb_symptom_dct[herb]:
                herb_symptom_dct[herb] += [symptom]
        else:
            herb_symptom_dct[herb] = [symptom]

        # Add to the symptom dictionary.
        if symptom in herb_symptom_dct:
            if herb not in herb_symptom_dct[symptom]:
                herb_symptom_dct[symptom] += [herb]
        else:
            herb_symptom_dct[symptom] = [herb]

    f.close()

    return herb_symptom_dct

def main():
    herb_symptom_dct = import_dictionary_file()

    feature_list = herb_symptom_dct.keys()

    out = open('./data/herb_symptom_embedding_matrix.txt', 'w')
    for row_feature in feature_list:

        # Get the elements associated with the current row.
        feature_elements = herb_symptom_dct[row_feature]

        # Assemble the feature vector.
        feature_vector = []
        for col_feature in feature_list:
            if col_feature in feature_elements:
                feature_vector += ['1']
            else:
                feature_vector += ['0']

        assert len(feature_vector) == len(feature_list)
                
        out.write('\t'.join(feature_vector) + '\n')    

    out.close()

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))