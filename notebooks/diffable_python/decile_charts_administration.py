# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all
#     notebook_metadata_filter: all,-language_info
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

# # Changes occurring in primary care ADMINISTRATION activity during the pandemic
#
# ## Producing decile charts to show activity across all practices in TPP

# +
import pyodbc
import pandas as pd
import os
from IPython.display import display, Markdown

# import custom functions from 'analysis' folder
import sys
sys.path.append('../lib/')
    
from functions import plotting_all, closing_connection
# -

server = 'covid.ebmdatalab.net,1433'
database = 'OPENCoronaExport' 
username = 'SA'
password = 'ahsjdkaJAMSHDA123[' 
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

# real data
server = '192.168.201.1'
database = 'OpenCorona' 
username = 'REDACTED'
password = 'REDACTED'
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

# +
# global variables 
if server == '192.168.201.1':
    threshold = 1000 # min activity threshold
else:
    threshold = 1

credentials = {
    "server":server, 
    "database":database, 
    "username":username, 
    "password":password}

concept = "Administration"
# -

Markdown(f"# Load data from csv and filter to {concept} only")

# +
codes = pd.read_csv(os.path.join('..','data','code_dictionary.csv'))

top_l2 = pd.read_csv(os.path.join("..","output","level_two_codes.csv"))
top_l2 = top_l2.loc[top_l2["concept_desc"]==concept]

combined = pd.read_csv(os.path.join("..","output","combined_codelist.csv"))
combined = combined.loc[combined["concept_desc"]==concept]

display(len(top_l2))
display(len(combined))
# -

# # Plotting charts
# ### NB Practice denominators (list size) and patient registrations only include current patients
# ### will need to be amended to per-month denominators

# # Top 150 full / L3 codes

plotting_all(combined, codes, 43, threshold, credentials, True)
