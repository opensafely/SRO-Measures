import os
import pandas as pd
from datetime import datetime
import os
from collections import Counter
from utilities import *


# get total number of practices by region to look at backend coverage
# source: https://digital.nhs.uk/data-and-information/publications/statistical/patients-registered-at-a-gp-practice/metadata#gp-reg-pat-prac-map
practice_df = pd.read_csv('analysis/gp-reg-pat-prac-map.csv')
num_practices_region = practice_df.groupby(by='COMM_REGION_NAME')['PRACTICE_CODE'].nunique().reset_index()
num_practices_region.to_csv('output/practice_region_total_count.csv')

dates_list = []

full_df = pd.read_feather(os.path.join('output', 'input_2019-01-01.feather'))
full_df = full_df.set_index('patient_id')


for file in sorted(os.listdir('output')):
    if match_input_files(file):

        date = get_date_input_file(file)
        datetime_object = pd.to_datetime(date)
        dates_list.append(datetime_object)
        

        df = pd.read_feather(os.path.join('output', file))
        df = df.set_index('patient_id')
        #update existing values in full_df
        full_df.update(df)
        
        #add new rows to full_df
        existing_id = list(full_df.index) 
        df = df[~df.index.isin(existing_id)]
    
        
        full_df = pd.concat([full_df, df])

    

full_df = calculate_imd_group(full_df)

unique_practices = full_df['practice'].unique()

total_count_df = pd.DataFrame([['total', len(full_df)], ['practice', len(unique_practices)]], columns=['pop', 'count'])
total_count_df.to_csv('output/total_count.csv')


practices_by_region = full_df.groupby(by='region')['practice'].nunique().reset_index()
practices_by_region.to_csv('output/practice_region_count.csv')


for column in ['sex', 'age_band', 'ethnicity', 'imd', 'region', 'learning_disability']:
    count = Counter(full_df[column])
    count_df = pd.DataFrame.from_dict(count, orient='index')
    count_df.to_csv(f'output/{column}_count.csv')
