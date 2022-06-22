# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# <h1 align="center">OpenSAFELY Service Restoration Observatory (SRO) - Changes in key GP measures during the pandemic</h1>
#
# The aim of the OpenSAFELY SRO is to describe trends and variation in clinical activity codes to evaluate NHS service restoration during the COVID-19 pandemic.
#
# The purpose of this notebook is to provide a set of key GP measures at the practice level, that are indicative of changes in overall activity during the pandemic.  For each of these measures we provide a link to the codelist containing all the codes used for that measure, a description of what the measure is and a brief overview of why the measure is important.  We also highlight any caveats, where there are any, for each measure.  
#
# Monthly rates of recorded activity are displayed as practice level decile charts to show both the general trend and practice level variation in activity changes. Accompanying each chart is a summary of the most commonly recorded SNOMED codes for each measure.
#
# For each measure we also indicate the number of unique patients recorded as having at least one event indicated by the measure as well as the total number of events since January 2019.
# A summary of the number of events for each measure is produced and monthly rates of recorded activity for each measure is plotted as a decile chart.
#
# For each measure, we also median activity rate in April 2019 (baseline) and the percentage change from this median in April 2020 (time of the 1st national lockdown) and April 2021.  These changes are used to give an overall classification of activity change as described in the box below.
#
# * No change: no change from baseline in both April 2020 and April 2021.
# * Increase: an increase from baseline in either April 2020 or April 2021.
# * Sustained drop: a drop from baseline of >15% in April 2020 which **has not** returned to within 15% of the baseline by April 2021.
# * Recovery: a drop of >15% from baseline in April 2020 which **has** returned to within 15% of the baseline by April 2021.
#
# The following key measures are provided:
#
# <ul id="docNav">
#     <li> <a href="#systolic_bp">Blood Pressure Monitoring</a>
#     <li> <a href="#qrisk2">Cardiovascular Disease 10 Year Risk Assessment</a>
#     <li> <a href="#cholesterol">Cholesterol Testing</a>
#     <li> <a href="#ALT">Liver Function Testing - Alanine Transferaminase (ALT)</a>
#     <li> <a href="#serum_tsh">Thyroid Testing</a>
#     <li> <a href="#rbc_fbc">Full Blood Count - Red Blood Cell (RBC) Testing</a>
#     <li> <a href="#hba1c">Glycated Haemoglobin A1c Level (HbA1c)</a>
#     <li> <a href="#serum_sodium">Renal Function Assessment - Sodium Testing</a>
#     <li> <a href="#asthma">Asthma Reviews</a>
#     <li> <a href="#copd">Chronic Obstrutive Pulmonary Disease (COPD) Reviews</a>
#     <li> <a href="#med_review">Medication Review</a>
# </ul>
#

# +
from IPython.display import HTML
import pandas as pd
import numpy as np
import itertools
import matplotlib.pyplot as plt
from utilities import *
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# %matplotlib inline
# %config InlineBackend.figure_format='png'


# +
# %%capture --no-display

sentinel_measures = ["qrisk2", "asthma", "copd", "sodium", "cholesterol", "alt", "tsh", "rbc", 'hba1c', 'systolic_bp', 'medication_review']


data_dict_practice = {}
childs_table_dict = {}



with open("../backend_outputs/emis/patient_count.json") as f:
        num_patients_emis = json.load(f)["num_patients"]

with open("../backend_outputs/emis/event_count.json") as f:
        num_events_emis = json.load(f)["num_events"]

with open("../backend_outputs/tpp/patient_count.json") as f:
        num_patients_tpp = json.load(f)["num_patients"]

with open("../backend_outputs/tpp/event_count.json") as f:
        num_events_tpp = json.load(f)["num_events"]

num_patients = {}
num_events = {}
for key, value in num_patients_emis.items():

        num_patients[key] = value + num_patients_tpp[key]

for key, value in num_events_emis.items():
        value = value/1_000_000
        num_events[key] = value + (num_events_tpp[key]/1_000_000)

for measure in sentinel_measures:
    df = pd.read_csv(f"../backend_outputs/measure_{measure}.csv", parse_dates=["date"])
    data_dict_practice[measure] = df
    child_table = pd.read_csv(f"../backend_outputs/code_table_{measure}.csv")
    childs_table_dict[measure] = child_table

