import os 
import pandas as pd
from cohortextractor import Measure

measures = [
    
    Measure(
        id="systolic_bp",
        numerator="systolic_bp",
        denominator="population",
        group_by=["practice", "systolic_bp_event_code"]
    ),

    Measure(
        id="systolic_bp_practice_only",
        numerator="systolic_bp",
        denominator="population",
        group_by=["practice"]
    ),

    Measure(
        id="qrisk2",
        numerator="qrisk2",
        denominator="population",
        group_by=["practice", "qrisk2_event_code"]
    ),

    Measure(
        id="qrisk2_practice_only",
        numerator="qrisk2",
        denominator="population",
        group_by=["practice"]
    ),

    Measure(
        id="cholesterol",
        numerator="cholesterol",
        denominator="population",
        group_by=["practice", "cholesterol_event_code"]
    ),

    Measure(
        id="cholesterol_practice_only",
        numerator="cholesterol",
        denominator="population",
        group_by=["practice"]
    ),
   
    Measure(
        id="alt",
        numerator="alt",
        denominator="population",
        group_by=["practice", "alt_event_code"]
    ),

    Measure(
        id="alt_practice_only",
        numerator="alt",
        denominator="population",
        group_by=["practice"]
    ),

    Measure(
        id="tsh",
        numerator="tsh",
        denominator="population",
        group_by=["practice", "tsh_event_code"]
    ),

    Measure(
        id="tsh_practice_only",
        numerator="tsh",
        denominator="population",
        group_by=["practice"]
    ),

    Measure(
        id="rbc",
        numerator="rbc",
        denominator="population",
        group_by=["practice", "rbc_event_code"]
    ),

    Measure(
        id="rbc_practice_only",
        numerator="rbc",
        denominator="population",
        group_by=["practice"]
    ),

    Measure(
        id="hba1c",
        numerator="hba1c",
        denominator="population",
        group_by=["practice", "hba1c_event_code"]
    ),

    Measure(
        id="hba1c_practice_only",
        numerator="hba1c",
        denominator="population",
        group_by=["practice"]
    ),

    Measure(
        id="sodium",
        numerator="sodium",
        denominator="population",
        group_by=["practice", "sodium_event_code"]
    ),

    Measure(
        id="sodium_practice_only",
        numerator="sodium",
        denominator="population",
        group_by=["practice"]
    ),

    Measure(
        id="asthma",
        numerator="asthma",
        denominator="population",
        group_by=["practice", "asthma_event_code"]
    ),

    Measure(
        id="asthma_practice_only",
        numerator="asthma",
        denominator="population",
        group_by=["practice"]
    ),

    Measure(
        id="copd",
        numerator="copd",
        denominator="population",
        group_by=["practice", "copd_event_code"]
    ),

    Measure(
        id="copd_practice_only",
        numerator="copd",
        denominator="population",
        group_by=["practice"]
    ),
]

demographics = ['region', 'age_band', 'imd', 'sex', 'learning_disability', 'ethnicity']
sentinel_measures = ["qrisk2", "asthma", "copd", "sodium", "cholesterol", "alt", "tsh", "alt", "rbc", 'hba1c', 'systolic_bp', 'medication_review']

for sentinel_measure in sentinel_measures:
    for d in demographics:
        if d=='age_band':
            m = Measure(
            id=f'{sentinel_measure}_{d}',
            numerator=sentinel_measure,
            denominator="population",
            group_by=["age_band", "practice"]
            )
                
            

        
        else:

            m = Measure(
                id=f'{sentinel_measure}_{d}',
                numerator=sentinel_measure,
                denominator="population",
                group_by=["age_band", d, "practice"]
            )
        
        measures.append(m)

for d in demographics:     
    data = []
    for file in os.listdir('output'):

        if file.startswith('input'):
            #exclude ethnicity and practice
            if file.split('_')[1] not in ['ethnicity.csv', 'practice']:

                file_path = os.path.join('output', file)
                date = file.split('_')[1][:-4]
                df = pd.read_feather(file_path)
                df['date'] = date

                data.append(df)


    df = pd.concat(data)
    
    
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
            
        measures_df.to_feather(f'output/measure_{measure}_{d}.feather')