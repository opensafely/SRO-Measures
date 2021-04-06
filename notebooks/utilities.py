import plotly.graph_objects as go
import pandas as pd
import numpy as np
from collections import Counter
from numpy import nan
import json
from IPython.display import display, HTML
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import math

# Legend locations for matplotlib
# https://github.com/ebmdatalab/datalab-pandas/blob/master/ebmdatalab/charts.py
BEST = 0
UPPER_RIGHT = 1
UPPER_LEFT = 2
LOWER_LEFT = 3
LOWER_RIGHT = 4
RIGHT = 5
CENTER_LEFT = 6
CENTER_RIGHT = 7
LOWER_CENTER = 8
UPPER_CENTER = 9
CENTER = 10


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
    df.reset_index(drop=True, inplace=True)

    #convert events to events/thousand
    df['Events (thousands)'] = df['Events'].apply(lambda x: x/1000)
    df.drop(columns=['Events'])

    #order by events
    df = df.sort_values(by='Events (thousands)', ascending=False)
    df = df.iloc[:, [1, 0, 2]]

    #get description for each code

    def get_description(row):
        code = row[code_column]

        description = code_df[code_df[code_column]
                              == code][term_column].values[0]

        return description

    df['Description'] = df.apply(
        lambda row: get_description(row), axis=1)

    
    df[code_column] = df[code_column].astype(int)



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
        df_subset = df_subset.sort_values('date')
        median = df_subset['num_per_thousand'].median()
        median_dict[date] = median
    return median_dict


def get_idr(df, dates):
    idr_dict = {}
    for date in dates:
        #subset by date
        df_subset = df[df['date'] == date]

        #order by value
        df_subset = df_subset.sort_values('date')

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


# https://github.com/ebmdatalab/datalab-pandas/blob/master/ebmdatalab/charts.py
def deciles_chart_ebm(
    df,
    period_column=None,
    column=None,
    title="",
    ylabel="",
    show_outer_percentiles=True,
    show_legend=True,
    ax=None):
    """period_column must be dates / datetimes
    """
    sns.set_style("whitegrid", {"grid.color": ".9"})
    if not ax:
        fig, ax = plt.subplots(1, 1)
    df = add_percentiles(
        df,
        period_column=period_column,
        column=column,
        show_outer_percentiles=show_outer_percentiles,
    )
    linestyles = {
        "decile": {"color": "b", "line": "b--", "linewidth": 1, "label": "decile"},
        "median": {"color": "b", "line": "b-", "linewidth": 1.5, "label": "median"},
        "percentile": {
            "color": "b",
            "line": "b:",
            "linewidth": 0.8,
            "label": "1st-9th, 91st-99th percentile",
        },
    }
    label_seen = []
    for percentile in range(1, 100):  # plot each decile line
        data = df[df["percentile"] == percentile]
        add_label = False

        if percentile == 50:
            style = linestyles["median"]
            add_label = True
        elif show_outer_percentiles and (percentile < 10 or percentile > 90):
            style = linestyles["percentile"]
            if "percentile" not in label_seen:
                label_seen.append("percentile")
                add_label = True
        else:
            style = linestyles["decile"]
            if "decile" not in label_seen:
                label_seen.append("decile")
                add_label = True
        if add_label:
            label = style["label"]
        else:
            label = "_nolegend_"

        ax.plot(
            data[period_column],
            data[column],
            style["line"],
            linewidth=style["linewidth"],
            color=style["color"],
            label=label,
        )
    ax.set_ylabel(ylabel, size=15, alpha=0.6)
    if title:
        ax.set_title(title, size=18)
    # set ymax across all subplots as largest value across dataset
    ax.set_ylim([0, df[column].max() * 1.05])
    ax.tick_params(labelsize=12)
    ax.set_xlim(
        [df[period_column].min(), df[period_column].max()]
    )  # set x axis range as full date range

    plt.setp(ax.xaxis.get_majorticklabels(), rotation=90)
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%B %Y"))
    if show_legend:
        ax.legend(
            bbox_to_anchor=(1.1, 0.8),  # arbitrary location in axes
            #  specified as (x0, y0, w, h)
            loc=CENTER_LEFT,  # which part of the bounding box should
            #  be placed at bbox_to_anchor
            ncol=1,  # number of columns in the legend
            fontsize=12,
            borderaxespad=0.0,
        )  # padding between the axes and legend
        #  specified in font-size units
    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    plt.gcf().autofmt_xdate()
    return plt