def generate_sentinel_measure_combined(data_dict_practice, child_table, measure, num_patients, num_events, codelist_link):
        df = data_dict_practice[measure]

        deciles_chart(
                df,
                period_column="date",
                column="rate",
                ylabel="rate per 1000",
                interactive=False,
        )

        display(
                Markdown(f"#### Most Common Codes <a href={codelist_link}>(Codelist)</a>"),
                HTML(child_table.to_html(index=False)),
        )

        display(
                Markdown(f"Total patients: {num_patients:.2f}M ({num_events:.2f}M events)")
        )
        return df


# -

# <a id="systolic_bp"></a>
# ### Blood Pressure Monitoring
#
# The codes used in for this measure are available in <a href="https://www.opencodelists.org/codelist/opensafely/systolic-blood-pressure-qof/3572b5fb/">this codelist</a>.
#
# <h3 class="details">What it is </h3>
#
# Rate of systolic blood presure monitoring per 1000 members of the population.
#
# <h3 class="details">Why it matters</h3>
#
# * The measurement of blood pressure and identification and management of hypertension is important for both primary and secondary prevention of cardiovascular disease, such as stroke, myocardial infarction and kidney disease. 
# * If patients cannot have their blood pressure measurements acted on by primary care, they may not benefit from averting associated complications. 
# * Active management and prevention of these complications is generally provided by Primary Care; as a measure it would therefore be considered an important marker of access to and provision of care.

systolic_bp_df = generate_sentinel_measure_combined(data_dict_practice, childs_table_dict["systolic_bp"], "systolic_bp", num_patients["systolic_bp"], num_events["systolic_bp"], codelist_link="https://www.opencodelists.org/codelist/opensafely/systolic-blood-pressure-qof/3572b5fb/")

baseline, values, differences = calculate_statistics(systolic_bp_df, '2019-04-01', ['2020-04-01', '2021-04-01'])
display_changes(baseline, values, differences, ['April 2020', 'April 2021'])
classify_changes(differences)

# <a id="qrisk2"></a>
# ### Cardiovascular Disease 10 year Risk Assessment
#
# The codes used in for this measure are available in <a href="https://www.opencodelists.org/codelist/opensafely/cvd-risk-assessment-score-qof/1adf44a5/">this codelist</a>.
#
# <h3 class="details">What it is </h3>
#
# Rate of cardiovascular disease risk assessments performed per 1000 members of the population.
#
# <h3 class="details">Why it matters</h3>
#
# * Primary prevention of cardiovascular disease is recommended in all people above the age of 40 year, and in particular, in people with clinical conditions such as hypertension and diabetes are at greater risk. To determine an individual's risk of a cardiovascular event such as a myocardial infarction or stroke, an algorithm called QRISK2 is recommended. This estimates the likelihood of a cardiovascular event in the next 10 years, and individuals with a risk of at least 10% should have a discussion with their GP about starting a statin, or blood pressure treatment if they have Stage I hypertension.  
# * If patients are not receiving these risk assessments due to the COVID-19 pandemic, these higher risk patients may not be identified and effective preventative treatment may not be commenced.
# * Such risk factor assessment generally only occurs in primary care; it would therefore be considered an important marker of the provision and access to basic preventative care. So for example, the risk calculation requires at least a single cholesterol test and blood pressure readings.

qrisk2_df = generate_sentinel_measure_combined(data_dict_practice, childs_table_dict["qrisk2"], "qrisk2", num_patients["qrisk2"], num_events["qrisk2"], codelist_link="https://www.opencodelists.org/codelist/opensafely/cvd-risk-assessment-score-qof/1adf44a5/")

baseline, values, differences = calculate_statistics(qrisk2_df, '2019-04-01', ['2020-04-01', '2021-04-01'])
display_changes(baseline, values, differences, ['April 2020', 'April 2021'])
classify_changes(differences)

# <a id="cholesterol"></a>
# ### Cholesterol Testing
#
# The codes used in for this measure are available in <a href="https://www.opencodelists.org/codelist/opensafely/cholesterol-tests/09896c09/">this codelist</a>.
#
# <h3 class="details">What it is </h3>
#
# Rate of total cholesterol tests performed per 1000 members of the population.
#
# <h3 class="details">Why it matters</h3>
#
# * Cholesterol tests are used to estimate your risk of cardiovacular disease and to monitor treatment with cholesterol modifying drugs.  You can read more about this test and when it should be used <a href="https://labtestsonline.org.uk/tests/cholesterol-test">here</a>.
# * As with most blood tests, there has been debate about the appropriate level of testing but we have presented the information here to inform recovery from COVID-19 in order to “build back better”.
#
# <h3 class="details">Caveats</h3>
# Here, we use codes which represent results reported to GPs, so tests requested but not yet reported are not included. This will usually exclude tests requested while a person is in hospital and other settings, like a private clinic.

