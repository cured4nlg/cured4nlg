import random
import sys
import numpy as np
import pandas as pd
import nltk

TABLES_PATH = '../data/tables/'
# TEXTS_PATH = '../data/texts/'
TEXTS_PATH = '../data/texts-cleaned/cleaned-'

REGIONS = ['Africa', 'Americas', 'Eastern Mediterranean', 'Europe', 'South-East Asia', 'Western Pacific']

N_ENTS = 9  # max. number of columns across any table

def prepare_global(date):
    '''Linearise the global table for the given date.'''
    
    # Read text document containing global report.
    text_file = TEXTS_PATH + date + '-' + 'global' + '.txt'
    with open(text_file) as f:
        text = ' '.join(line.strip() for line in f.readlines())
        
    text = ' '.join(nltk.word_tokenize(text))
    
    # Read table file.
    table_file = TABLES_PATH + date + '-' + 'global' + '.tsv'
    table = pd.read_csv(table_file, sep='\t', index_col='WHO Region', dtype=str)
    table = table.fillna('-')
    rows = ['']

    for row in table.iterrows():
        fields = [table.index.name] + list(table.columns)
        values = [row[0]] + list(row[1])
        
        ent = ''
        for field, value in zip(fields, values):
            ent += value.replace(' ', '_') + '￨' + field.upper().replace(' ', '_') + ' '
            
        for _ in range(N_ENTS - len(fields)):
            ent += '<blank>￨<blank>' + ' '

        rows.append(ent)
        
    tail = date + '￨DATE ' + 'Global' + '￨REGION'
    for _ in range(8):
        tail += '<blank>￨<blank>' + ' '
        
    return '<ent>￨<ent> '.join(rows) + '<ent>￨<ent> ' + tail, text


def prepare_regional(date, region):
    '''Linearse the table for the give date and region.'''
    
    region_lc = region.lower().replace(' ', '-')
    
    text_file = TEXTS_PATH + date + '-' + region_lc + '.txt'
    
    with open(text_file) as f:
        text = ' '.join(line.strip() for line in f.readlines())

    text = ' '.join(nltk.word_tokenize(text))
    
    table_file = TABLES_PATH + date + '-' + region_lc + '.tsv'
    
    table = pd.read_csv(table_file, sep='\t', index_col='Reporting Country/Territory/Area', dtype=str)
    table = table.fillna('-')
    table = table.drop(['Transmission classification'], axis=1)  # drop last column for now

    rows = ['']

    for row in table.iterrows():
        fields = [table.index.name] + list(table.columns)
        values = [row[0]] + list(row[1])
        
        ent = ''
        for field, value in zip(fields, values):
            ent += value.replace(' ', '_') + '￨' + field.upper().replace(' ', '_') + ' '
            
        for _ in range(N_ENTS - len(fields)):
            ent += '<blank>￨<blank>' + ' '

        rows.append(ent)


    # Add corresponding row for the region from the global table.
    global_table_file = TABLES_PATH + date + '-' + 'global' + '.tsv'
    global_table = pd.read_csv(global_table_file, sep='\t', index_col='WHO Region', dtype=str)
    global_table = global_table.fillna('-')
    
    for row in global_table.iterrows():
        if row[0] != region:
            continue

        fields = [global_table.index.name] + list(global_table.columns)
        values = [row[0]] + list(row[1])
        
        ent = ''
        for field, value in zip(fields, values):
            ent += value.replace(' ', '_') + '￨' + field.upper().replace(' ', '_') + ' '
        
        for _ in range(N_ENTS - len(fields)):
            ent += '<blank>￨<blank>' + ' '

        rows.append(ent)
        
    tail = date + '￨DATE ' + region.replace(' ', '_') + '￨REGION'
    for _ in range(8):
        tail += '<blank>￨<blank>' + ' '

    return '<ent>￨<ent> '.join(rows) + '<ent>￨<ent> ' + tail, text


def create_src_trg(dates):
    src = []
    trg = []
    
    triples = []
    
    for date in dates:
        table, text = prepare_global(date)
        src.append(table)
        trg.append(text)
        
        for region in REGIONS:
            table, text = prepare_regional(date, region)
            src.append(table)
            trg.append(text)
    
    return src, trg

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


train_src, train_trg = create_src_trg(dates_train)
valid_src, valid_trg = create_src_trg(dates_valid)
test_src, test_trg = create_src_trg(dates_test)

write_to_file(train_src, 'data/train_input.txt')
write_to_file(train_trg, 'data/train_output.txt')

write_to_file(valid_src, 'data/valid_input.txt')
write_to_file(valid_trg, 'data/valid_output.txt')

write_to_file(test_src, 'data/test_input.txt')
write_to_file(test_trg, 'data/test_output.txt')