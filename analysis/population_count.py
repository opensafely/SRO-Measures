import pandas as pd
import json
from pathlib import Path
from utilities import get_patients_left_tpp, get_patients_joined_tpp, concatenate_patients_moved, match_input_files, get_date_input_file



moved = []

first_month = pd.read_feather("output/joined/input_population_2019-01-01.feather")

for file in Path("output/joined").iterdir():

    if match_input_files(file.name):

        df = pd.read_feather(file)
        date = get_date_input_file(str(file.name))
        if date != "2019-01-01":

            demographics_patients_left = get_patients_left_tpp(df, first_month, "died", ["sex",
                    "age_band",
                    "ethnicity",
                    "imd",
                    "region"])
            
            demographics_patients_joined = get_patients_joined_tpp(df, first_month, "age", "age_prev_month",["sex",
                    "age_band",
                    "ethnicity",
                    "imd",
                    "region"])

            moved.extend([demographics_patients_left, demographics_patients_joined])


total_moved, dem_counts = concatenate_patients_moved(moved)


with open("output/moved_count.json", "w") as f:
    json.dump({"num_patients": total_moved}, f)

with open("output/moved_demographic_count.json", "w") as f:
    json.dump(dem_counts, f)
