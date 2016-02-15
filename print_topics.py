### Author: Edward Huang

import subprocess
import math

### This script prints out the topics for each of the runs we made.

N_WORDS = 20

if __name__ == '__main__':
    # for file_type in ['herb', 'syndrome', 'symptoms']:
    #     vocab_file_name = './data/vocab_%s.txt' % file_type
    #     for k in [5, 10, 20, 50, 100]:
    #         beta_file_name = './lda_results/%s_lda_k_%d/final.beta' % (file_type, k)
    #         norm_beta_file_name = './lda_results/%s_lda_k_%d/normalized_final.beta' % (file_type, k)
            
    #         # First, normalize the beta files.
    #         mean_prob_lst = []
    #         normalized_probs = []
    #         f = open(beta_file_name, 'r')
    #         for line in f:
    #             line = [math.exp(float(prob)) for prob in line.split()]
    #             normalized_probs += [line]
    #             mean_prob_lst += line
    #         f.close()
    #         mean_prob = sum(mean_prob_lst) / float(len(mean_prob_lst))

    #         out = open(norm_beta_file_name, 'w')
    #         for i, e in enumerate(normalized_probs):
    #             line = [str(prob - mean_prob) for prob in e]
    #             out.write(' '.join(line) + '\n')
    #         out.close()

    #         command = 'python ./lda-c/topics.py %s %s %d > ./lda_topics/%s_topics_k_%d.txt' % (norm_beta_file_name, vocab_file_name, N_WORDS, file_type, k)

    #         subprocess.call(command, shell=True)

    for file_type in ['drugs', 'symptoms']:
        vocab_file_name = './data/ZRS_%s_vocab.txt' % file_type
        for k in [5, 10, 20, 50, 100]:
            beta_file_name = './lda_results/ZRS_%s_lda_k_%d/final.beta' % (file_type, k)
            norm_beta_file_name = './lda_results/ZRS_%s_lda_k_%d/normalized_final.beta' % (file_type, k)
            
            # First, normalize the beta files.
            mean_prob_lst = []
            normalized_probs = []
            f = open(beta_file_name, 'r')
            for line in f:
                line = [math.exp(float(prob)) for prob in line.split()]
                normalized_probs += [line]
                mean_prob_lst += line
            f.close()
            mean_prob = sum(mean_prob_lst) / float(len(mean_prob_lst))

            out = open(norm_beta_file_name, 'w')
            for i, e in enumerate(normalized_probs):
                line = [str(prob - mean_prob) for prob in e]
                out.write(' '.join(line) + '\n')
            out.close()

            command = 'python ./lda-c/topics.py %s %s %d > ./ZRS_lda_topics/ZRS_%s_topics_k_%d.txt' % (norm_beta_file_name, vocab_file_name, N_WORDS, file_type, k)

            subprocess.call(command, shell=True)