# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# <h1 align="center">Changes in sentinel measures of primary care activity during the pandemic</h1>
#
# The purpose of this notebook is to provide measures of overall activity at the practice level during the pandemic.
#
# The following sentinel measures are provided:
# * [Systolic BP](#systolic_bp)
# * [QRISK](#qrisk)
# * [Cholesterol](#cholesterol)
# * [Bilirubin](#bilirubin)
# * [Serum TSH](#serum_tsh)
# * [RBC/FBC](#rbc_fbc)
# * [HBa1c](#hba1c)
# * [Serum Sodium](#serum_sodium)
# * [Asthma](#asthma)
#
#

# +
import pandas as pd
import matplotlib.pyplot as plt
from ebmdatalab import charts
from IPython.display import HTML
from decimal import Decimal
import numpy as np
import json
from utilities import *

# %matplotlib inline
# -

HTML('''<script>
code_show=true; 
function code_toggle() {
 if (code_show){
 $('div.input').hide();
 } else {
 $('div.input').show();
 }
 code_show = !code_show
} 
$( document ).ready(code_toggle);
</script>
The raw code for this IPython notebook is by default hidden for easier reading.
To toggle on/off the raw code, click <a href="javascript:code_toggle()">here</a>.''')

# +

HTML('''<script>
code_show_err=false; 
function code_toggle_err() {
 if (code_show_err){
 $('div.output_stderr').hide();
 } else {
 $('div.output_stderr').show();
 }
 code_show_err = !code_show_err
} 
$( document ).ready(code_toggle_err);
</script>
To toggle on/off output_stderr, click <a href="javascript:code_toggle_err()">here</a>.''')

# +
# code_df = pd.read_csv('../data/code_dictionary.csv')

# example_code_df = pd.DataFrame(data=[["A", "Description A here"], ["B", "Description B here"]], columns=["first_digits", "Description"])

sentinel_measures = ["systolic_bp", "qrisk", "cholesterol", "bilirubin", "serum_tsh", "rbc_fbc", "hba1c", "serum_sodium", "asthma"]
sentinel_measures_test = ["chronic_respiratory_disease"]
# -

# Load in the measures csv files for each sentinel measure.
# Convert datetime column
# Drop unwanted practices (not using code)

# +
data_dict = {}

for measure in sentinel_measures_test:
    df = pd.read_csv(f'../output/measure_{measure}.csv')
    convert_datetime(df)
    df = drop_irrelevant_practices(df)
    data_dict[measure] = df
    
data_dict_practice = {}

for measure in sentinel_measures_test:
    df = pd.read_csv(f'../output/measure_{measure}_practice_only.csv')
    convert_datetime(df)
    df = drop_irrelevant_practices(df)
    data_dict_practice[measure] = df
    
# -

# Load in codelist for each sentinel measure (to get descriptions).

# +
sentinel_measure_codelist_mapping_dict = {"chronic_respiratory_disease":"opensafely-chronic-respiratory-disease","systolic_bp":"systolic_bp", "qrisk":"qrisk", "cholesterol": "cholesterol", "bilirubin": "bilirubin", "serum_tsh": "serum_tsh", "rbc_fbc": "rbc_fbc", "hba1c": "hba1c", "serum_sodium": "serum_sodium", "asthma": "asthma"}

codelist_dict = {}
for measure in sentinel_measures_test:
    codelist_name = sentinel_measure_codelist_mapping_dict[measure]
    codelist = pd.read_csv(f'../codelists/{codelist_name}.csv')
    codelist_dict[measure] = codelist
    
    

# -

# Get first measure and create dictionary of all subcodes

df = data_dict['chronic_respiratory_disease']
example_code_dict = get_child_codes(df, 'chronic_respiratory_disease')
example_code_dict

# Create table of top child codes

childs_df = create_child_table(df, codelist_dict['chronic_respiratory_disease'], 'CTV3ID', 'CTV3PreferredTermDesc', 'chronic_respiratory_disease')
childs_df


# Calculate statistics for measures.
# * Practices as percentage of total practices
# * Total number of patients (with specific events) (2020)
# * Total number of events (2020)
# * Median and IDR at Feb, April, December
# * Percentage drops between time periods
# * Overall classification of rate change

# +
def calculate_statistics(df, measure_column, idr_dates):
    #load total number of practices from practice count json object
    f = open("../output/practice_count.json")
    num_practices = json.load(f)['num_practices']

    # calculate number of unique practices and caluclate as % of total
    practices_included = get_number_practices(df)
    practices_included_percent = float(f'{((practices_included/num_practices)*100):.2f}')
    
    # calculate number of events per mil
    num_events_mil = float(f'{df[measure_column].sum()/1000000:.2f}')
    
    
    # load total number of patients from json object
    f = open("../output/patient_count.json")
    num_patients_dict = json.load(f)['num_patients']
    num_patients = num_patients_dict[measure_column]
    
    
    return practices_included, practices_included_percent, num_events_mil, num_patients


# -

practices_included, practices_included_percent, num_events_mil, num_patients = calculate_statistics(df, 'chronic_respiratory_disease', ["2020-01-01"])

practices_included, practices_included_percent, num_events_mil, num_patients

# Measure produces value split by practice and event code.  Used above to get child codes.  Load df only grouped by practice for charts.

df = data_dict_practice['chronic_respiratory_disease']
convert_datetime(df)
calculate_rate(df, 'chronic_respiratory_disease', 'population')


