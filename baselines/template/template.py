# template.py - Create an update report using a pre-defined template for a specific date.
#
# Usage: python template.py date prev_date

import sys
import numpy as np
import pandas as pd


TABLES_PATH = '../data/tables/'
regions = ['Africa', 'Americas', 'Eastern Mediterranean', 'Europe', 'South-East Asia', 'Western Pacific']


def round_and_format(number):
    '''Round a number to nearest million or thousand and return it formatted appropriately.'''

    if number >= 10**6:
        number = int(str(number)[:-5]) / 10
        return str(number).replace('.0', '') + ' million'

    if number >= 10**4:
        number = int(str(number)[:-3])
        return str(number) + '000'

    if number >= 1000:
        number = int(str(number)[:-2])
        return str(number) + '00'

    return str(number)


def mutate_global_table(table):
    '''Modify the global table structure in the .tsv file mainly to 
       distribute information in a single cell across different cells
       and correctly handle data types.
    '''

    table['New cases in last 7 days'] = table['New cases in last 7 days (%)'].apply(lambda s: s.split()[0]).astype(int)
    table['New cases in last 7 days (%)'] = table['New cases in last 7 days (%)'].apply(lambda s: s.split()[1][1:-2]).astype(int)

    table['Cumulative cases'] = table['Cumulative cases (%)'].apply(lambda s: s.split()[0]).astype(int)
    table['Cumulative cases (%)'] = table['Cumulative cases (%)'].apply(lambda s: s.split()[1][1:-2]).astype(int)

    table['New deaths in last 7 days'] = table['New deaths in last 7 days (%)'].apply(lambda s: s.split()[0]).astype(int)
    table['New deaths in last 7 days (%)'] = table['New deaths in last 7 days (%)'].apply(lambda s: s.split()[1][1:-2]).astype(int)

    table['Cumulative deaths'] = table['Cumulative deaths (%)'].apply(lambda s: s.split()[0]).astype(int)
    table['Cumulative deaths (%)'] = table['Cumulative deaths (%)'].apply(lambda s: s.split()[1][1:-2]).astype(int)

    table['Change in new cases in last 7 days'] = table['Change in new cases in last 7 days'].apply(lambda s: int(s[:-1]))
    table['Change in new deaths in last 7 days'] = table['Change in new deaths in last 7 days'].apply(lambda s: int(s[:-1]))
    
    return table


