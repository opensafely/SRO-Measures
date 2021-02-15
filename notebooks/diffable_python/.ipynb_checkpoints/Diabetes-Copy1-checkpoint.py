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

import pyodbc
import pandas as pd
from IPython.display import display, Markdown
import os

server = 'covid.ebmdatalab.net,1433'
database = 'OPENCoronaExport' 
username = 'SA'
password = 'ahsjdkaJAMSHDA123[' 
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

# import diabetes codelist
diabetes = pd.read_csv(os.path.join('..','codelists','opensafely-diabetes-2020-04-15.csv'), usecols=["CTV3ID"])
diabetes.head()

# # All diabetes patients

import numpy as np
codelist = diabetes['CTV3ID'].values.tolist()
l = tuple(codelist)
params = {'l': l}

# +
query = '''--diabetes patients
SELECT Patient_ID
FROM CodedEvent
WHERE CTV3Code IN {}
'''.format(l)

df = pd.read_sql(query, cnxn)
df
# -

# # Diabetic retinopathy screening

# +
'''--diabetes patients
SELECT Patient_ID,
CAST(ConsultationDate AS date) as ConsultationDate,
CASE WHEN  CTV3Code IN('XaJOD','XaPjM','XaJkQ') THEN 1 else 0 end as exclusion_flag, 
CASE WHEN CTV3Code = 'XaPaa' THEN 1 
WHEN CTV3Code IN () THEN 0 end as eligible_flag, --Eligible or ineligible for diabetic retinopathy screening 
FROM CodedEvent
WHERE CTV3Code IN (
'XaIIj', --Diabetic retinopathy screening
'XaKaW', --Diabetic retinopathy screening offered
'XaMFF', --Referral for diabetic retinopathy screening
'XaLsL', --Diabetic digital retinopathy screening offered
'XaJOD', --Diabetic retinopathy screening not indicated
'XaPjM', --Declined diabetic retinopathy screening 
'XaJkQ', --Diabetic retinopathy screening refused
-- eligibility:
'XaPad', --Eligibility permanently inactive for diabetic retinopathy screening 
'XaPac', --Eligibility temporarily inactive for diabetic retinopathy screening 
'XaPaa', --Eligible for diabetic retinopathy screening 
'XaPjR', --Excluded from diabetic retinopathy screening 
'XaPab', --Ineligible for diabetic retinopathy screening 
'XaLP3', --Referral to diabetic eye clinic
'XaEJQ'  --Seen in diabetic eye clinic
)
'''

eye_screen = pd.read_sql(query, cnxn)
eye_screen 
