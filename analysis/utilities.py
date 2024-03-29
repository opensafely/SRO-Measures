import json
from pathlib import Path
import re
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
from IPython.display import HTML, display, Markdown

BASE_DIR = Path(__file__).parents[1]
OUTPUT_DIR = BASE_DIR / "output"


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

BASE_DIR = Path(__file__).parents[1]
OUTPUT_DIR = BASE_DIR / "output"


def load_and_drop(measure, practice=False):
    """Loads the measure table for the measure with the given ID.

    Drops irrelevant practices and produces stripped measures

    Args:
        measure: The measure ID.
        practice: Whether to load the "practice only" measure.

    Returns:
        The table for the given measure ID and practice.
    """
    if practice:
        f_in = OUTPUT_DIR / f"measure_{measure}_practice_only_rate.csv"
    else:
        f_in = OUTPUT_DIR / f"measure_{measure}_rate.csv"

    df = pd.read_csv(f_in, parse_dates=["date"])

    if practice:
        df = drop_irrelevant_practices(df)
        df = produce_stripped_measures(df, measure)

    else:

        df = drop_irrelevant_practices(df)

    return df


def convert_ethnicity(df):
    ethnicity_codes = {
        1.0: "White",
        2.0: "Mixed",
        3.0: "Asian",
        4.0: "Black",
        5.0: "Other",
        np.nan: "unknown",
        0: "unknown",
    }

    df = df.replace({"ethnicity": ethnicity_codes})
    return df


def calculate_rate(df, value_col, population_col, round_rate=False):
    """Calculates the number of events per 1,000 of the population.

    This function operates on the given measure table in-place, adding
    a `num_per_thousand` column.

    Args:
        df: A measure table.
        value_col: The name of the numerator column in the measure table.
        population_col: The name of the denominator column in the measure table.
        round: Bool indicating whether to round rate to 2dp.
    """
    if round_rate:
        num_per_thousand = round(df[value_col] / (df[population_col] / 1000), 2)

    else:
        num_per_thousand = df[value_col] / (df[population_col] / 1000)

    df["rate"] = num_per_thousand


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


def create_child_table(df, code_df, code_column, term_column, measure, nrows=5):
    """
    Args:
        df: A measure table.
        code_df: A codelist table.
        code_column: The name of the code column in the codelist table.
        term_column: The name of the term column in the codelist table.
        measure: The measure ID.
        nrows: The number of rows to display.

    Returns:
        A table of the top `nrows` codes.
    """
    event_counts = (
        df.groupby(f"{measure}_event_code")[f"{measure}"]
        .sum()  # We can't use .count() because the measure column contains zeros.
        .rename_axis(code_column)
        .rename("Events")
        .reset_index()
        .sort_values("Events", ascending=False)
    )

    # calculate % makeup of each code
    total_events = event_counts["Events"].sum()
    event_counts["Proportion of codes (%)"] = round(
        (event_counts["Events"] / total_events) * 100, 2
    )

    # Gets the human-friendly description of the code for the given row
    # e.g. "Systolic blood pressure".
    code_df = code_df.set_index(code_column).rename(
        columns={term_column: "Description"}
    )
    event_counts = event_counts.set_index(code_column).join(code_df).reset_index()

    # Cast the code to an integer.
    event_counts[code_column] = event_counts[code_column].astype(int)

    # check that codes not in the top 5 rows have >5 events
    outside_top_5_percent = 1 - ((event_counts.head(5)["Events"].sum()) / total_events)

    if 0 < (outside_top_5_percent * total_events) <= 5:
        # drop percent column
        event_counts = event_counts.loc[:, ["code", "Description"]]

    else:
        # give more logical column ordering
        event_counts_with_count = event_counts.loc[
            :, ["code", "Description", "Events", "Proportion of codes (%)"]
        ]

        event_counts = event_counts.loc[
            :, ["code", "Description", "Proportion of codes (%)"]
        ]

    if len(event_counts["code"]) > 1:
        event_counts.loc[
            event_counts["Proportion of codes (%)"] == 0, "Proportion of codes (%)"
        ] = "< 0.005"
        event_counts.loc[
            event_counts["Proportion of codes (%)"] == 100, "Proportion of codes (%)"
        ] = "> 99.995"

        event_counts_with_count.loc[
            event_counts_with_count["Proportion of codes (%)"] == 0,
            "Proportion of codes (%)",
        ] = "< 0.005"
        event_counts_with_count.loc[
            event_counts_with_count["Proportion of codes (%)"] == 100,
            "Proportion of codes (%)",
        ] = "> 99.995"

    # return top n rows
    return event_counts.head(5), event_counts_with_count.head()


