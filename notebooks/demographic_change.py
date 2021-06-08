import pandas as pd
from utilities import *


sentinel_measures = ["qrisk2", "asthma", "copd", "sodium", "cholesterol", "tsh", "alt", "rbc", 'hba1c', 'systolic_bp', 'medication_review']

demographics = ['region', 'age_band', 'imd', 'sex', 'learning_disability', 'ethnicity']

values_dict = {}


dates = [['2019-01-01', '2019-02-01', '2019-03-01'], ['2020-01-01', '2020-02-01', '2020-03-01'], ['2021-01-01','2021-02-01', '2021-03-01']]

dates_categorisation = ['2019-04-01', '2020-04-01', '2021-04-01']

differences_list = []


def classify_changes(changes):
    """Classifies list of % changes

    Args:
        changes: list of percentage changes
    """
   
    
    #between baseline both time periods
    if (-15 <= changes[0] < 15) and (-15 <= changes[1] < 15):
        classification = 'no change'
    
    #increase at both time periods
    elif (changes[0] >= 15) and (changes[1] >= 15):
        classification = 'increase'
    
    #increase at first then return to normal
    elif (changes[0] >= 15) and (-15 <= changes[1] < 15):
        classification = 'increase then return'
        
    #no change then increase
    elif (-15 <= changes[0] < 15) and (changes[1] >= 15):
        classification = 'no change then increase'
    
    #no change then decrease
    elif (-15 <= changes[0] < 15) and (changes[1] <= -15):
        classification = 'no change then decrease'
    
    #drop that stays low
    elif (changes[0] <= -15) and not (changes[1] <= -15):
        classification = 'sustained drop'
    
    #drop that recovers
    elif (changes[0] <= -15) and (-15 <= changes[1] < 15) :
        classification = 'recovery'
    
    #drop then increase
    elif (changes[0] <= -15) and (changes[1] > 15) :
        classification = 'decrease then increase'
    
    #increase then drop
    elif (changes[0] > 15) and (changes[1] <= -15):
        classification = 'increase then decrease'
    
    #anything else
    else:
        classification = 'none'
    
    return classification


for measure in sentinel_measures:
    
    
    for d in demographics:
        df = pd.read_csv(f'output/combined_measure_{measure}_{d}.csv', parse_dates=['date']).sort_values(['date'])
        
        total_population = df.groupby(by=['date'])[['population']].sum().reset_index()
        total_events = df.groupby(by=['date'])[[measure]].sum().reset_index()
        
        total_df = total_events.merge(total_population, on='date')
        
        total_df['rate'] = total_df[measure]/(total_df['population']/1000)
        
        totals_dict = {}
        for date in dates:
            val = total_df[total_df['date'].isin(date)]['rate'].mean()
            totals_dict[date[1]] = val
    
        
        
        if d == 'ethnicity':
            
            #drop missing ethnicity :('0')
            df = df[df['ethnicity'] != 0]
            
            # replace with strings
            ethnicity_codes = {1.0: "White", 2.0: "Mixed", 3.0: "Asian", 4.0: "Black", 5.0:"Other"}
            df = df.replace({"ethnicity": ethnicity_codes})
            
        elif d == 'age_band':
            df = df[df['age_band'] != 'missing']
            
        elif d == 'learning_disability':
            ld_dict = {0: 'No record of a learning disability', 1: 'Record of a learning disability'}
            df = df.replace({"learning_disability": ld_dict})
        
        
        if d != 'age_band':
            df['rate'] = df[measure]/(df['population']/1000)
        
        
      
        for unique_category in df[d].unique():
            df_subset = df[df[d] == unique_category]
            
            classification_date_values = {}
            date_values = {}
            date_changes = {}
            population_values = {}
            
            for i, date in enumerate(dates):
                classification_val = df_subset.loc[df_subset['date'] == dates_categorisation[i], 'rate'].values[0]
               
                classification_date_values[dates_categorisation[i]] = classification_val
                
                val = df_subset[df_subset['date'].isin(date)]['rate'].mean()
                total_val = totals_dict[date[1]]

              

                difference = round(((val - total_val) / total_val)*100, 2)
                
                population_values[date[1]] = total_val
                date_values[date[1]]=val
                date_changes[date[1]] = difference
            
            
            classification = classify_changes([classification_date_values["2020-04-01"], classification_date_values["2021-04-01"]])
            row = [measure, d, unique_category, date_values["2019-02-01"], population_values["2019-02-01"],date_changes["2019-02-01"], date_values["2020-02-01"], population_values["2020-02-01"], date_changes["2020-02-01"], date_values["2021-02-01"], population_values["2021-02-01"], date_changes["2021-02-01"], classification, date_changes["2021-02-01"] - date_changes["2019-02-01"]]
            differences_list.append(row)
        
 
            
   
    
differences_df =pd.DataFrame(differences_list, columns=['measure', 'demographic', 'demographic_subset', '2019_rate_per_1000', '2019_population_rate', '2019_percentage_difference_from_population_rate', '2020_rate_per_1000', '2020_population_rate', '2020_percentage_difference_from_population_rate', '2021_rate_per_1000', '2021_population_rate', '2021_percentage_difference_from_population_rate', 'absolute_rate_difference_classification', 'difference_in_percentage_distance_from_population_rate_2019_to_2021'])
differences_df.to_csv('output/demographics_differences.csv')

differences_df_sorted = differences_df.reindex(differences_df['difference_in_percentage_distance_from_population_rate_2019_to_2021'].sort_values(ascending=False).index)
differences_df_sorted.to_csv('output/demographics_differences_sorted.csv')