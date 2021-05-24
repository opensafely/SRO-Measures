import pandas as pd
import os


ethnicity_df = pd.read_feather('output/input_ethnicity.feather')


for file in os.listdir('output'):
    if file.startswith('input'):
        #exclude ethnicity
        if file.split('_')[1] not in ['ethnicity.csv', 'practice']:
            file_path = os.path.join('output', file)
            df = pd.read_feather(file_path)
            merged_df = df.merge(ethnicity_df, how='left', on='patient_id')
            
            merged_df.to_feather(file_path)