def get_number_practices(df):
    """Gets the number of practices in the given measure table.

    Args:
        df: A measure table.
    """
    return len(df.practice.unique())


def get_percentage_practices(measure_table):
    """Gets the percentage of practices in the given measure table.

    Args:
        measure_table: A measure table.
    """
    with open(OUTPUT_DIR / "practice_count.json") as f:
        num_practices = json.load(f)["num_practices"]

    num_practices_in_study = get_number_practices(measure_table)

    return np.round((num_practices_in_study / num_practices) * 100, 2)


def get_number_events_mil(measure_table, measure_id):
    """Gets the number of events per million, rounded to 2DP.

    Args:
        measure_table: A measure table.
        measure_id: The measure ID.
    """
    num_events = measure_table[measure_id].sum()
    return num_events, np.round(num_events / 1_000_000, 2)


def get_number_patients(measure_id):
    """Gets the number of patients.

    Args:
        measure_id: The measure ID.
    """
    with open(OUTPUT_DIR / "patient_count.json") as f:
        d = json.load(f)
    return d["num_patients"][measure_id]


# https://github.com/ebmdatalab/datalab-pandas/blob/master/ebmdatalab/charts.py
def deciles_chart_ebm(
    df,
    period_column=None,
    column=None,
    title="",
    ylabel="",
    show_outer_percentiles=True,
    show_legend=True,
    ax=None,
    output_path=None,
):
    """period_column must be dates / datetimes"""
    sns.set_style("whitegrid", {"grid.color": ".9"})
    if not ax:
        fig, ax = plt.subplots(1, 1)
    df = compute_deciles(df, period_column, column, show_outer_percentiles)
    linestyles = {
        "decile": {
            "line": "b--",
            "linewidth": 1,
            "label": "decile",
        },
        "median": {
            "line": "b-",
            "linewidth": 1.5,
            "label": "median",
        },
        "percentile": {
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
            label=label,
        )
    ax.set_ylabel(ylabel, size=15, alpha=0.6)
    if title:
        ax.set_title(title, size=18)

    # Replace 'np.inf' and '-np.inf' with 'NaN'
    df[column].replace([np.inf, -np.inf], np.nan, inplace=True)

    # Drop rows with NaN in the specified column
    df.dropna(subset=[column], inplace=True)

    if not df[column].empty:
        ax.set_ylim([0, df[column].max() * 1.05])
    
    ax.tick_params(labelsize=12)

    df[period_column].replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(subset=[period_column], inplace=True)

    if not df[period_column].empty:
        ax.set_xlim(
            [df[period_column].min(), df[period_column].max()]
        )  # set x axis range as full date range

    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%B %Y"))
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=1))
    if show_legend:
        ax.legend(
            bbox_to_anchor=(1.05, 0.6),
            ncol=1,
            fontsize=12,
            borderaxespad=0.0,
            frameon=True,
        )

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    plt.gcf().autofmt_xdate(rotation=90, ha="center", which="both")

    plt.show()

    if output_path:
        ax.get_figure().savefig(output_path, bbox_inches="tight")
        

    return plt


def compute_deciles(measure_table, groupby_col, values_col, has_outer_percentiles=True):
    """Computes deciles.

    Args:
        measure_table: A measure table.
        groupby_col: The name of the column to group by.
        values_col: The name of the column for which deciles are computed.
        has_outer_percentiles: Whether to compute the nine largest and nine smallest
            percentiles as well as the deciles.

    Returns:
        A data frame with `groupby_col`, `values_col`, and `percentile` columns.
    """
    quantiles = np.round(np.arange(0.1, 1, 0.1), 2)
    if has_outer_percentiles:
        quantiles = np.concatenate(
            [quantiles, np.round(np.arange(0.01, 0.1, 0.01), 2), np.round(np.arange(0.91, 1, 0.01), 2)]
        )
    
    percentiles = (
        measure_table.groupby(groupby_col)[values_col]
        .quantile(pd.Series(quantiles))
        .reset_index()
    )
   
    percentiles["percentile"] = percentiles["level_1"].apply(lambda x: int(x * 100))
    percentiles = percentiles.loc[:, [groupby_col, "percentile", values_col]]
    return percentiles


