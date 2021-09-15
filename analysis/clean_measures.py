import re
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parents[1]
OUTPUT_DIR = BASE_DIR / "output"

measure_pattern = r'^measure_\w*_practice_only.csv'

def calculate_rate(df, value_col, population_col):
    """Calculates the number of events per 1,000 of the population.

    This function operates on the given measure table in-place, adding
    a `num_per_thousand` column.

    Args:
        df: A measure table.
        value_col: The name of the numerator column in the measure table.
        population_col: The name of the denominator column in the measure table.
    """
    num_per_thousand = df[value_col] / (df[population_col] / 1000)
    df["num_per_thousand"] = num_per_thousand

def drop_irrelevant_practices(df):
    """Drops irrelevant practices from the given measure table.

    An irrelevant practice has zero events during the study period.

    Args:
        df: A measure table.

    Returns:
        A copy of the given measure table with irrelevant practices dropped.
    """
    is_relevant = df.groupby("practice").value.any()
    return df[df.practice.isin(is_relevant[is_relevant == True].index)]

def load_and_drop(measure, practice=False, drop=True):
    """Loads the measure table for the measure with the given ID.

    Drops irrelevant practices and casts the `date` column from a `str`
    to a `datetime64`.

    Args:
        measure: The measure ID.
        practice: Whether to load the "practice only" measure.

    Returns:
        The table for the given measure ID and practice.
    """
    if practice:
        f_in = OUTPUT_DIR / f"measure_{measure}_practice_only.csv"
    else:
        f_in = OUTPUT_DIR / f"measure_{measure}.csv"

    df = pd.read_csv(f_in, parse_dates=["date"])
    
    if drop:
        df = drop_irrelevant_practices(df)
    return df


for file in OUTPUT_DIR.iterdir():
    if re.match(measure_pattern, file.name):
        
        sentinel_measure = re.search(r'measure_(.*)\_practice_only.csv', file.name).group(1)
        df = load_and_drop(sentinel_measure, practice=True)
        
        calculate_rate(df, sentinel_measure, "population")
        
        #select only the rate and date columns
        df = df.loc[:,['num_per_thousand', 'date']]
        
        #randomly shuffle the df and reset the index
        df.sample(frac=1).reset_index(drop=True).to_csv(OUTPUT_DIR / f"measure_cleaned_{sentinel_measure}.csv")
        




