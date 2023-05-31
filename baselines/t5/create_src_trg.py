import random
import sys
import numpy as np
import pandas as pd

TABLES_PATH = '../data/tables/'
# TEXTS_PATH = '../data/texts/'
TEXTS_PATH = '../data/texts-cleaned/cleaned-'

REGIONS = ['Africa', 'Americas', 'Eastern Mediterranean', 'Europe', 'South-East Asia', 'Western Pacific']


def linearise_global(date, shuffle=False, subset=0):
    '''Linearise the global table for the given date.'''
    
    # Read text document containing global report.
    text_file = TEXTS_PATH + date + '-' + 'global' + '.txt'
    with open(text_file) as f:
        text = ' '.join(line.strip() for line in f.readlines())
    
    # Read table file.
    table_file = TABLES_PATH + date + '-' + 'global' + '.tsv'
    table = pd.read_csv(table_file, sep='\t', index_col='WHO Region', dtype=str)
    table = table.fillna('-')
    
    rows = []

    for row in table.iterrows():   # Linearise rows into a sequence
        rows.append(row[0] + ' ' + ' '.join(row[1]))
        
    if subset:
        rows = rows[:min(len(rows), subset)]
    
    if shuffle:
        random.shuffle(rows)
        
    rows = ['', ' '.join(list(table.columns))] + rows
    header = '[DATE] ' + date + ' [REGION] ' + 'Global '

    return 'Table to text: ' + header + ' [ROW] '.join(rows).strip(), text

def linearise_regional(date, region, shuffle=False, subset=0):
    '''Linearse the table for the give date and region.'''
    
    region_lc = region.lower().replace(' ', '-')
    
    text_file = TEXTS_PATH + date + '-' + region_lc + '.txt'
    
    with open(text_file) as f:
        text = ' '.join(line.strip() for line in f.readlines())

    
    table_file = TABLES_PATH + date + '-' + region_lc + '.tsv'
    
    table = pd.read_csv(table_file, sep='\t', index_col='Reporting Country/Territory/Area', dtype=str)
    table = table.fillna('-')
    table = table.drop(['Transmission classification'], axis=1)  # drop last column for now
    
    rows = []

    for row in table.iterrows():
        rows.append(row[0] + ' ' + ' '.join(row[1]))
        
    if subset:
        rows = rows[:min(len(rows), subset)]
        
    if shuffle:
        random.shuffle(rows)
        
    rows = ['', ' '.join(list(table.columns))] + rows
    header = '[DATE] ' + date + ' [REGION] '

    # Add corresponding row for the region from the global table.
    global_table_file = TABLES_PATH + date + '-' + 'global' + '.tsv'
    global_table = pd.read_csv(global_table_file, sep='\t', index_col='WHO Region', dtype=str)
    global_table = global_table.fillna('-')
    global_row = ' [TOTAL] '.join(' '.join([key, value]) for key, value in table.loc[region].to_dict().items())

    return 'Table to text: ' + header + region + ' [TOTAL] ' + global_row + ' ' + ' [ROW] '.join(rows).strip(), text

def table_to_triples(date, region):
    '''Convert a table to triples for evaluation with the PARENT metric.'''
    
    triples = []
    
    region_lc = region.lower().replace(' ', '-')
    table_file = TABLES_PATH + date + '-' + region_lc + '.tsv'
    table = pd.read_csv(table_file, sep='\t')
    
    if region != 'global':
        table = table.drop(['Transmission classification'], axis=1)  # drop last column for now

    for row in table.iterrows():
        attributes = list(row[1].index)
        values = list(map(str, row[1].values))
        for attribute, value in zip(attributes[1:], values[1:]):
            triples.append('|||'.join([values[0], attribute, value]))
    
    return '\t'.join(triples)

def create_src_trg(dates):
    src = []
    trg = []
    
    triples = []
    
    for date in dates:
        table, text = linearise_global(date)
        src.append(table)
        trg.append(text)
        triples.append(table_to_triples(date, 'global'))
        
        for region in REGIONS:
            table, text = linearise_regional(date, region)
            src.append(table)
            trg.append(text)
            triples.append(table_to_triples(date, region))
    
    return src, trg, triples

def write_to_file(lines, filename):
    with open(filename, 'w') as f:
        f.write('\n'.join(lines))


# Find table and text files for training, validation and test sets.
with open('../data/dates.train.txt') as f:
    dates_train = sorted(line.strip() for line in f.readlines())
with open('../data/dates.valid.txt') as f:
    dates_valid = sorted(line.strip() for line in f.readlines())
with open('../data/dates.test.txt') as f:
    dates_test = sorted(line.strip() for line in f.readlines())


train_src, train_trg, train_triples = create_src_trg(dates_train)
valid_src, valid_trg, valid_triples = create_src_trg(dates_valid)
test_src, test_trg, test_triples = create_src_trg(dates_test)

write_to_file(train_src, 'data/train.clean.src')
write_to_file(train_trg, 'data/train.clean.trg')
write_to_file(train_triples, 'data/train.clean.triples')
write_to_file(valid_src, 'data/valid.clean.src')
write_to_file(valid_trg, 'data/valid.clean.trg')
write_to_file(valid_triples, 'data/valid.clean.triples')
write_to_file(test_src, 'data/test.clean.src')
write_to_file(test_trg, 'data/test.clean.trg')
write_to_file(test_triples, 'data/test.clean.triples')