def deciles_chart(
    df,
    period_column=None,
    column=None,
    title="",
    ylabel="",
    interactive=True,
    width=800,
    height=400,
    output_path=None,
):
    """period_column must be dates / datetimes"""

    df = compute_deciles(df, period_column, column, True)

    if interactive:

        fig = go.Figure()

        linestyles = {
            "decile": {"color": "blue", "dash": "dash"},
            "median": {"color": "blue", "dash": "solid"},
            "percentile": {"color": "blue", "dash": "dash"},
        }

        for percentile in np.unique(df["percentile"]):
            df_subset = df[df["percentile"] == percentile]
            if percentile == 50:
                fig.add_trace(
                    go.Scatter(
                        x=df_subset[period_column],
                        y=df_subset[column],
                        line={"color": "blue", "dash": "solid", "width": 1.2},
                        name="median",
                    )
                )
            else:
                fig.add_trace(
                    go.Scatter(
                        x=df_subset[period_column],
                        y=df_subset[column],
                        line={"color": "blue", "dash": "dash", "width": 1},
                        name=f"decile {int(percentile/10)}",
                    )
                )

        # Set title
        fig.update_layout(
            title_text=title,
            hovermode="x",
            title_x=0.5,
            width=width,
            height=height,
        )

        fig.update_yaxes(title=ylabel)
        fig.update_xaxes(title="Date")

        # Add range slider
        fig.update_layout(
            xaxis=go.layout.XAxis(
                rangeselector=dict(
                    buttons=list(
                        [
                            dict(
                                count=1,
                                label="1m",
                                step="month",
                                stepmode="backward",
                            ),
                            dict(
                                count=6,
                                label="6m",
                                step="month",
                                stepmode="backward",
                            ),
                            dict(
                                count=1,
                                label="1y",
                                step="year",
                                stepmode="backward",
                            ),
                            dict(step="all"),
                        ]
                    )
                ),
                rangeslider=dict(visible=True),
                type="date",
            )
        )

        fig.show()

    else:
        px = 1 / plt.rcParams["figure.dpi"]  # pixel in inches
        fig, ax = plt.subplots(
            1, 1, figsize=(width * px, height * px), tight_layout=True
        )

        deciles_chart_ebm(
            df,
            period_column=period_column,
            column=column,
            ylabel="rate per 1000",
            show_outer_percentiles=True,
            ax=ax,
            output_path=output_path,
        )


def generate_sentinel_measure(
    data_dict,
    data_dict_practice,
    codelist_dict,
    measure,
    code_column,
    term_column,
    dates_list,
    codelist_links,
    interactive=True,
):
    """Generates tables and charts for the measure with the given ID.

    Args:
        data_dict: A mapping of measure IDs to measure tables.
        data_dict_practice: A mapping of measure IDs to "practice only" measure tables.
        codelist_dict: A mapping of measure IDs to codelist tables.
        measure: A measure ID.
        code_column: The name of the code column in the codelist table.
        term_column: The name of the term column in the codelist table.
        dates_list: Not used.
        interactive: Flag indicating whether or not the chart should be interactive.
    """
    df = data_dict[measure]

    childs_df, childs_df_with_count = create_child_table(
        df, codelist_dict[measure], code_column, term_column, measure
    )

    practices_included = get_number_practices(df)
    practices_included_percent = get_percentage_practices(df)

    num_events, num_events_mil = get_number_events_mil(df, measure)

    num_patients = get_number_patients(measure)

    num_practices_df = pd.DataFrame(
        {"num_practices_included": pd.Series([practices_included])}
    )
    num_practices_df.to_csv(
        f"{OUTPUT_DIR}/num_practices_included_{measure}.csv", index=False
    )

    df = data_dict_practice[measure]

    deciles_chart(
        df,
        period_column="date",
        column="rate",
        ylabel="rate per 1000",
        interactive=interactive,
    )

    display(
        Markdown(f"Practices included: {practices_included} ({practices_included_percent:.2f}%)"),
    )

    childs_df = childs_df.rename(columns={code_column: code_column.title()})
    childs_df.to_csv(f"{OUTPUT_DIR}/code_table_{measure}.csv")

    childs_df_with_count = childs_df_with_count.rename(
        columns={code_column: code_column.title()}
    )
    childs_df_with_count.to_csv(f"{OUTPUT_DIR}/code_table_{measure}_with_count.csv")

    if len(codelist_links)>1:
        display(
            Markdown(f"#### Most Common Codes <a href={codelist_links[0]}>(Codelist 1)</a>, <a href={codelist_links[1]}>(Codelist 2)</a>"),
            HTML(childs_df.to_html(index=False)),
        )

    else:
        display(
            Markdown(f"#### Most Common Codes <a href={codelist_links[0]}>(Codelist)</a>"),
            HTML(childs_df.to_html(index=False)),
        )

    display(
        Markdown(f"Total patients: {num_patients:.2f}M ({num_events_mil:.2f}M events)"),
    )

    return df, num_events


