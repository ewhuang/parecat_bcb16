# coding: utf8
### Author: Edward Huang

from collections import OrderedDict

### This script takes in each of the three spreadsheets for traditional Chinese
### medicine, and creates files ready to be used by LDA-C.
### The data format is a file where each line is of the form:
### num_unique_terms term_1_index:count term_2_index:count... term_N_index:count

if __name__ == '__main__':

    for file_type in ['herb', 'syndrome', 'symptoms']:
        document_dct = OrderedDict({})
        target_list = []
        # Read in the target file.
        f = open('./data/%s.tsv' % file_type, 'r')
        for i, line in enumerate(f):
            if i == 0:
                continue
            # Each document is considered as a visit to the doctor. The terms are
            # the targets, whether it is the set of herbs issued, or the symptoms
            # identified.
            case_no, inhospital_id, physician, target = line.split()

            # Add to our vocabulary the current target.
            if target not in target_list:
                target_list += [target]

            # Keep track of the counts for each term within each document.
            if inhospital_id in document_dct:
                if target in document_dct[inhospital_id]:
                    document_dct[inhospital_id][target] += 1
                else:
                    document_dct[inhospital_id][target] = 1
            else:
                document_dct[inhospital_id] = OrderedDict({})
                document_dct[inhospital_id][target] = 1
        f.close()

        # Write out the input file for LDA.
        out = open('./data/lda_input_%s.txt' % file_type, 'w')
        for inhospital_id in document_dct:
            # Write out number of unique terms first.
            num_unique_terms = len(document_dct[inhospital_id])
            out.write('%d ' % num_unique_terms)

            for target in document_dct[inhospital_id]:
                target_count = str(document_dct[inhospital_id][target])
                out.write(str(target_list.index(target)) + ':' + target_count + ' ')
            out.write('\n')
        out.close()

        vocab_f = open('./data/vocab_%s.txt' % file_type, 'w')
        for target in target_list:
            vocab_f.write('%s\n' % target)
        vocab_f.close()