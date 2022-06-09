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