cholesterol_df = generate_sentinel_measure_combined(data_dict_practice, childs_table_dict["cholesterol"], "cholesterol", num_patients["cholesterol"], num_events["cholesterol"], codelist_link="https://www.opencodelists.org/codelist/opensafely/cholesterol-tests/09896c09/")

baseline, values, differences = calculate_statistics(cholesterol_df, '2019-04-01', ['2020-04-01', '2021-04-01'])
display_changes(baseline, values, differences, ['April 2020', 'April 2021'])
classify_changes(differences)

# <a id="ALT"></a>
# ### Liver Function Testing - Alanine Transferaminase (ALT)
#
# The codes used in for this measure are available in <a href="https://www.opencodelists.org/codelist/opensafely/alanine-aminotransferase-alt-tests/2298df3e/">this codelist</a>.
#
# <h3 class="details">What it is </h3>
#
# Rate of ALT tests performed per 1000 members of the population.
#
# <h3 class="details">Why it matters</h3>
#
# * ALT tests blood tests are used as a part of Liver Function Testing, a group of tests which detect problems with liver function. You can read more about this test and when it should be used <a href="https://labtestsonline.org.uk/tests/alanine-aminotransferase-alt-test">here</a>.
# * As with most blood tests, there has been debate about the appropriate level of testing but we have presented the information here to inform recovery from COVID-19 in order to “build back better”.
#
# <h3 class="details">Caveats</h3>
# **In a small number of places, an ALT test may NOT be included within a liver function test.** We use codes which represent results reported to GPs so tests requested but not yet reported are not included. Only tests results returned to GPs are included, which will usually exclude tests requested while a person is in hospital and other settings like a private clinic.

alt_df = generate_sentinel_measure_combined(data_dict_practice, childs_table_dict["alt"], "alt", num_patients["alt"], num_events["alt"], codelist_link="https://www.opencodelists.org/codelist/opensafely/alanine-aminotransferase-alt-tests/2298df3e/")

baseline, values, differences = calculate_statistics(alt_df, '2019-04-01', ['2020-04-01', '2021-04-01'])
display_changes(baseline, values, differences, ['April 2020', 'April 2021'])
classify_changes(differences)

# <a id="serum_tsh"></a>
# ### Thyroid Testing
#
# The codes used in for this measure are available in <a href="https://www.opencodelists.org/codelist/opensafely/thyroid-stimulating-hormone-tsh-testing/11a1abeb/">this codelist</a>.
#
# <h3 class="details">What it is </h3>
#
# Rate of thyroid-stimulating hormone (TSH) tests performed per 1000 members of the population.
#
# <h3 class="details">Why it matters</h3>
#
# * Thyroid stimulating hormone (TSH) is a blood test used for diagnosis and monitoring of hypothyroidism and hyperthyroidism. You can read more about this test and <a href="https://labtestsonline.org.uk/tests/thyroid-stimulating-hormone-tsh">when TSH should be used here </a>and NICE have produced guidance on the assessment and <a href="https://www.nice.org.uk/guidance/ng145/chapter/recommendations">management of thyroid disease here</a>. 
# * As with most blood tests, there has been debate about the appropriate level of testing but we have presented the information here to inform recovery from COVID-19 in order to “build back better”.
#
# <h3 class="details">Caveats</h3>
# Here, we use codes which represent results reported to GPs, so tests requested but not yet reported are not included. This will usually exclude tests requested while a person is in hospital and other settings, like a private clinic.

tsh_df = generate_sentinel_measure_combined(data_dict_practice, childs_table_dict["tsh"], "tsh", num_patients["tsh"], num_events["tsh"], codelist_link="https://www.opencodelists.org/codelist/opensafely/thyroid-stimulating-hormone-tsh-testing/11a1abeb/")

baseline, values, differences = calculate_statistics(tsh_df, '2019-04-01', ['2020-04-01', '2021-04-01'])
display_changes(baseline, values, differences, ['April 2020', 'April 2021'])
classify_changes(differences)