def calculate_imd_group(df, disease_column, rate_column):
    imd_column = pd.to_numeric(df["imd"])
    df["imd"] = pd.qcut(
        imd_column,
        q=5,
        duplicates="drop",
        labels=["Most deprived", "2", "3", "4", "Least deprived"],
    )

    df_rate = (
        df.groupby(by=["date", "imd", "practice"])[[rate_column]].mean().reset_index()
    )

    df_population = (
        df.groupby(by=["date", "imd", "practice"])[[disease_column, "population"]]
        .sum()
        .reset_index()
    )

    df_merged = df_rate.merge(
        df_population, on=["date", "imd", "practice"], how="inner"
    )

    return df_merged


def redact_small_numbers(df, n, numerator, denominator, rate_column, date_column):
    """
    Takes counts df as input and suppresses low numbers.  Sequentially redacts
    low numbers from numerator and denominator until count of redcted values >=n.
    Rates corresponding to redacted values are also redacted.

    df: input df
    n: threshold for low number suppression
    numerator: numerator column to be redacted
    denominator: denominator column to be redacted
    """

    def suppress_column(column):
        suppressed_count = column[column <= n].sum()

        # if 0 dont need to suppress anything
        if suppressed_count == 0:
            pass

        else:
            column[column <= n] = np.nan

            while suppressed_count <= n:
                suppressed_count += column.min()

                column[column.idxmin()] = np.nan
        return column

    df_list = []

    dates = df[date_column].unique()

    for d in dates:
        df_subset = df.loc[df[date_column] == d, :]

        for column in [numerator, denominator]:
            df_subset[column] = suppress_column(df_subset[column])

        df_subset.loc[
            (df_subset[numerator].isna()) | (df_subset[denominator].isna()),
            rate_column,
        ] = np.nan
        df_list.append(df_subset)

    return pd.concat(df_list, axis=0)


def calculate_statistics(df, baseline_date, comparative_dates):
    """Calculates % change between given dates

    Args:
        df: measures dataframe with rate column
        baseline_date: date to use as baseline. Format: YYYY-MM-DD.
        comparative_dates: list of dates to comare to baseline.

    returns:
        list of % differences
    """
    median_baseline = round(df[df["date"] == baseline_date]["rate"].median(), 2)
    differences = []
    values = []
    for date in comparative_dates:
        value = round(df[df["date"] == date]["rate"].median(), 2)
        difference = round(((value - median_baseline) / median_baseline) * 100, 2)
        differences.append(difference)
        values.append(round(value, 2))

    return median_baseline, values, differences


def classify_changes(changes):
    """Classifies list of % changes

    Args:
        changes: list of percentage changes
    """

    if (-15 <= changes[0] < 15) and (-15 <= changes[1] < 15):
        classification = "no change"

    elif (changes[0] > 15) or (changes[1] > 15):
        classification = "increase"

    elif (changes[0] <= -15) and not (-15 <= changes[1] < 15):
        classification = "sustained drop"

    elif (changes[0] <= -15) and (-15 <= changes[1] < 15):
        classification = "recovery"

    else:
        classification = "none"

    display(Markdown(f"Overall classification: **{classification}**"))


