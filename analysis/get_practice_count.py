import pandas as pd
import numpy as np
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parents[1]
OUTPUT_DIR = BASE_DIR / "output"

pattern = r'^input_20\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])\.feather' 

practice_list = []

for file in OUTPUT_DIR.iterdir():
    
    if re.match(pattern, file.name):
        df = pd.read_feather(OUTPUT_DIR / file.name)
        
        practice_list.extend(np.unique(df['practice']))

num_practices = len(np.unique(practice_list))

with open('output/practice_count.json', 'w') as f:
    json.dump({"num_practices": num_practices}, f)



