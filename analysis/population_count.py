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


def get_patients_left_tpp(df, df_first_month, died_column, demographics):

    patients_still_alive = df.loc[df[died_column] == 0, "patient_id"]

    # anyone in the first month but not in monthyl cohort of people still alive
    patients_left = df_first_month.loc[
        ~df_first_month["patient_id"].isin(patients_still_alive), "patient_id"
    ]

    # demographics of those people in a given month
    demographics_patients_left = df.loc[
        df["patient_id"].isin(patients_left),
        demographics + ["patient_id"],
    ]

    # lets assume the people who leave go to EMIS
    demographics_patients_left["ehr_provider"] = "EMIS"
    return demographics_patients_left

def get_patients_joined_tpp(df, df_first_month, age_column, age_prev_month_column, demographics):
    # any patients in monthly cohort who didn't become eligible by turning 18 in prev month
    patients_adults = df.loc[
        ~((df[age_column] == 18) & (df[age_prev_month_column] == 17)), "patient_id"
    ]

    # anyone of these patients who were not in the first month
    patients_joined = patients_adults[~patients_adults.isin(df_first_month["patient_id"])]

    demographics_patients_joined = df.loc[
        df["patient_id"].isin(patients_joined),
        demographics + ["patient_id"],
    ]
    # Anyone who has joined should now be counted as TPP
    demographics_patients_joined["ehr_provider"] = "TPP"

    return demographics_patients_joined

def concatenate_patients_moved(moved):
    moved_df = pd.concat(moved)
    # this will contain duplicates. Take the last entry (most recent demographics)
    moved_df = moved_df.drop_duplicates(subset="patient_id", keep="last")

    total_moved = len(moved_df["patient_id"].unique())

    dem_counts = {}
    for name, values in moved_df.iteritems():
        if name !="patient_id":

            count = values.value_counts().to_dict()
            dem_counts[name] = count
    
    return total_moved, dem_counts

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