# <a id="rbc_fbc"></a>
# ### Full Blood Count - Red Blood Cell (RBC) Testing
#
# The codes used in for this measure are available in <a href="https://www.opencodelists.org/codelist/opensafely/red-blood-cell-rbc-tests/576a859e/">this codelist</a>.
#
# <h3 class="details">What it is </h3>
#
# Rate of RBC count tests performed per 1000 members of the population.
#
# <h3 class="details">Why it matters</h3>
#
# * RBC count tests are used as a part of a Full Blood Count, a group of tests which can detect a variety of disorders of the blood, such as anaemia and infection. You can read more about this test and when it should be used <a href="https://labtestsonline.org.uk/tests/red-blood-cell-count">here</a>.
# *  As with most blood tests, there has been debate about the appropriate level of testing but we have presented the information here to inform recovery from COVID-19 in order to “build back better”.
#
# <h3 class="details">Caveats</h3>
# Here, we use codes which represent results reported to GPs, so tests requested but not yet reported are not included. This will usually exclude tests requested while a person is in hospital and other settings, like a private clinic.

rbc_df = generate_sentinel_measure_combined(data_dict_practice, childs_table_dict["rbc"], "rbc", num_patients["rbc"], num_events["rbc"], codelist_link="https://www.opencodelists.org/codelist/opensafely/red-blood-cell-rbc-tests/576a859e/")

baseline, values, differences = calculate_statistics(rbc_df, '2019-04-01', ['2020-04-01', '2021-04-01'])
display_changes(baseline, values, differences, ['April 2020', 'April 2021'])
classify_changes(differences)

# <a id="hba1c"></a>
# ### Glycated Haemoglobin A1c Level (HbA1c)
#
# The codes used in for this measure are available in <a href="https://www.opencodelists.org/codelist/opensafely/glycated-haemoglobin-hba1c-tests/62358576/">this codelist</a>.
#
# <h3 class="details">What it is </h3>
#
# Rate of HbA1c tests performed per 1000 members of the population.
#
# <h3 class="details">Why it matters</h3>
#
# * HbA1c is a measure of blood glucose levels. It is used to make the diagnosis of type 2 diabetes as well as to monitor the average blood glucose in those with recorded diabetes. It is recommended that everyone with diabetes has HbA1c measured at least twice a year.
# * If HbA1c is not been monitored regularly, patients may not be identified as having poor diabetes control, and therefore there is a greater risk of complications.  You can read more about this test and when it should be used <a href="https://labtestsonline.org.uk/tests/hba1c-test">here</a>.
# *  As with most blood tests, there has been debate about the appropriate level of testing but we have presented the information here to inform recovery from COVID-19 in order to “build back better”.
#
# <h3 class="details">Caveats</h3>
# Here, we use codes which represent results reported to GPs, so tests requested but not yet reported are not included. This will usually exclude tests requested while a person is in hospital and other settings, like a private clinic.

hba1c_df = generate_sentinel_measure_combined(data_dict_practice, childs_table_dict["hba1c"], "hba1c", num_patients["hba1c"], num_events["hba1c"], codelist_link="https://www.opencodelists.org/codelist/opensafely/glycated-haemoglobin-hba1c-tests/62358576/")

baseline, values, differences = calculate_statistics(hba1c_df, '2019-04-01', ['2020-04-01', '2021-04-01'])
display_changes(baseline, values, differences, ['April 2020', 'April 2021'])
classify_changes(differences)

# <a id="serum_sodium"></a>
# ### Renal Function Assessment - Sodium Testing
#
# The codes used in for this measure are available in <a href="https://www.opencodelists.org/codelist/opensafely/sodium-tests-numerical-value/32bff605/">this codelist</a>.
#
# <h3 class="details">What it is </h3>
#
# Rate of sodium blood tests performed per 1000 members of the population.
#
# <h3 class="details">Why it matters</h3>
#
# * Sodium blood test is used to detect the cause and help monitor treatment in persons with dehydration, oedema, or with a variety of other symptoms. It is routinely tested for with other blood electrolytes including those used to detect kidney disease. You can read more about <a href="https://labtestsonline.org.uk/tests/sodium-test">sodium tests and when it should be used here</a>.
# *  As with most blood tests, there has been debate about the appropriate level of testing but we have presented the information here to inform recovery from COVID-19 in order to “build back better”.
#
# <h3 class="details">Caveats</h3>
# Here, we use codes which represent results reported to GPs, so tests requested but not yet reported are not included. This will usually exclude tests requested while a person is in hospital and other settings, like a private clinic.

