import pandas as pd
from pathlib import Path
from utilities import (
    get_patients_left_tpp,
    get_patients_joined_tpp,
    concatenate_patients_moved,
    match_input_files,
    get_date_input_file,
    save_dict_as_json,
)

# this will contain dataframes of patients who have joined or left during the study period. There will be duplicates
moved = []

first_month = pd.read_feather("output/joined/input_population_2019-01-01.feather")

for file in Path("output/joined").iterdir():

    if match_input_files(file.name):
        
        df = pd.read_feather(file)
        date = get_date_input_file(str(file.name))

        # 2019-01-01 is the month being compared, so we ignore it here
        if date != "2019-01-01":

            demographics_patients_left = get_patients_left_tpp(
                df,
                first_month,
                ["sex", "age_band", "ethnicity_y", "imd", "region"],
            )

            demographics_patients_joined = get_patients_joined_tpp(
                df,
                first_month,
                "age",
                "age_start",
                ["sex", "age_band", "ethnicity_y", "imd", "region"],
            )
            demographics_patients_left["ethnicity_y"] = demographics_patients_left[
                "ethnicity_y"
            ].astype(str)
            demographics_patients_joined["ethnicity_y"] = demographics_patients_joined[
                "ethnicity_y"
            ].astype(str)
            moved.extend([demographics_patients_left, demographics_patients_joined])


total_moved, dem_counts = concatenate_patients_moved(moved)

save_dict_as_json(total_moved, "output/moved_count.json")
save_dict_as_json(dem_counts, "output/moved_demographic_count.json")
