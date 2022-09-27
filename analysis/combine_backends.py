# Use to combine results across backends.

import pandas as pd
from utilities import BASE_DIR
import json
import numpy as np

sentinel_measures = [
    "qrisk2",
    "asthma",
    "copd",
    "sodium",
    "cholesterol",
    "alt",
    "tsh",
    "alt",
    "rbc",
    "hba1c",
    "systolic_bp",
    "medication_review",
]

demographics = ["age_band", "ethnicity", "imd", "region", "sex", "total"]

for d in demographics:
    emis_count = pd.read_csv(f"backend_outputs/emis/{d}_count.csv", index_col=0)
    tpp_count = pd.read_csv(f"backend_outputs/tpp/{d}_count.csv", index_col=0)

    if d == "ethnicity":
        # map emis ethnicity to 6 categories
        mapping = {
            1: 1,
            2: 1,
            3: 1,
            4: 2,
            5: 2,
            6: 2,
            7: 2,
            8: 3,
            9: 3,
            10: 3,
            11: 3,
            12: 4,
            13: 4,
            14: 4,
            15: 5,
            16: 5,
        }
        emis_count.index = emis_count.index.map(mapping)
        emis_count = emis_count.groupby(level=0).sum()

    if d == "region":

        mapping_tpp = {
            "East Midlands": "Midlands",
            "Yorkshire and The Humber": "North East",
            "North West": "North West",
            "North East": "North East",
            "East": "East",
            "London": "London",
            "South East": "South East",
            "South West": "South West",
            "West Midlands": "Midlands",
        }

        mapping_emis = {
            "NORTH EAST AND YORKSHIRE COMMISSIONING REGION": "North East",
            "LONDON COMMISSIONING REGION": "London",
            "NORTH WEST COMMISSIONING REGION": "North West",
            "SOUTH EAST COMMISSIONING REGION": "South East",
            "EAST OF ENGLAND COMMISSIONING REGION": "East",
            "SOUTH WEST COMMISSIONING REGION": "South West",
            "MIDLANDS COMMISSIONING REGION": "Midlands",
        }

        emis_count.index = emis_count.index.map(mapping_emis)
        emis_count = emis_count.groupby(level=0).sum()

        tpp_count.index = tpp_count.index.map(mapping_tpp)
        tpp_count = tpp_count.groupby(level=0).sum()

    if d == "total":
        emis_count.set_index("pop", drop=True, inplace=True)
        tpp_count.set_index("pop", drop=True, inplace=True)

    combined_count = emis_count.sort_index().add(tpp_count.sort_index())
    combined_count.to_csv(f"backend_outputs/{d}_count.csv")


with open("backend_outputs/tpp/event_count.json") as f:
    num_events_tpp = json.load(f)["num_events"]
with open("backend_outputs/emis/event_count.json") as f:
    num_events_emis = json.load(f)["num_events"]

total_count = {}

for key, value in num_events_tpp.items():
    count = value + num_events_emis[key]
    total_count[key] = count


for measure in sentinel_measures:
    code_table_path_emis = BASE_DIR / f"backend_outputs/emis/code_table_{measure}.csv"
    code_table_path_tpp = BASE_DIR / f"backend_outputs/tpp/code_table_{measure}.csv"

    code_table_emis = pd.read_csv(code_table_path_emis)
    code_table_tpp = pd.read_csv(code_table_path_tpp)

    code_table_combined = pd.merge(
        code_table_emis,
        code_table_tpp,
        how="outer",
        on="Code",
        suffixes=("_emis", "_tpp"),
    )

    # checkif code in both

    code_table_combined["combined_events"] = code_table_combined["Events_emis"].fillna(
        0
    ) + code_table_combined["Events_tpp"].fillna(0)

    # calculate % makeup of each code
    total_events = total_count[measure]

    code_table_combined = code_table_combined.sort_values(
        by="combined_events", ascending=False
    )

    code_table_combined = code_table_combined.head(5)

    code_table_combined["Proportion of Codes (%)"] = round(
        (code_table_combined["combined_events"] / total_events) * 100, 2
    )
    code_table_combined["Description_emis"] = code_table_combined[
        "Description_emis"
    ].astype(str)
    code_table_combined["Description_tpp"] = code_table_combined[
        "Description_tpp"
    ].astype(str)

    ######

    ###########
    # # Cast the code to an integer.
    # event_counts[code_column] = event_counts[code_column].astype(int)

    # check that codes not in the top 5 rows have >5 events
    outside_top_5_percent = 1 - (
        (code_table_combined.head(5)["combined_events"].sum()) / total_events
    )

    if (0 < (outside_top_5_percent * total_events) <= 5) & (outside_top_5_percent != 0):

        # drop percent column
        code_table_combined = code_table_combined.loc[
            :, ["Code", "Description_emis", "Description_tpp"]
        ]

    else:
        # give more logical column ordering

        code_table_combined = code_table_combined.loc[
            :,
            ["Code", "Description_emis", "Description_tpp", "Proportion of Codes (%)"],
        ]

    code_table_combined["Proportion of Codes (%)"] = code_table_combined[
        "Proportion of Codes (%)"
    ].round(decimals=2)

    if len(code_table_combined["Code"]) > 1:

        code_table_combined.loc[
            code_table_combined["Proportion of Codes (%)"] == 0,
            "Proportion of Codes (%)",
        ] = "< 0.005"
        code_table_combined.loc[
            code_table_combined["Proportion of Codes (%)"] == 100,
            "Proportion of Codes (%)",
        ] = "> 99.995"

    code_table_combined = code_table_combined.loc[
        :, ["Code", "Description_tpp", "Description_emis", "Proportion of Codes (%)"]
    ]

    code_table_combined.to_csv(BASE_DIR / f"backend_outputs/code_table_{measure}.csv")

    measure_path_emis = BASE_DIR / f"backend_outputs/emis/measure_cleaned_{measure}.csv"
    measure_path_tpp = BASE_DIR / f"backend_outputs/tpp/measure_cleaned_{measure}.csv"

    measure_emis = pd.read_csv(measure_path_emis)
    measure_tpp = pd.read_csv(measure_path_tpp)

    measures_combined = pd.concat([measure_emis, measure_tpp], axis="index")
    measures_combined.to_csv(BASE_DIR / f"backend_outputs/measure_{measure}.csv")