sodium_df = generate_sentinel_measure_combined(data_dict_practice, childs_table_dict["sodium"], "sodium", num_patients["sodium"], num_events["sodium"], codelist_link="https://www.opencodelists.org/codelist/opensafely/sodium-tests-numerical-value/32bff605/")

baseline, values, differences = calculate_statistics(sodium_df, '2019-04-01', ['2020-04-01', '2021-04-01'])
display_changes(baseline, values, differences, ['April 2020', 'April 2021'])
classify_changes(differences)

# <a id="asthma"></a>
# ### Asthma Reviews
#
# The codes used in for this measure are available in <a href="https://www.opencodelists.org/codelist/opensafely/asthma-annual-review-qof/33eeb7da/">this codelist</a>.  QoF recommends a number of codes that can be used by practices as an asthma annual review.  These are all included in our codelist.
#
# <h3 class="details">What it is </h3>
#
# Rate of asthma reviews performed per 1000 members of the population.
#
# <h3 class="details">Why it matters</h3>
#
# * It is recommended that people with asthma receive a review of their condition at least annually, in order to ensure that their asthma is well controlled and that they are using their inhalers correctly.  
# * If patients have not received an annual during the time of the pandemic, it is possible that their asthma control may have worsened, leading to greater chance of symptoms and admission.
# * The Quality and Outcomes Framework (QoF) recommends a number of codes that can be used by practices as an asthma annual review.  These are all included in our codelist.

asthma_df = generate_sentinel_measure_combined(data_dict_practice, childs_table_dict["asthma"], "asthma", num_patients["asthma"], num_events["asthma"], codelist_link="https://www.opencodelists.org/codelist/opensafely/asthma-annual-review-qof/33eeb7da/")

baseline, values, differences = calculate_statistics(asthma_df, '2019-04-01', ['2020-04-01', '2021-04-01'])
display_changes(baseline, values, differences, ['April 2020', 'April 2021'])
classify_changes(differences)
classify_changes([differences[0], differences[2]])

# <a id="copd"></a>
# ### Chronic Obstructive Pulmonary Disease (COPD) Reviews
#
# The codes used in for this measure are available in <a href="https://www.opencodelists.org/codelist/opensafely/chronic-obstructive-pulmonary-disease-copd-review-qof/01cfd170/">this codelist</a>.  
#
# <h3 class="details">What it is </h3>
#
# Rate of COPD reviews (primarily annual reviews, but also includes codes for 6 month and 3 month reviews) performed per 1000 members of the population.
#
# <h3 class="details">Why it matters</h3>
#
# * It is <a href="https://www.nice.org.uk/guidance/ng115/chapter/Recommendations">recommended by NICE</a> that all individuals living with COPD have an annual review, with individuals with very severe (stage 4) COPD being reviewed at least twice a year.
# * The purpose of the review is multifaceted, but includes, for example, smoking cessation support, review of symptoms and optimising treatment. The annual COPD review is also a feature of <a href="https://www.england.nhs.uk/wp-content/uploads/2020/09/C0713-202021-General-Medical-Services-GMS-contract-Quality-and-Outcomes-Framework-QOF-Guidance.pdf">QOF</a>, which supports practices to deliver quality care.
# * As COPD is a chronic progressive disease with significant morbidity and mortality (especially in more severe cases), a reduction in reviews due to the COVID-19 pandemic could not only lead to worsening disease (and associated complications) but also significant social and economic detriment. 

copd_df = generate_sentinel_measure_combined(data_dict_practice, childs_table_dict["copd"], "copd", num_patients["copd"], num_events["copd"], codelist_link="https://www.opencodelists.org/codelist/opensafely/chronic-obstructive-pulmonary-disease-copd-review-qof/01cfd170/")

baseline, values, differences = calculate_statistics(copd_df, '2019-04-01', ['2020-04-01', '2021-04-01'])
display_changes(baseline, values, differences, ['April 2020', 'April 2021'])
classify_changes(differences)

