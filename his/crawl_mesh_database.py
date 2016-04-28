### Author: Edward Huang

import time
import urllib

### This script crawls the MeSH database and makes edges for each of the
### symptoms.

url_format = 'http://www.ncbi.nlm.nih.gov/mesh/?term=%s&report=Full&format=text'

# Go through the dictionary and get the MeSH ID's.
def get_mesh_ids():
    mesh_ids = []
    f = open('./data/herb_symptom_dictionary.txt', 'r')
    for i, line in enumerate(f):
        if i == 0:
            continue
        line = line.strip().split('\t')
        if 'MeSH' in line:
            mesh_ids += [line[4]]
    f.close()
    return mesh_ids

# Goes through the tree list and makes an edge between each parent and each
# child.
def process_tree(tree, symptom):
    tree = tree.strip().split('\n')
    # List of pairs, where the first element has an edge to the second element,
    # or the first element is the parent of the second element.
    edge_list = []
    parent_node = ''
    previous_tab_size = -22
    for node in tree:
        tab_size = len(node) - len(node.lstrip())
        if previous_tab_size == tab_size:
            print 'problem problem', symptom
            exit()
        node = node.strip().lower()
        if parent_node == '':
            parent_node = node
            continue
        edge_list += [(parent_node, node)]
        parent_node = node
        previous_tab_size = tab_size
        # If we have reached the target symptom, return the edge list.
        if node == symptom:
            return edge_list

# Gets the symptom name from the first block of html.
def get_symptom(html):
    symptom = html[0]
    symptom = symptom[symptom.index('1: ') + len('1: '):]
    symptom = symptom[:symptom.index('\n')].lower()
    return symptom

def main():
    # Contains all of the parent-child relationships in all symptom trees.
    master_edge_list = []
    mesh_ids = get_mesh_ids()

    # Progress variables.
    progress_counter = 0.0
    num_pages = len(mesh_ids)

    for mesh_id in mesh_ids:
    # for mesh_id in ['D020521']:
        # Read in page html.
        f = urllib.urlopen(url_format % mesh_id)
        html = f.read().split('All MeSH Categories')

        # Get the symptom name.
        symptom = get_symptom(html)
        # Get the edge list for each tree in the symptom html page.
        for tree in html[1:]:
            edge_list = process_tree(tree, symptom)
            for edge in edge_list:
                if edge not in master_edge_list:
                    master_edge_list += [edge]
        f.close()

        # Update progress.
        progress_counter += 1
        print 'Progress: %f%%...' % (progress_counter / num_pages)

    # Write out to file.
    out = open('./results/crawled_mesh_symptom_edges.txt', 'w')
    out.write('parent\tchild\n')
    for (parent, node) in master_edge_list:
        out.write('%s\t%s\n' % (parent, node))
    out.close()

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))