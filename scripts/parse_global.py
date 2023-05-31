import sys

for line in sys.stdin:
    fields = line.strip().split('\t')
    
    if not line.startswith('WHO'):
        fields[1] += ' (' + fields[2] + '%)'
        fields[3] += '%'
        fields[4] += ' (' + fields[5] + '%)'
        fields[6] += ' (' + fields[7] + '%)'
        fields[8] += '%'
        fields[9] += ' (' + fields[10] + '%)'

    print('\t'.join([fields[0], fields[1], fields[3], fields[4], fields[6], fields[8], fields[9]]))
