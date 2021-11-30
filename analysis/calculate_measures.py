import os 
import re
import numpy as np
import pandas as pd
from cohortextractor import Measure
from analysis.utilities import get_date_input_file
from utilities import *


demographics = ['region', 'age_band', 'imd', 'sex', 'learning_disability', 'ethnicity']
sentinel_measures = ["qrisk2", "asthma", "copd", "sodium", "cholesterol", "alt", "tsh", "alt", "rbc", 'hba1c', 'systolic_bp', 'medication_review']

for file in OUTPUT_DIR.iterdir():
    if match_input_files(file):


    
        file_path = os.path.join('output', file)
        date = get_date_input_file(file)
        df = pd.read_feather(file_path)
        df['date'] = pd.to_datetime(date)

        

        for d in demographics:  
            if d=='age_band':
                    population = df.groupby(by=[d, 'date']).size().reset_index(name='population')


            else:

                population = df.groupby(by=['age_band', d, 'date']).size().reset_index(name='population')


            for measure in sentinel_measures:

                if d =='age_band':
                    event = df.groupby(by=[d, 'date'])[[measure, 'date']].sum().reset_index()

                    measures_df = population.merge(event, on=[d, 'date'])
                else:
                    event = df.groupby(by=['age_band', d, 'date'])[[measure, 'date']].sum().reset_index()

                    measures_df = population.merge(event, on=['age_band', d, 'date'])

                measures_df = measures_df[measures_df["age_band"] != "missing"]
                    
                measures_df = measures_df.replace({True: 1, False: 0})
                counts = measures_df.groupby(by=[d, "date"])[[measure, "population"]].sum().reset_index()
                
                if d == "age_band":
                    measures_df = calculate_rate_standardise(measures_df, measure, "population", standardise=False)
                else:
                    measures_df['rate_standardised'] = calculate_rate_standardise(measures_df, measure, "population", standardise=True, age_group_column="age_band")

                if d == "ethnicity":
                    measures_df = convert_ethnicity(measures_df)
                    

                if d == "age_band":
                    measures_df = measures_df.groupby(by=[d, "date"])["rate"].mean().reset_index()
                    
                else:
                    measures_df = measures_df.groupby(by=[d, "date"])["rate_standardised"].sum().reset_index()
                
                
                measures_df = measures_df.merge(counts, on=[d, "date"], how="outer")
                
                
                if d == 'sex':
                    measures_df = measures_df[measures_df['sex'].isin(['M', 'F'])]
                
                
                if d == 'age_band':
                    measures_df = redact_small_numbers(measures_df, 5, measure, "population", 'rate')
                
                else:

                    
                    measures_df = redact_small_numbers(measures_df, 5, measure, "population", 'rate_standardised')
                
                
                measures_df.to_csv(f'output/measure_{measure}_{d}_{date}.csv')
                

for sentinel_measure in sentinel_measures:
    for d in demographics:
        
        #load all measures for that sentinel measure and demographic
        data = []
        for file in os.listdir('output'):
            if f'measure_{sentinel_measure}_{d}' in file:
                df = pd.read_csv(os.path.join('output', file))
                data.append(df)
                
        df = pd.concat(data)
        df.to_csv(f'output/combined_measure_{sentinel_measure}_{d}.csv')
