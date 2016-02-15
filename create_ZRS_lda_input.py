# coding: utf8
### Author: Edward Huang

from collections import OrderedDict

### This script takes in each of the three spreadsheets for traditional Chinese
### medicine, and creates files ready to be used by LDA-C.
### The data format is a file where each line is of the form:
### num_unique_terms term_1_index:count term_2_index:count... term_N_index:count

if __name__ == '__main__':
    for file_type in ['drugs', 'symptoms']:
        document_dct = OrderedDict({})
        target_vocab = []
        # Read in the target file.
        f = open('./data/norm_ZRS_patient_%s.txt' % file_type, 'r')
        for i, line in enumerate(f):
            # Skip header for drug file.
            if file_type == 'drugs' and i == 0:
                continue
            # Each document is considered as a visit to the doctor. The terms are
            # the targets, whether it is the set of herbs issued, or the symptoms
            # identified.
            line = line.split()
            visit_no = line[0]
            targets = line[1:]
            # Add to our vocabulary the current target.
            for target in targets:
                if target not in target_vocab:
                    target_vocab += [target]

                # Keep track of the counts for each term within each document.
                if visit_no in document_dct:
                    if target in document_dct[visit_no]:
                        document_dct[visit_no][target] += 1
                    else:
                        document_dct[visit_no][target] = 1
                else:
                    document_dct[visit_no] = OrderedDict({})
                    document_dct[visit_no][target] = 1
        f.close()

        # Write out the input file for LDA.
        out = open('./data/ZRS_lda_input_%s.txt' % file_type, 'w')
        for visit_no in document_dct:
            # Write out number of unique terms first.
            num_unique_terms = len(document_dct[visit_no])
            out.write('%d ' % num_unique_terms)

            for target in document_dct[visit_no]:
                target_count = str(document_dct[visit_no][target])
                out.write(str(target_vocab.index(target)) + ':' + target_count + ' ')
            out.write('\n')
        out.close()

        vocab_f = open('./data/ZRS_%s_vocab.txt' % file_type, 'w')
        for target in target_vocab:
            vocab_f.write('%s\n' % target)
        vocab_f.close()