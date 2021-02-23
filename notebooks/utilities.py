import pandas as pd
import numpy as np
from collections import Counter
from numpy import nan
import json
from ebmdatalab import charts
from IPython.display import display, HTML

def convert_datetime(df):
    df['date'] = pd.to_datetime(df['date'])

def load_and_drop(measure, practice=False):

    if practice:
        df = pd.read_csv(f'../output/measure_{measure}_practice_only.csv')
        convert_datetime(df)
        df = drop_irrelevant_practices(df)
        return df
    else:
        df = pd.read_csv(f'../output/measure_{measure}.csv')
        convert_datetime(df)
        df = drop_irrelevant_practices(df)
        return df

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
    df.drop(columns=['Events'])

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


def get_median(df, dates):
    median_dict = {}
    for date in dates:
        #subset by date
        df_subset = df[df['date'] == date]

        #order by value
        df = df_subset.sort_values('date')
        median = df_subset['num_per_thousand'].median()
        median_dict[date] = median
    return median_dict


def get_idr(df, dates):
    idr_dict = {}
    for date in dates:
        #subset by date
        df_subset = df[df['date'] == date]

        #order by value
        df = df_subset.sort_values('date')

        #calculate idr
        ten = df_subset['num_per_thousand'].quantile(0.1)
        ninety = df_subset['num_per_thousand'].quantile(0.9)
        idr = ninety-ten

        idr_dict[date] = idr
    return idr_dict


def calculate_change_median(median_list):
    change_list = []
    for i in range(len(median_list)):
        if i > 0:
            percent = ((median_list[i]/median_list[0])-1)*100
            change_list.append(percent)
    return change_list

def calculate_statistics(df, measure_column, idr_dates):
    #load total number of practices from practice count json object
    f = open("../output/practice_count.json")
    num_practices = json.load(f)['num_practices']

    # calculate number of unique practices and caluclate as % of total
    practices_included = get_number_practices(df)
    practices_included_percent = float(
        f'{((practices_included/num_practices)*100):.2f}')

    # calculate number of events per mil
    num_events_mil = float(f'{df[measure_column].sum()/1000000:.2f}')

    # load total number of patients from json object
    f = open("../output/patient_count.json")
    num_patients_dict = json.load(f)['num_patients']
    num_patients = num_patients_dict[measure_column]

    return practices_included, practices_included_percent, num_events_mil, num_patients

def generate_sentinel_measure(data_dict, data_dict_practice, codelist_dict, measure, code_colum, term_column, dates_list):
    df = data_dict[measure]
    childs_df = create_child_table(df, codelist_dict[measure], 'CTV3ID', 'CTV3PreferredTermDesc', measure)

    practices_included, practices_included_percent, num_events_mil, num_patients = calculate_statistics(
        df, measure, dates_list)


    df = data_dict_practice[measure]
    convert_datetime(df)
    calculate_rate(df, measure, 'population')
    
    idr_list = [get_idr(df, dates_list)[x]
                for x in dates_list]


    median_list = [get_median(df, dates_list)[x]
               for x in dates_list]

    change_list = calculate_change_median(median_list)

    print(f'Practices included: {practices_included} ({practices_included_percent}%)')
    print(f'2020 patients: {num_patients:.2f}M ({num_events_mil:.2f}M events)')
    print(
        f'Feb Median: {median_list[0]:.1f} (IDR: {idr_list[0]:.1f}), April Median: {median_list[1]:.1f} (IDR: {idr_list[1]:.1f}), Dec Median: {median_list[2]:.1f} (IDR: {idr_list[2]:.1f})')
    print(
        f'Change in median from Feb 2020: April: {change_list[0]:.2f}%; December: {change_list[1]:.2f}%')
    
    display(HTML(childs_df.to_html()))

    charts.deciles_chart(
        data_dict_practice[measure],
        period_column="date",
        column="num_per_thousand",
        title=measure,
        ylabel="rate per 1000",
        show_outer_percentiles=False,
        show_legend=True,
    )
    

