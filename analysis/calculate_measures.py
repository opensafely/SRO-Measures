import os 
import re
import numpy as np
import pandas as pd
from cohortextractor import Measure

def calculate_imd_group(df):
    imd_column = pd.to_numeric(df["imd"])
    df["imd"] = pd.qcut(imd_column, q=5,duplicates="drop", labels=['Most deprived', '2', '3', '4', 'Least deprived'])      
    
    return df

def redact_small_numbers(df, n, counts_columns):
    """
    Takes counts df as input and suppresses low numbers.  Sequentially redacts
    low numbers from each column until count of redcted values >=n.
    
    df: input df
    n: threshold for low number suppression
    counts_columns: list of columns in df that contain counts to be suppressed.
    """
    
    def suppress_column(column):    
        suppressed_count = column[column<=n].sum()
        column = column.where(column<=n, np.nan)
        
        while suppressed_count <=n:
            suppressed_count += column.min()
            column.iloc[column.idxmin()] = np.nan   
        return column
        
    for column in counts_columns:
        df[column] = suppress_column(df[column])
    
    return df   

def calculate_rate_standardise(df, numerator, denominator, rate_per=1000, standardise=False, age_group_column=False):
    """
    df: measures df
    numerator: numerator column in df
    denominator: denominator column in df
    groupby: list containing columns to group by when calculating rate
    rate_per: defines level of rate measure
    standardise: Boolean, whether to apply age standardisation
    age_group_column: if applying age standardisation, defines column that is age
    """
    rate = df[numerator]/(df[denominator]/rate_per)
    df['rate'] = rate
    
    def standardise_row(row):
    
        age_group = row[age_group_column]
        rate = row['rate']
        
        
        standardised_rate = rate * standard_pop.loc[str(age_group)]
        return standardised_rate
    
   
    if standardise:
        path = "notebooks/european_standard_population.csv"
        standard_pop = pd.read_csv(path)
        
        age_band_grouping_dict = {
            '0-4 years': '0-19',
            '5-9 years': '0-19',
            '10-14 years': '0-19',
            '15-19 years': '0-19',
            '20-24 years': '20-29',
            '25-29 years': '20-29',
            '30-34 years': '30-39',
            '35-39 years': '30-39',
            '40-44 years': '40-49',
            '45-49 years': '40-49',
            '50-54 years': '50-59',
            '55-59 years': '50-59',
            '60-64 years': '60-69',
            '65-69 years': '60-69',
            '70-74 years': '70-79',
            '75-79 years': '70-79',
            '80-84 years': '80+',
            '85-89 years': '80+',
            '90plus years': '80+',
        }

        standard_pop = standard_pop.set_index('AgeGroup')
        standard_pop = standard_pop.groupby(age_band_grouping_dict, axis=0).sum()
        standard_pop = standard_pop.reset_index().rename(columns={'index': 'AgeGroup'})


        standard_pop["AgeGroup"] = standard_pop["AgeGroup"].str.replace(" years", "")
        standard_pop = standard_pop.set_index("AgeGroup")["EuropeanStandardPopulation"]
        standard_pop = standard_pop / standard_pop.sum()
        
        #apply standardisation
        df['rate_standardised'] = df.apply(standardise_row, axis=1)
        
    return df

def convert_ethnicity(df):
    ethnicity_codes = {1.0: "White", 2.0: "Mixed", 3.0: "Asian", 4.0: "Black", 5.0:"Other", np.nan: "unknown", 0: "unknown"}

    df = df.replace({"ethnicity": ethnicity_codes})
    return df




demographics = ['region', 'age_band', 'imd', 'sex', 'learning_disability', 'ethnicity']
sentinel_measures = ['systolic_bp']


for file in os.listdir('output'):

    if file.startswith('input'):
        #exclude ethnicity and practice
        if file.split('_')[1] not in ['ethnicity.feather', 'practice']:

            file_path = os.path.join('output', file)
            date = re.match(r"input_(?P<date>\d{4}-\d{2}-\d{2})\.feather", file)
            df = pd.read_feather(file_path)
            df['date'] = pd.to_datetime(date.group("date"))

           
            df = calculate_imd_group(df)

            for d in demographics:  
                if d=='age_band':
                     population = df.groupby(by=[d, 'date', 'practice']).size().reset_index(name='population')


                else:

                    population = df.groupby(by=['age_band', d, 'date', 'practice']).size().reset_index(name='population')


                for measure in sentinel_measures:

                    if d =='age_band':
                        event = df.groupby(by=[d, 'date', 'practice'])[[measure, 'date']].sum().reset_index()

                        measures_df = population.merge(event, on=[d, 'date', 'practice'])
                    else:
                        event = df.groupby(by=['age_band', d, 'date', 'practice'])[[measure, 'date']].sum().reset_index()

                        measures_df = population.merge(event, on=['age_band', d, 'date', 'practice'])

                    measures_df = measures_df[measures_df["age_band"] != "missing"]

                    measures_df = redact_small_numbers(measures_df, 5, [measure, "population"])

                    if d == "age_band":
                        measures_df = calculate_rate_standardise(measures_df, measure, "population", standardise=False)
                    else:
                        measures_df = calculate_rate_standardise(measures_df, measure, "population", standardise=True, age_group_column="age_band")

                    if d == "ethnicity":
                        measures_df = convert_ethnicity(measures_df)

                    if d == "age_band":
                        measures_df = measures_df.groupby(by=[d, "date", "practice"])["rate"].mean().reset_index()
                        measures_df = measures_df.groupby(by=[d, "date"])["rate"].median().reset_index()
                    else:
                        measures_df = measures_df.groupby(by=[d, "date", "practice"])["rate_standardised"].mean().reset_index()
                        measures_df = measures_df.groupby(by=[d, "date"])["rate_standardised"].median().reset_index()

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
        df.to_csv(f'output/combined_measure_{measure}_{d}.csv')
