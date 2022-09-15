import pandas as pd
import numpy as np
import re
import json
from pathlib import Path


def match_input_files(file: str) -> bool:
    """Checks if file name has format outputted by cohort extractor"""
    pattern = (
        r"^input_population_20\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])\.feather"
    )
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
            patients_not_died = df.loc[df["died"] == 0, "patient_id"]
            patients_left = first_month.loc[
                ~first_month["patient_id"].isin(patients_not_died), "patient_id"
            ]

            demographics_patients_left = df.loc[
                df["patient_id"].isin(patients_left),
                [
                    "sex",
                    "age_band",
                    "ethnicity",
                    "imd",
                    "region",
                    "patient_id"
                ],
            ]

            demographics_patients_left["ehr_provider"] = "EMIS"
            moved.append(demographics_patients_left)

            patients = df.loc[
                ~((df["age"] == 18) & (df["age_prev_month"] == 17)), "patient_id"
            ]
            patients_joined = patients[~patients.isin(first_month["patient_id"])]

            demographics_patients_joined = df.loc[
                df["patient_id"].isin(patients_joined),
                [
                    "sex",
                    "age_band",
                    "ethnicity",
                    "imd",
                    "region",
                    "patient_id"
                ],
            ]
            demographics_patients_joined["ehr_provider"] = "TPP"
            moved.append(demographics_patients_joined)


moved_df = pd.concat(moved)
# this will contain duplicates. Take the last entry (most recent demographics)
moved_df = moved_df.drop_duplicates(subset="patient_id", keep="last")

total_moved = len(moved_df["patient_id"].unique())

dem_counts = {}
for name, values in moved_df.iteritems():
    if name !="patient_id":

        count = values.value_counts().to_dict()
        dem_counts[name] = count


with open("output/moved_count.json", "w") as f:
    json.dump({"num_patients": total_moved}, f)

with open("output/moved_demographic_count.json", "w") as f:
    json.dump(dem_counts, f)