def generate_global_report(date, prev_date):
    '''Generate global report using the template and the tabular data for the given date.'''

    with open('global_template.txt', 'r') as f:
        global_template = ' '.join(line.strip() for line in f.readlines())

    # Read file containing the table with global information.
    global_table_file = TABLES_PATH + date + '-' + 'global' + '.tsv'
    global_table = pd.read_csv(global_table_file, sep='\t', index_col='WHO Region')
    global_table = mutate_global_table(global_table)  # modify table to make further steps easier
    
    # New cases and deaths reported this week.
    global_new_cases = global_table.loc['Global', 'New cases in last 7 days']
    global_new_deaths = global_table.loc['Global', 'New deaths in last 7 days']
    
    # Cumulative cases reported this week.
    global_cumulative_cases = global_table.loc['Global', 'Cumulative cases']
    global_cumulative_deaths = global_table.loc['Global', 'Cumulative deaths']

    # Change in new cases reported this week.
    global_new_cases_change = global_table.loc['Global', 'Change in new cases in last 7 days']
    global_new_cases_change_descriptor = 'increased' if global_new_cases_change > 0 else 'decreased'
    global_new_cases_change = abs(global_new_cases_change)

    # Change in new deaths reported this week.
    global_new_deaths_change = global_table.loc['Global', 'Change in new deaths in last 7 days']
    global_new_deaths_change_descriptor = 'increased' if global_new_deaths_change > 0 else 'decreased'
    global_new_deaths_change = abs(global_new_deaths_change)
    

    global_table = global_table.drop(index='Global')
    
    # Most affected region.
    most_affected_region = global_table['New cases in last 7 days'].idxmax()
    most_affected_new_cases = global_table.loc[most_affected_region, 'New cases in last 7 days']
    most_affected_new_cases_share = global_table.loc[most_affected_region, 'New cases in last 7 days (%)']
    most_affected_cases_change = global_table.loc[most_affected_region, 'Change in new cases in last 7 days']
    most_affected_cases_change_descriptor = 'an increase' if most_affected_cases_change > 0 else 'a decrease'
    most_affected_cases_change = abs(most_affected_cases_change)
    most_affected_new_deaths = global_table.loc[most_affected_region, 'New deaths in last 7 days']
    
    # Changes reported in new cases across different regions.
    regions_with_increased_cases = sorted(global_table[global_table.loc[:, 'Change in new cases in last 7 days'] > 0].index)
    regions_with_decreased_cases = sorted(global_table[global_table.loc[:, 'Change in new cases in last 7 days'] < 0].index)
    regions_with_no_change_cases = sorted(global_table[global_table.loc[:, 'Change in new cases in last 7 days'] == 0].index)

    
    if len(regions_with_increased_cases) == 0:
        sentence_increased_cases = ''
        regions_with_increased_cases = ''
    else:
        sentence_increased_cases = 'Regions reporting an increase in new cases include '
        regions_with_increased_cases = ', '.join(regions_with_increased_cases)
        if regions_with_increased_cases.count(','):
            regions_with_increased_cases = ' and'.join(regions_with_increased_cases.rsplit(',', 1))
        sentence_increased_cases = ' ' + sentence_increased_cases + regions_with_increased_cases + '.'
        
    if len(regions_with_decreased_cases) == 0:
        sentence_decreased_cases = ''
        regions_with_decreased_cases = ''
    else:
        sentence_decreased_cases = 'Regions reporting a decline in new cases include '
        regions_with_decreased_cases = ', '.join(regions_with_decreased_cases)
        if regions_with_decreased_cases.count(','):
            regions_with_decreased_cases = ' and'.join(regions_with_decreased_cases.rsplit(',', 1))
        sentence_decreased_cases = ' ' + sentence_decreased_cases + regions_with_decreased_cases + '.'
    
    if len(regions_with_no_change_cases) == 0:
        sentence_no_change_cases = ''
        regions_with_no_change_cases = ''
    else:
        sentence_no_change_cases = ' reported no change in the number of new cases.'
        regions_with_no_change_cases = ', '.join(regions_with_no_change_cases)
        if regions_with_no_change_cases.count(','):
            regions_with_no_change_cases = ' and'.join(regions_with_no_change_cases.rsplit(',', 1))
        sentence_no_change_cases = ' ' + regions_with_decreased_cases + sentence_no_change_cases
        
    global_template += sentence_increased_cases + sentence_decreased_cases + sentence_no_change_cases
        
    # Changes reported in new deaths across different regions.
    regions_with_increased_deaths = sorted(global_table[global_table.loc[:, 'Change in new deaths in last 7 days'] > 0].index)
    regions_with_decreased_deaths = sorted(global_table[global_table.loc[:, 'Change in new deaths in last 7 days'] < 0].index)
    regions_with_no_change_deaths = sorted(global_table[global_table.loc[:, 'Change in new deaths in last 7 days'] == 0].index)

    
    if len(regions_with_increased_deaths) == 0:
        sentence_increased_deaths = ''
        regions_with_increased_deaths = ''
    else:
        sentence_increased_deaths = 'Regions reporting an increase in new deaths include '
        regions_with_increased_deaths = ', '.join(regions_with_increased_deaths)
        if regions_with_increased_deaths.count(','):
            regions_with_increased_deaths = ' and'.join(regions_with_increased_deaths.rsplit(',', 1))
        sentence_increased_deaths = ' '  + sentence_increased_deaths + regions_with_increased_deaths + '.'
        
    if len(regions_with_decreased_deaths) == 0:
        sentence_decreased_deaths = ''
        regions_with_decreased_deaths = ''
    else:
        sentence_decreased_deaths = 'Regions reporting a decline in new deaths include '
        regions_with_decreased_deaths = ', '.join(regions_with_decreased_deaths)
        if regions_with_decreased_deaths.count(','):
            regions_with_decreased_deaths = ' and'.join(regions_with_decreased_deaths.rsplit(',', 1))
        sentence_decreased_deaths = ' ' + sentence_decreased_deaths + regions_with_decreased_deaths + '.'
    
    if len(regions_with_no_change_deaths) == 0:
        sentence_no_change_deaths = ''
        regions_with_no_change_deaths = ''
    else:
        sentence_no_change_deaths = ' reported no change in the number of new deaths.'
        regions_with_no_change_deaths = ', '.join(regions_with_no_change_deaths)
        if regions_with_no_change_deaths.count(','):
            regions_with_no_change_deaths = ' and'.join(regions_with_no_change_deaths.rsplit(',', 1))
        sentence_no_change_deaths = ' ' + regions_with_decreased_deaths + sentence_no_change_deaths
        
    global_template += sentence_increased_deaths + sentence_decreased_deaths + sentence_no_change_deaths

    
    # Read file containing the tables with regional information.
    all_table = pd.concat([pd.read_csv(TABLES_PATH + date + '-' + region.lower().replace(' ', '-') + '.tsv', 
                                       sep='\t', index_col='Reporting Country/Territory/Area') 
                           for region in regions])
    
    prev_all_table = pd.concat([pd.read_csv(TABLES_PATH + prev_date + '-' + region.lower().replace(' ', '-') + '.tsv', 
                                            sep='\t', index_col='Reporting Country/Territory/Area') 
                                for region in regions])

    # Find the 5 countries reporting the highest number of cases
    df_highest_countries = all_table.drop(regions).nlargest(5, 'New cases in last 7 days')
    highest_countries = []
    
    sentence_highest_countries = ' The highest numbers of new cases were reported from '
    for country in df_highest_countries.iterrows():
        country_name = country[0]
        country_new_cases = country[1][0]
        country_prev_new_cases = prev_all_table.loc[country_name][0]
        country_new_cases_change = round(100.0 * (country_new_cases - country_prev_new_cases) / country_prev_new_cases)
        
        if country_new_cases_change > 0:
            country_new_cases_change = str(abs(country_new_cases_change)) + '%' + ' increase'
        elif country_new_cases_change < 0:
            country_new_cases_change = str(abs(country_new_cases_change)) + '%' + ' decrease'
        else:
            country_new_cases_change = 'similar to previous week'
        
        highest_countries.append(country_name + ' (' + str(country_new_cases) + ' new cases; ' + \
                                 country_new_cases_change + ')')
        
    highest_countries = ', '.join(highest_countries)
    highest_countries = ' and'.join(highest_countries.rsplit(',', 1))
    sentence_highest_countries += ' ' + highest_countries + '.'

    global_template += sentence_highest_countries
    
    return global_template.replace('{GLOBAL_NEW_CASES}', round_and_format(global_new_cases)) \
                          .replace('{GLOBAL_NEW_DEATHS}', round_and_format(global_new_deaths)) \
                          .replace('{GLOBAL_CUMULATIVE_CASES}', round_and_format(global_cumulative_cases)) \
                          .replace('{GLOBAL_CUMULATIVE_DEATHS}', round_and_format(global_cumulative_deaths)) \
                          .replace('{GLOBAL_NEW_CASES_CHANGE}', str(global_new_cases_change)) \
                          .replace('{GLOBAL_NEW_DEATHS_CHANGE}', str(global_new_deaths_change)) \
                          .replace('{GLOBAL_NEW_CASES_CHANGE_DESCRIPTOR}', str(global_new_cases_change_descriptor)) \
                          .replace('{GLOBAL_NEW_DEATHS_CHANGE_DESCRIPTOR}', str(global_new_deaths_change_descriptor)) \
                          .replace('{MOST_AFFECTED_REGION}', str(most_affected_region)) \
                          .replace('{MOST_AFFECTED_NEW_CASES}', round_and_format(most_affected_new_cases)) \
                          .replace('{MOST_AFFECTED_NEW_DEATHS}', round_and_format(most_affected_new_deaths)) \
                          .replace('{MOST_AFFECTED_CASES_CHANGE_DESCRIPTOR}', most_affected_cases_change_descriptor) \
                          .replace('{MOST_AFFECTED_CASES_CHANGE}', str(most_affected_cases_change)) \
                          .replace('{MOST_AFFECTED_NEW_CASES_SHARE}', str(most_affected_new_cases_share)) \
                          .replace('\n', ' ')


