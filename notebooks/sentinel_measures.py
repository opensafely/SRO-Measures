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
# * [2469: O/E - Systolic BP reading](#systolic_bp)
# * ["XaQVY" - QRISK2 cardiovascular disease 10 risk score](#qrisk2)
# * ["XE2eD" - Serum Cholesterol level](#cholesterol)
# * ["44E" - Serum Bilirubin level](#bilirubin)
# * ["XaELV" - Serum TSH level](#serum_tsh)
# * ["426" - Red blood cell count](#rbc_fbc)
# * ["XaPbt" - Haemoglobin A1c level - IFCC standardised](#hba1c)
# * ["XE2q0" - Serum Sodium level](#serum_sodium)
# * ["Xaleq" - Asthma annual review](#asthma)
# * ["Xalet" - Chronic obstrutive pulmonary disease annual review](#copd)

# +
from IPython.display import HTML
import pandas as pd
import matplotlib.pyplot as plt
from utilities import *

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# %matplotlib inline

# +
sentinel_measures = ["systolic_bp", "qrisk2", "serum_cholesterol", "serum_bilirubin", "serum_tsh", "rbc", "hba1c", "serum_sodium", "asthma", "copd"]

data_dict = {}

for measure in sentinel_measures:
    df = load_and_drop(measure)
    data_dict[measure] = df
    
data_dict_practice = {}

for measure in sentinel_measures:
    df = load_and_drop(measure, practice=True)
    data_dict_practice[measure] = df

sentinel_measure_codelist_mapping_dict = {"systolic_bp":"opensafely-chronic-respiratory-disease", "qrisk2":"opensafely-chronic-respiratory-disease", "serum_cholesterol": "opensafely-chronic-respiratory-disease", "serum_bilirubin": "opensafely-chronic-respiratory-disease", "serum_tsh": "opensafely-chronic-respiratory-disease", "rbc": "opensafely-chronic-respiratory-disease", "hba1c": "opensafely-chronic-respiratory-disease", "serum_sodium": "opensafely-chronic-respiratory-disease", "asthma": "opensafely-chronic-respiratory-disease", "copd": "opensafely-chronic-respiratory-disease"}

codelist_dict = {}
for measure in sentinel_measures:
    codelist_name = sentinel_measure_codelist_mapping_dict[measure]
    codelist = pd.read_csv(f'../codelists/{codelist_name}.csv')
    codelist_dict[measure] = codelist
# -

# <a id="systolic_bp"></a>
# ### 2469: O/E - Systolic BP
#
# Description:

generate_sentinel_measure(data_dict, data_dict_practice, codelist_dict, 'systolic_bp', 'CTV3ID', 'CTV3PreferredTermDesc', ["2020-02-01", "2020-04-01", "2020-12-01"])

# <a id="qrisk"></a>
# ### "XaQVY" - QRISK2 Cardiovascular Disease 10 year risk score

generate_sentinel_measure(data_dict, data_dict_practice, codelist_dict, 'qrisk2', 'CTV3ID', 'CTV3PreferredTermDesc', ["2020-02-01", "2020-04-01", "2020-12-01"])

# <a id="cholesterol"></a>
# ### "XE2eD" - Serum Cholesterol Level

generate_sentinel_measure(data_dict, data_dict_practice, codelist_dict, 'serum_cholesterol', 'CTV3ID', 'CTV3PreferredTermDesc', ["2020-02-01", "2020-04-01", "2020-12-01"])

# <a id="bilirubin"></a>
# ### "44E" - Serum Bilirubin Level

generate_sentinel_measure(data_dict, data_dict_practice, codelist_dict, 'serum_bilirubin', 'CTV3ID', 'CTV3PreferredTermDesc', ["2020-02-01", "2020-04-01", "2020-12-01"])

# <a id="serum_tsh"></a>
# ### "XaELV" - Serum TSH Level

generate_sentinel_measure(data_dict, data_dict_practice, codelist_dict, 'serum_tsh', 'CTV3ID', 'CTV3PreferredTermDesc', ["2020-02-01", "2020-04-01", "2020-12-01"])

# <a id="rbc_fbc"></a>
# ### "426" - Red Blood Cell Count

generate_sentinel_measure(data_dict, data_dict_practice, codelist_dict, 'rbc', 'CTV3ID', 'CTV3PreferredTermDesc', ["2020-02-01", "2020-04-01", "2020-12-01"])

# <a id="hba1c"></a>
# ### "XaPbt" - Haemoglobin A1c Level - IFCC Standardised

generate_sentinel_measure(data_dict, data_dict_practice, codelist_dict, 'hba1c', 'CTV3ID', 'CTV3PreferredTermDesc', ["2020-02-01", "2020-04-01", "2020-12-01"])

# <a id="serum_sodium"></a>
# ### "XE2q0" - Serum Sodium Level

generate_sentinel_measure(data_dict, data_dict_practice, codelist_dict, 'serum_sodium', 'CTV3ID', 'CTV3PreferredTermDesc', ["2020-02-01", "2020-04-01", "2020-12-01"])

# <a id="asthma"></a>
# ### "Xaleq" - Asthma Annual Review

generate_sentinel_measure(data_dict, data_dict_practice, codelist_dict, 'asthma', 'CTV3ID', 'CTV3PreferredTermDesc', ["2020-02-01", "2020-04-01", "2020-12-01"])

# <a id="copd"></a>
# ### "Xalet" - Chronic Obstructive Pulmonary Disease Annual Review

# +
generate_sentinel_measure(data_dict, data_dict_practice, codelist_dict, 'copd', 'CTV3ID', 'CTV3PreferredTermDesc', ["2020-02-01", "2020-04-01", "2020-12-01"])


