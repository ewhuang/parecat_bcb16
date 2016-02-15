### Author: Edward Huang


### This script takes the frequent patterns mined for the ZRS data and keeps
### only the closed patterns.

if __name__ == '__main__':

    max_patterns = []

    f = open('./results/ZRS_freq_patterns.txt', 'r')
    for line in f:
        # Parse file contents.
        line = line.split(', ')
        curr_pattern = set(line[:-1])
        freq = line[-1]

        # Check if the current pattern is a subset of something we have
        # previously seen. Also find the patterns which are bad.
        isMax = True
        bad_patterns = []
        for pattern in max_patterns:
            if curr_pattern < pattern:
                isMax = False
                break
            if curr_pattern > pattern:
                bad_patterns += [pattern]
        # Delete the bad patterns from the set.
        for pattern in bad_patterns:
            max_patterns.remove(pattern)
        if isMax:
            max_patterns += [curr_pattern]
    f.close()

    # Write out the closed patterns.
    f = open('./results/ZRS_freq_patterns.txt', 'r')
    out = open('./results/ZRS_max_patterns.txt', 'w')
    for line in f:
        # Parse file contents.
        new_line = line.split(', ')
        curr_pattern = set(new_line[:-1])
        freq = new_line[-1]
        if curr_pattern in max_patterns:
            out.write(line)
    out.close()
    f.close()