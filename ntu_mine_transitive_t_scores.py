### Author: Edward Huang

import urllib2
import re

### This script crawls the NTU TCM database and gets the transitive
### associations for each disease.

if __name__ == '__main__':
    url_to_scrape_pre = 'http://tcm.lifescience.ntu.edu.tw/HanMedDBsearch_association.cgi?field='
    url_to_scrape_suf = '&collocation=tcm_gene_disease_transitive&type=disease'

    marker = 'select name=confidence_tcm_gene'
    # for i in range(1, 3361):

    out = open('./data/transitive_correlations.txt', 'w')
    # Loop from 1 to 3360.
    for i in range(1, 3361):
        r = urllib2.urlopen(url_to_scrape_pre + str(i) + url_to_scrape_suf)
        # Read the page source.
        page_source = r.read()
        if marker not in page_source:
            continue
        index = page_source.index(marker)
        page_source = page_source[index:]
        result = re.findall('>(.*)<', page_source)

        page_source = '\n'.join(result)

        disease_entries = []
        tcm_entries = []
        gene_entries = []
        disease_t_entries = []
        gene_t_entries = []

        tcm_and_gene = re.findall('query_way=med>(.*)</a>', page_source)
        diseases = re.findall('query_way=disease>(.*)</a>', page_source)
        t_values = re.findall('font color=red>(.*)</font>', page_source)
        # Get the entities for each category.
        for html_str in tcm_and_gene:
            assert 'gene_id' in html_str
            herb = html_str[:html_str.index('<')]
            gene = html_str[html_str.index('gene_id') + len('gene_id>'):]
            tcm_entries += [herb]
            gene_entries += [gene]
            # print herb, gene
        for html_str in t_values:
            disease_and_tcm_t = html_str[:html_str.index('<')]
            tcm_and_gene_t = html_str[html_str.index('color=red>') + len('color=red>'):]
            disease_t_entries += [disease_and_tcm_t]
            gene_t_entries += [tcm_and_gene_t]

        # Write out to file.
        for i in range(len(diseases)):
            out.write('%s\t%s\t%s\t%s\t%s\n' % (diseases[i], tcm_entries[i], gene_entries[i],
                disease_t_entries[i], gene_t_entries[i]))
    out.close()