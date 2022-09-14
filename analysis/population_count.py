import pandas as pd
import numpy as np
import re
import json
from pathlib import Path

def match_input_files(file: str) -> bool:
    """Checks if file name has format outputted by cohort extractor"""
    pattern = r"^input_population_20\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])\.feather"
    return True if re.match(pattern, file) else False

def get_date_input_file(file: str) -> str:
    """Gets the date in format YYYY-MM-DD from input file name string"""
    # check format
    if not match_input_files(file):
        raise Exception("Not valid input file format")

    else:
        date = result = re.search(r"input_population_(.*)\.feather", file)
        return date.group(1)

moved = []

first_month = pd.read_feather("output/joined/input_population_2019-01-01.feather")

for file in Path("output/joined").iterdir():

    if match_input_files(file.name):
      
        df = pd.read_feather(file)
        date = get_date_input_file(str(file.name))
        if date != "2019-01-01":
            patients_not_died = df.loc[df["died"]==0, "patient_id"]
            patients_left = ~first_month.loc[:, "patient_id"].isin(patients_not_died)
            moved.extend(patients_left)

        
            patients = df.loc[~((df["age"] == 18) & (df["age_prev_month"]==17)), "patient_id"]
            patients_joined = ~patients.isin(first_month.loc[:, "patient_id"])
            moved.extend(patients_joined)

total_moved = len(np.unique(moved))

with open("output/moved_count.json", "w") as f:
    json.dump({"num_patients": total_moved}, f)