def add_percentiles(df, period_column=None, column=None, show_outer_percentiles=True):
    """For each period in `period_column`, compute percentiles across that
    range.
    Adds `percentile` column.
    """
    deciles = np.arange(0.1, 1, 0.1)
    bottom_percentiles = np.arange(0.01, 0.1, 0.01)
    top_percentiles = np.arange(0.91, 1, 0.01)
    if show_outer_percentiles:
        quantiles = np.concatenate((deciles, bottom_percentiles, top_percentiles))
    else:
        quantiles = deciles
    df = df.groupby(period_column)[column].quantile(quantiles).reset_index()
    df = df.rename(index=str, columns={"level_1": "percentile"})
    # create integer range of percentiles
    df["percentile"] = df["percentile"].apply(lambda x: int(x * 100))
    return df


def deciles_chart(
    df,
    period_column=None,
    column=None,
    title="",
    ylabel="",
    interactive=True):
    """period_column must be dates / datetimes
    """

    df = add_percentiles(
        df,
        period_column=period_column,
        column=column,
        show_outer_percentiles=False,
    )

    if interactive:

        fig = go.Figure()

        linestyles = {
            "decile": {"color": "blue", "dash": "dash"},
            "median": {"color": "blue", "dash": "solid"},
            "percentile": {"color": "blue", "dash": "dash"},
        }

        for percentile in np.unique(df['percentile']):
            df_subset = df[df['percentile'] == percentile]
            if percentile == 50:
                fig.add_trace(go.Scatter(x=df_subset[period_column], y=df_subset[column], line={
                            "color": "blue", "dash": "solid", "width": 1.2}, name="median"))
            else:
                fig.add_trace(go.Scatter(x=df_subset[period_column], y=df_subset[column], line={
                            "color": "blue", "dash": "dash", "width": 1}, name=f"decile {int(percentile/10)}"))

        # Set title
        fig.update_layout(
            title_text=title,
            hovermode='x',
            title_x=0.5,


        )

        fig.update_yaxes(title=ylabel)
        fig.update_xaxes(title="Date")

        # Add range slider
        fig.update_layout(
            xaxis=go.layout.XAxis(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                            label="1m",
                            step="month",
                            stepmode="backward"),
                        dict(count=6,
                            label="6m",
                            step="month",
                            stepmode="backward"),

                        dict(count=1,
                            label="1y",
                            step="year",
                            stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            )
        )

        fig.show()

    else:
        deciles_chart_ebm(df, period_column="date", column="num_per_thousand", ylabel="rate per 1000", show_outer_percentiles=False)
        


def generate_sentinel_measure(data_dict, data_dict_practice, codelist_dict, measure, code_column, term_column, dates_list, interactive=True):
    df = data_dict[measure]
    childs_df = create_child_table(df, codelist_dict[measure], code_column, term_column, measure)

    practices_included, practices_included_percent, num_events_mil, num_patients = calculate_statistics(
        df, measure, dates_list)


    df = data_dict_practice[measure]
    convert_datetime(df)
    calculate_rate(df, measure, 'population')
    
    # idr_list = [get_idr(df, dates_list)[x]
    #             for x in dates_list]


    # median_list = [get_median(df, dates_list)[x]
    #            for x in dates_list]

    # change_list = calculate_change_median(median_list)

    print(f'Practices included: {practices_included} ({practices_included_percent}%)')
    print(f'Total patients: {num_patients:.2f}M ({num_events_mil:.2f}M events)')
    # print(
    #     f'Feb Median: {median_list[0]:.1f} (IDR: {idr_list[0]:.1f}), April Median: {median_list[1]:.1f} (IDR: {idr_list[1]:.1f}), Dec Median: {median_list[2]:.1f} (IDR: {idr_list[2]:.1f})')
    # print(
    #     f'Change in median from Feb 2020: April: {change_list[0]:.2f}%; December: {change_list[1]:.2f}%')
    
    display(HTML(childs_df.to_html()))

    deciles_chart(
        df,
        period_column="date",
        column="num_per_thousand",
        ylabel="rate per 1000",
        interactive=interactive
    )
    






