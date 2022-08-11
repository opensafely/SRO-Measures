import pandas as pd
import argparse
from pathlib import Path
from utilities import create_top_5_code_table, write_csv

def parse_args():
    parser = argparse.ArgumentParser()
 

    parser.add_argument("--input-dir", type=Path)
    parser.add_argument("--low-count-threshold", default=100, type=int)
    parser.add_argument("--rounding-base", default=10, type=int)

    
    return parser.parse_args()



def main():
    args = parse_args()
    input_dir = args.input_dir
    low_count_threshold = args.low_count_threshold
    rounding_base = args.rounding_base

    measures = ["alt", "asthma", "cholesterol", "copd", "hba1c", "medication_review", "qrisk2", "rbc", "sodium", "systolic_bp", "tsh"]
    sentinel_measure_codelist_mapping_dict = {"medication_review": "opensafely-care-planning-medication-review-simple-reference-set-nhs-digital","systolic_bp":"opensafely-systolic-blood-pressure-qof", "qrisk2":"opensafely-cvd-risk-assessment-score-qof", "cholesterol": "opensafely-cholesterol-tests", "alt": "opensafely-alanine-aminotransferase-alt-tests", "tsh": "opensafely-thyroid-stimulating-hormone-tsh-testing", "rbc": "opensafely-red-blood-cell-rbc-tests", "hba1c": "opensafely-glycated-haemoglobin-hba1c-tests", "sodium": "opensafely-sodium-tests-numerical-value", "asthma": "opensafely-asthma-annual-review-qof", "copd": "opensafely-chronic-obstructive-pulmonary-disease-copd-review-qof"}

    for measure in measures:

        code_df = pd.read_csv(f"{input_dir}/{measure}/counts_per_code.csv")
        codelist = pd.read_csv(f"codelists/{sentinel_measure_codelist_mapping_dict[measure]}.csv")

        top_5_code_table = create_top_5_code_table(
            df=code_df,
            code_df=codelist,
            code_column="code",
            term_column="term",
            low_count_threshold=low_count_threshold,
            rounding_base=rounding_base,
        )
        write_csv(top_5_code_table, Path(f"{input_dir}/{measure}/top_5_code_table.csv", index=False))


if __name__ == "__main__":
    main()