# +
def get_median(df, dates):
    median_dict = {}
    for date in dates:
        #subset by date
        df_subset = df[df['date'] == date]

        #order by value
        df_subset.sort_values('date', inplace=True)
        median = df_subset['num_per_thousand'].median()
        median_dict[date] = median
    return median_dict

def get_idr(df, dates):
    idr_dict = {}
    for date in dates:
        #subset by date
        df_subset = df[df['date'] == date]

        #order by value
        df_subset.sort_values('date', inplace=True)
        
        #calculate idr
        ten = df_subset['num_per_thousand'].quantile(0.1)
        ninety = df_subset['num_per_thousand'].quantile(0.9)
        idr = ninety-ten
        
        idr_dict[date] = idr
    return idr_dict

def calculate_change_median(median_list):
    change_list = []
    for i in range(len(median_list)):
        if i >0:
            percent = ((median_list[i]/median_list[0])-1)*100
            change_list.append(percent)
    return change_list



# +
median = get_median(df, ["2020-02-01", "2020-04-01", "2020-12-01"])
idr = get_idr(df, ["2020-02-01", "2020-04-01", "2020-12-01"])

idr_list = [get_idr(df, ["2020-02-01", "2020-04-01", "2020-12-01"])[x] for x in ["2020-02-01", "2020-04-01", "2020-12-01"]]
median_list = [get_median(df, ["2020-02-01", "2020-04-01", "2020-12-01"])[x] for x in ["2020-02-01", "2020-04-01", "2020-12-01"]]
# median_list = [get_median(df, x)[x] for x in ["2020-02-01", "2020-04-01", "2020-12-01"]]

change_list = calculate_change_median(median_list)
# -

print(f'Practices included: {practices_included} ({practices_included_percent})')
print(f'2020 patients: {num_patients}M ({num_events_mil}M)')
print(f'Feb Median: {median_list[0]} (IDR: {idr_list[0]:.1f}), April Median: {median_list[1]} (IDR: {idr_list[1]:.1f}), Dec Median: {median_list[2]} (IDR: {idr_list[2]:.1f})')
print(f'Change in median from Feb 2020: April: {change_list[0]:.2f}%; December: {change_list[1]:.2f}%')

charts.deciles_chart(
    data_dict['chronic_respiratory_disease'],
    period_column="date",
    column="value",
    title="Chronic Respiratory Disease",
    ylabel="rate per 1000",
    show_outer_percentiles=False,
    show_legend=True,
);

# <a id="systolic_bp"></a>
# ### Systolic BP
#
# Description:

# +
systolic_bp_df = drop_irrelevant_practices(data_dict['sentinel_measure_x'])

charts.deciles_chart(
    data_dict['sentinel_measure_x'],
    period_column="date",
    column="value",
    title="Systolic BP",
    ylabel="rate per 1000",
    show_outer_percentiles=False,
    show_legend=True,
);

example_code_dict = get_child_codes(systolic_bp_df)
childs_df = create_child_table(systolic_bp_df)
HTML(childs_df.to_html(index=False))
# -

# <a id="qrisk"></a>
# ### QRISK

charts.deciles_chart(
    data_dict['qrisk'],
    period_column="date",
    column="value",
    title="QRISK",
    ylabel="rate per 1000",
    show_outer_percentiles=False,
    show_legend=True,
);

# <a id="cholesterol"></a>
# ### Cholesterol

charts.deciles_chart(
    data_dict['cholesterol'],
    period_column="date",
    column="value",
    title="Cholesterol",
    ylabel="rate per 1000",
    show_outer_percentiles=False,
    show_legend=True,
);

# <a id="bilirubin"></a>
# ### Bilirubin

charts.deciles_chart(
    data_dict['bilirubin'],
    period_column="date",
    column="value",
    title="Bilirubin",
    ylabel="rate per 1000",
    show_outer_percentiles=False,
    show_legend=True,
);

# <a id="serum_tsh"></a>
# ### Serum TSH

charts.deciles_chart(
    data_dict['serum_tsh'],
    period_column="date",
    column="value",
    title="Serum TSH",
    ylabel="rate per 1000",
    show_outer_percentiles=False,
    show_legend=True,
);

# <a id="rbc_fbc"></a>
# ### RBC/FBC

charts.deciles_chart(
    data_dict['rbc_fbc'],
    period_column="date",
    column="value",
    title="RBC/FBC",
    ylabel="rate per 1000",
    show_outer_percentiles=False,
    show_legend=True,
);

# <a id="hba1c"></a>
# ### HBa1c

charts.deciles_chart(
    data_dict['hba1c'],
    period_column="date",
    column="value",
    title="HBa1c",
    ylabel="rate per 1000",
    show_outer_percentiles=False,
    show_legend=True,
);

# <a id="serum_sodium"></a>
# ### Serum Sodium

charts.deciles_chart(
    data_dict['serum_sodium'],
    period_column="date",
    column="value",
    title="Serum Sodium",
    ylabel="rate per 1000",
    show_outer_percentiles=False,
    show_legend=True,
);

# <a id="asthma"></a>
# ### Asthma

charts.deciles_chart(
    data_dict['asthma'],
    period_column="date",
    column="value",
    title="Asthma",
    ylabel="rate per 1000",
    show_outer_percentiles=False,
    show_legend=True,
);
