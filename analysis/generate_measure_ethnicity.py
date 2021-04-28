import os
import pandas as pd

ethnicity_data = []
for file in os.listdir('output'):

    if file.startswith('input'):
        #exclude ethnicity and practice
        if file.split('_')[1] not in ['ethnicity.csv', 'practice']:
            
            file_path = os.path.join('output', file)
            date = file.split('_')[1][:-4]
            df = pd.read_csv(file_path)
            df['date'] = date
            
            ethnicity_data.append(df)
    
            
ethnicity_df = pd.concat(ethnicity_data)

population = ethnicity_df.groupby(by=['age_band', 'ethnicity', 'date']).size().reset_index(name='population')

event = ethnicity_df.groupby(by=['age_band', 'ethnicity', 'date'])[['event', 'date']].sum().reset_index()

measures_df = population.merge(event, on=['age_band', 'ethnicity', 'date'])

measures_df.to_csv('output/measure_ethnicity.csv')