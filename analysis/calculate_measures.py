import os 
import re
import numpy as np
import pandas as pd
from cohortextractor import Measure

def calculate_imd_group(df):
    imd_column = pd.to_numeric(df["imd"])
    df["imd"] = pd.qcut(imd_column, q=5,duplicates="drop", labels=['Most deprived', '2', '3', '4', 'Least deprived'])      
    
    return df

def redact_small_numbers(df, n, numerator, denominator, rate_column):
    """
    Takes counts df as input and suppresses low numbers.  Sequentially redacts
    low numbers from numerator and denominator until count of redcted values >=n.
    Rates corresponding to redacted values are also redacted.
    
    df: input df
    n: threshold for low number suppression
    numerator: numerator column to be redacted
    denominator: denominator column to be redacted
    """
    
    def suppress_column(column):    
        suppressed_count = column[column<=n].sum()
        
        #if 0 dont need to suppress anything
        if suppressed_count == 0:
            pass
        
        else:
            df[column.name][df[column.name]<=n] = np.nan
            

            while suppressed_count <=n:
                suppressed_count += column.min()
                column.iloc[column.idxmin()] = np.nan   
        return column
    
    
    for column in [numerator, denominator]:
        df[column] = suppress_column(df[column])
    
    df[rate_column][(df[numerator].isna())| (df[denominator].isna())] = np.nan
    
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

    rate = df[numerator].div(df[denominator].where(df[denominator] != 0, np.nan))*1000
    
    df['rate'] = rate
    
    def standardise_row(row):
    
        age_group = row[age_group_column]
        rate = row['rate']
        
        
        standardised_rate = rate * standard_pop.loc[str(age_group)]
        return standardised_rate
    
   
    if standardise:
        path = "european_standard_population.csv"
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

        merged_df = df.merge(standard_pop, left_on='age_band', right_on='AgeGroup', how='left')
        merged_df['rate_standardised'] = merged_df['rate'] * merged_df['EuropeanStandardPopulation']
      
        return merged_df['rate_standardised']
    
    else:
        return df
def convert_ethnicity(df):
    ethnicity_codes = {1.0: "White", 2.0: "Mixed", 3.0: "Asian", 4.0: "Black", 5.0:"Other", np.nan: "unknown", 0: "unknown"}

    df = df.replace({"ethnicity": ethnicity_codes})
    return df




demographics = ['region', 'age_band', 'imd', 'sex', 'learning_disability', 'ethnicity']
sentinel_measures = ["qrisk2", "asthma", "copd", "sodium", "cholesterol", "alt", "tsh", "alt", "rbc", 'hba1c', 'systolic_bp', 'medication_review']


for file in os.listdir('output'):

    if file.startswith('input'):
        #exclude ethnicity and practice
        if file.split('_')[1] not in ['ethnicity.feather', 'practice']:
            
            file_path = os.path.join('output', file)
            date = re.match(r"input_(?P<date>\d{4}-\d{2}-\d{2})\.feather", file).group("date")
            df = pd.read_feather(file_path)
            df['date'] = pd.to_datetime(date)

           
            # df = calculate_imd_group(df)

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