# <a id="med_review"></a>
# ### Medication Reviews
#
# The codes used in for this measure are a combination of codes available in <a href="https://www.opencodelists.org/codelist/opensafely/care-planning-medication-review-simple-reference-set-nhs-digital/61b13c39/">this NHS Digitatil medication planning refset</a> and <a href="https://www.opencodelists.org/codelist/nhsd-primary-care-domain-refsets/medrvw_cod/20200812/">this primary care domain medication review refset</a>.
#  
# <h3 class="details">What it is </h3>
#
# Rate of recording of codes related to medication reviews performed per 1000 members of the population.
#
# <h3 class="details">Why it matters</h3>
#
# * Many medicines are used long-term and they should be reviewed regularly to ensure they are still appropriate.
# * Medication review is a broad term encompassing encompassing a range of types of review, from notes-led review without a patient, to in depth Structured Medication Reviews with multiple appointments and follow-ups. The codelist provided captures all these types of reviews to give an overall picture of medicines reviews.
# * NICE have advice on guidance about <a href="https://pathways.nice.org.uk/pathways/medicines-optimisation/medication-review#content">medication reviews here</a> and NHS England has published guidance on <a href="https://www.england.nhs.uk/wp-content/uploads/2020/09/SMR-Spec-Guidance-2020-21-FINAL-.pdf">Structured Medication Reviews</a> which are an intervention aimed at complex or problematic polypharmacy.

medication_review_df = generate_sentinel_measure_combined(data_dict_practice, childs_table_dict["medication_review"], "medication_review", num_patients["medication_review"], num_events["medication_review"], codelist_link="https://www.opencodelists.org/codelist/opensafely/care-planning-medication-review-simple-reference-set-nhs-digital/61b13c39/")

baseline, values, differences = calculate_statistics(medication_review_df, '2019-04-01', ['2020-04-01', '2021-04-01'])
display_changes(baseline, values, differences, ['April 2020', 'April 2021'])
classify_changes(differences)


# +
def deciles_chart_subplots(
    df,
    period_column=None,
    column=None,
    title="",
    ylabel="",
    show_outer_percentiles=True,
    show_legend=True,
    ax=None,
):
    """period_column must be dates / datetimes"""
    sns.set_style("whitegrid", {"grid.color": ".9"})
    
    
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
    ax.set_ylabel(ylabel, size=14)
    if title:
        ax.set_title(title, size=20)
    # set ymax across all subplots as largest value across dataset
    ax.set_ylim([0, df[column].max() * 1.05])
    ax.tick_params(labelsize=14)
    ax.set_xlim(
        [df[period_column].min(), df[period_column].max()]
    )  # set x axis range as full date range
    
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%B %Y"))
    if show_legend:
        ax.legend(
            bbox_to_anchor=(0.25, -0.8),  # arbitrary location in axes
            #  specified as (x0, y0, w, h)
            loc=CENTER_LEFT,  # which part of the bounding box should
            #  be placed at bbox_to_anchor
            ncol=1,  # number of columns in the legend
            fontsize=28,
            borderaxespad=0.0,
        )  # padding between the axes and legend
        #  specified in font-size units
    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    plt.gcf().autofmt_xdate()
    return plt

x = np.arange(0, 6, 1)
y = np.arange(0, 2, 1)

axs_list = [(i, j) for i in x for j in y]
fig, axs = plt.subplots(6, 2, figsize=(15,30), sharex='col')
fig.delaxes(axs[5, 1])

sentinel_measures = ["qrisk2", "asthma", "copd", "sodium", "cholesterol", "alt", "tsh", "rbc", 'hba1c', 'systolic_bp', 'medication_review']

titles = ['Cardiovascular disease risk assessment', 'Asthma review', 'COPD review', 'Renal assessment', 'Cholesterol testing', 'Liver function testing', 'Thyroid testing', 'Full blood count testing', 'Glycated haemoglobin testing', 'Blood pressure monitoring', 'Medication review']

for x, measure in enumerate(sentinel_measures):
    
    df = data_dict_practice[measure]
    
    
    
    if axs_list[x] == (4, 1):
        show_legend = True
    
    else:
        show_legend=False
        
        
       
    deciles_chart_subplots(df,
        period_column='date',
        column='rate',
        title=titles[x],
        ylabel="Rate per 1000",
        show_outer_percentiles=False,
        show_legend=show_legend,
        ax=axs[axs_list[x]])
 
fig.savefig('../output/sentinel_measures_subplots.png')
plt.close()
# -