def generate_regional_report(date, prev_date, region):
    '''Generate regional report using the template and the tabular data for the given date and region.'''

    with open('regional_template.txt', 'r') as f:
        template = ' '.join(line.strip() for line in f.readlines())
        
    table_file = TABLES_PATH + date + '-' + region.lower().replace(' ', '-') + '.tsv'
    table = pd.read_csv(table_file, sep='\t', index_col='Reporting Country/Territory/Area')

    # Get an estimate for the population of each country to further calculate new cases per 100k population.
    table['Population estimate'] = 100000.0 * table['Cumulative cases'] / table['Cumulative cases per 100 thousand population']
    
    region_new_cases = table.loc[region, 'New cases in last 7 days']
    region_new_deaths = table.loc[region, 'New deaths in last 7 days']
    region_cumulative_cases = table.loc[region, 'Cumulative cases']
    region_cumulative_deaths = table.loc[region, 'Cumulative deaths']
    region_cumulative_cases_per_100k = table.loc[region, 'Cumulative cases per 100 thousand population']

    prev_table_file = TABLES_PATH + prev_date + '-' + region.lower().replace(' ', '-') + '.tsv'
    prev_table = pd.read_csv(prev_table_file, sep='\t', index_col='Reporting Country/Territory/Area')
    
    region_prev_new_cases = prev_table.loc[region, 'New cases in last 7 days']
    region_prev_new_deaths = prev_table.loc[region, 'New deaths in last 7 days']
    region_prev_cumulative_cases = prev_table.loc[region, 'Cumulative cases']
    region_prev_cumulative_deaths = prev_table.loc[region, 'Cumulative deaths']
    region_prev_cumulative_cases_per_100k = prev_table.loc[region, 'Cumulative cases per 100 thousand population']
    

    region_new_cases_change = round(100.0 * (region_new_cases - region_prev_new_cases) / region_prev_new_cases)
    region_new_cases_change_descriptor = 'increase' if region_new_cases_change > 0 else 'decrease'
    region_new_cases_change = abs(region_new_cases_change)
    region_new_deaths_change = round(100.0 * (region_new_deaths - region_prev_new_deaths) / region_prev_new_deaths)
    region_new_deaths_change_descriptor = 'increase' if region_new_deaths_change > 0 else 'decrease'
    region_new_deaths_change = abs(region_new_deaths_change)
    
    table = table.drop(index=region)
    
    # calculate new cases per 100k population and % change for most affected countries
    most_affected_countries_by_cases = table.nlargest(3, 'New cases in last 7 days')
    
    highest_cases = []
    
    for country in most_affected_countries_by_cases.iterrows():
        country_name = country[0]
        country_new_cases = int(country[1]['New cases in last 7 days'])
        country_prev_new_cases = max(int(prev_table.loc[country_name]['New cases in last 7 days']), 1)
        country_new_cases_change = round(100.0 * (country_new_cases - country_prev_new_cases) / country_prev_new_cases)
        
        country_population_estimate = country[1]['Population estimate']
        country_new_cases_per_100k = round(100000.0 * country_new_cases / country_population_estimate, 1)

        if country_new_cases_change > 0:
            country_new_cases_change = 'a ' + str(abs(country_new_cases_change)) + '% increase'
        elif country_new_cases_change < 0: 
            country_new_cases_change = 'a ' + str(abs(country_new_cases_change)) + '% decrease'
        else:
            country_new_cases_change = 'similar to previous week'
    
        highest_cases.append(country_name + ' (' + 
                             str(country_new_cases) + ' new cases; ' + 
                             str(country_new_cases_per_100k) + ' new cases per 100000 population; ' +
                             country_new_cases_change + ')')
        
    highest_cases = ', '.join(highest_cases)
    highest_cases = ' and'.join(highest_cases.rsplit(',', 1))
    
    # calculate new deaths per 100k population and % change for most affected countries
    most_affected_countries_by_deaths = table.nlargest(3, 'New deaths in last 7 days')
    
    highest_deaths = []
    
    for country in most_affected_countries_by_deaths.iterrows():
        country_name = country[0]
        country_new_deaths = int(country[1]['New deaths in last 7 days'])
        country_prev_new_deaths = max(int(prev_table.loc[country_name]['New deaths in last 7 days']), 1)
        country_new_deaths_change = round(100.0 * (country_new_deaths - country_prev_new_deaths) / country_prev_new_deaths)
        
        country_population_estimate = country[1]['Population estimate']
        country_new_deaths_per_100k = round(100000.0 * country_new_deaths / country_population_estimate, 1)

        if country_new_deaths_change > 0:
            country_new_deaths_change = 'a ' + str(abs(country_new_deaths_change)) + '%' + ' increase'
        elif country_new_deaths_change < 0: 
            country_new_deaths_change = 'a ' + str(abs(country_new_deaths_change)) + '%' + ' decrease'
        else:
            country_new_deaths_change = 'similar to previous week'
    
        highest_deaths.append(country_name + ' (' + 
                             str(country_new_deaths) + ' new deaths; ' + 
                             str(country_new_deaths_per_100k) + ' new deaths per 100000 population; ' +
                             country_new_deaths_change + ')')
        
    highest_deaths = ', '.join(highest_deaths)
    highest_deaths = ' and'.join(highest_deaths.rsplit(',', 1))


    return template.replace('{REGION_NEW_CASES}', round_and_format(region_new_cases)) \
                   .replace('{REGION_NEW_DEATHS}', round_and_format(region_new_deaths)) \
                   .replace('{REGION}', str(region)) \
                   .replace('{REGION_NEW_CASES_CHANGE}', str(region_new_cases_change)) \
                   .replace('{REGION_NEW_DEATHS_CHANGE}', str(region_new_deaths_change)) \
                   .replace('{REGION_NEW_CASES_CHANGE_DESCRIPTOR}', str(region_new_cases_change_descriptor)) \
                   .replace('{REGION_NEW_DEATHS_CHANGE_DESCRIPTOR}', str(region_new_deaths_change_descriptor)) \
                   .replace('{MOST_AFFECTED_COUNTRIES_BY_CASES}', highest_cases) \
                   .replace('{MOST_AFFECTED_COUNTRIES_BY_DEATHS}', highest_deaths) \
                   .replace('\n', ' ')
    

if __name__ == '__main__':
    date, prev_date = sys.argv[1:3]

    # Generate global report.
    global_report = generate_global_report(date, prev_date)

    # Write to file.
    with open(date + '-global.out', 'w') as f:
        f.write(global_report)

    # Generate regional reports.
    for region in regions:
        regional_report = generate_regional_report(date, prev_date, region)

        # Write to file.
        with open(date + '-' + region.lower().replace(' ', '-') + '.out', 'w') as f:
            f.write(regional_report)
