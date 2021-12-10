import re
import pandas as pd
from pathlib import Path
from utilities import calculate_rate, drop_irrelevant_practices, load_and_drop, OUTPUT_DIR, produce_stripped_measures


measure_pattern = r'^measure_\w*_practice_only_rate.csv'

for file in OUTPUT_DIR.iterdir():
    if re.match(measure_pattern, file.name):
        
        sentinel_measure = re.search(r'measure_(.*)\_practice_only_rate.csv', file.name).group(1)
        df = load_and_drop(sentinel_measure, practice=True)
        
        df = produce_stripped_measures(df, sentinel_measure)

        df.to_csv(OUTPUT_DIR / f"measure_cleaned_{sentinel_measure}.csv", index=False)
        




