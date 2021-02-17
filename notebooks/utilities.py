import pandas as pd
import numpy as np
from collections import Counter
from numpy import nan

def convert_datetime(df):
    df['date'] = pd.to_datetime(df['date'])


def calculate_rate(df, value_col, population_col, per=1000):
    num_per_thousand = df[value_col]/(df[population_col]/1000)
    df['num_per_thousand'] = num_per_thousand


def drop_irrelevant_practices(df):
    #drop practices that do not use the code
    mean_value_df = df.groupby("practice")["value"].mean().reset_index()

    practices_to_drop = list(
    mean_value_df['practice'][mean_value_df['value'] == 0])

    #drop
    df = df[~df['practice'].isin(practices_to_drop)]

    return df


# def get_child_codes(df, event_code_column):
#     codes = df[event_code_column]
#     code_dict = Counter(codes)
    
#     del code_dict[nan]
#     return dict(code_dict)


def get_child_codes(df, measure):

    event_code_column = f'{measure}_event_code'
    event_column = f'{measure}'

    counts = df.groupby(event_code_column)[event_column].sum()
    code_dict = dict(counts)

    return code_dict


def create_child_table(df, code_df, code_column, term_column, measure, nrows=5):
    #pass in df from data_dict
    #code df contains first digits and descriptions

    #get codes counts
    code_dict = get_child_codes(df, measure)

    #make df of events for each subcode
    df = pd.DataFrame.from_dict(
        code_dict, orient="index", columns=["Events"])
    df[code_column] = df.index

    #convert events to events/thousand
    df['Events (thousands)'] = df['Events'].apply(lambda x: x/1000)

    #order by events
    df.sort_values(by='Events (thousands)', inplace=True)
    df = df.iloc[:, [1, 0, 2]]

    #get description for each code

    def get_description(row):
        code = row[code_column]

        description = code_df[code_df[code_column]
                              == code][term_column].values[0]

        return description

    df['Description'] = df.apply(
        lambda row: get_description(row), axis=1)

    #return top n rows
    return df.iloc[:nrows, :]

def get_number_practices(df):
    num_practices = len(np.unique(df['practice']))
    return num_practices
