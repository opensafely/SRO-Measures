import re
import pandas as pd
from pathlib import Path
from utilities import calculate_rate, drop_irrelevant_practices, load_and_drop, OUTPUT_DIR


measure_pattern = r'^measure_\w*_practice_only_rate.csv'

for file in OUTPUT_DIR.iterdir():
    if re.match(measure_pattern, file.name):
        
        sentinel_measure = re.search(r'measure_(.*)\_practice_only_rate.csv', file.name).group(1)
        df = load_and_drop(sentinel_measure, practice=True)
        
        calculate_rate(df, sentinel_measure, "population")
     
        #select only the rate and date columns
        df = df.loc[:, ['rate', 'date']]
        
        #randomly shuffle the df and reset the index
        df.sample(frac=1).reset_index(drop=True).to_csv(OUTPUT_DIR / f"measure_cleaned_{sentinel_measure}.csv")
        