def display_changes(baseline, values, changes, dates):
    """Display % changes at given dates

    Args:
        changes: list of % changes
        dates: list of readable dates changes refer to
    """

    for value, change, date in zip(values, changes, dates):
        display(
            Markdown(
                f"Change in median from April 2019 ({baseline}) - {date} ({value}): **{change}%**"
            )
        )


def match_input_files(file: str) -> bool:
    """Checks if file name has format outputted by cohort extractor"""
    pattern = r"^input_20\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])\.feather"
    return True if re.match(pattern, file) else False


def get_date_input_file(file: str) -> str:
    """Gets the date in format YYYY-MM-DD from input file name string"""
    # check format
    if not match_input_files(file):
        raise Exception("Not valid input file format")

    else:
        date = result = re.search(r"input_(.*)\.feather", file)
        return date.group(1)


def produce_stripped_measures(df, sentinel_measure):
    """Takes in a practice level measures file, calculates rate and strips
    persistent id,including only a rate and date column. Rates are rounded
    and the df is randomly shuffled to remove any potentially predictive ordering.
    Returns stripped df
    """

    # drop irrelevant practices
    df = drop_irrelevant_practices(df)

    # calculate rounded rate
    calculate_rate(df, sentinel_measure, "population", round_rate=True)
    df = df.loc[:, ["rate", "date"]]
    # randomly shuffle (resetting index)
    return df.sample(frac=1).reset_index(drop=True)


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


def get_patients_left_tpp(df, df_comparison, demographics):
    """Identifies patients not in a given monthly extract who were in another (previous extract).
    Excludes patients who are not present because they have since died. Extracts demographics
    for these patients.

    Args:
        df: input dataframe to identify patients in
        df_comparison: input dataframe to compare to. This should be earlier than df.
        demographics: list of demographics to extract for patients who have left.

    returns:
        dataframe of all patients who have left and their demographics
    """

    # anyone in the first month but not in monthly cohort of people
    patients_left = df_comparison.loc[
        ~df_comparison["patient_id"].isin(df.loc[:, "patient_id"]), "patient_id"
    ]
   
    # demographics of those people in a given month (from first month)
    demographics_patients_left = (
        df_comparison.loc[
            df_comparison["patient_id"].isin(patients_left),
            :
        ].reindex(columns = ["patient_id"] + demographics)
        .reset_index()
        .drop(["index"], axis=1)
    )

    # lets assume the people who leave go to EMIS
    demographics_patients_left["ehr_provider"] = "EMIS"
    return demographics_patients_left


def get_patients_joined_tpp(
    df, df_first_month, age_column, age_start_column, demographics
):
    """Identifies patients in a given monthly extract who are not in another (previous extract).
    Excludes patients if they are present because they now satisfy the age criteria. Extracts demographics
    for these patients.

    Args:
        df: input dataframe to identify patients in
        df_comparison: input dataframe to compare to. This should be earlier than df.
        age_column: colum in df that identifies the age of a patient in that month.
        age_start_column: column in df that identifies the age of a patient at the start.
        demographics: list of demographics to extract for patients who have left.

    returns:
        dataframe of all patients who have joined and their demographics
    """

    # any patients in monthly cohort who didn't become eligible by turning 18 in study
    patients_adults = df.loc[
        ~(df[age_start_column] <= 17), "patient_id"
    ]

    # anyone of these patients who were not in the first month
    patients_joined = patients_adults[
        ~patients_adults.isin(df_first_month["patient_id"])
    ]

    demographics_patients_joined = (
        
        df.loc[
            df["patient_id"].isin(patients_joined),
            :
        ].reindex(columns = ["patient_id"] + demographics)
        .reset_index()
        .drop(["index"], axis=1)
    )
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
        if name != "patient_id":

            count = values.value_counts(dropna=False).to_dict()
            for key, value in count.items():
                if value <=10:
                    value = np.nan
                
                count[key] = round_values(value, 5)
                

            dem_counts[name] = count

    return total_moved, dem_counts


def save_dict_as_json(dict, output_path):
    """Saves dictionary as json"""
    with open(output_path, "w") as f:
        json.dump(dict, f)

def round_values(x, base=5):
    rounded = x
    if isinstance(x, (int, float)):
        if np.isnan(x):
            rounded = np.nan
        else:
            rounded = int(base * round(x / base))
    return rounded
