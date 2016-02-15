### Author: Edward Huang

import subprocess

### This script runs the lda-c script by David M. Blei. We perform topic
### estimation on our TCM files.

if __name__ == '__main__':
    ## For original data.
    # for file_type in ['herb', 'syndrome', 'symptoms']:
    #     for k in [5, 10, 20, 50, 100]:

    #         ## This command is for the first time we run this script, to create
    #         ## the necessary directories.
    #         # mkdir_command = 'mkdir ./lda_results/%s_lda_k_%d' % (file_type, k)
    #         # subprocess.call(mkdir_command, shell=True)

    #         alpha = 1.0 / k
    #         command = './lda-c/lda est %f %d ./lda-c/settings.txt \
    #             ./data/lda_input_%s.txt random ./lda_results/%s_lda_k_%d/' % (alpha, k, file_type, file_type, k)
    #         subprocess.call(command, shell=True)


    # For ZRS data.
    for file_type in ['drugs', 'symptoms']:
        for k in [5, 10, 20, 50, 100]:

            ## This command is for the first time we run this script, to create
            ## the necessary directories.
            # mkdir_command = 'mkdir ./lda_results/ZRS_%s_lda_k_%d' % (file_type, k)
            # subprocess.call(mkdir_command, shell=True)

            alpha = 1.0 / k
            command = './lda-c/lda est %f %d ./lda-c/settings.txt \
                ./data/ZRS_lda_input_%s.txt random ./lda_results/ZRS_%s_lda_k_%d/' % (alpha, k, file_type, file_type, k)
            subprocess.call(command, shell=True)