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

# +
import pyodbc
import pandas as pd
import os
from IPython.display import display, Markdown
from datetime import date
import numpy as np

import matplotlib.pyplot as plt

dbconn = os.environ.get('DBCONN', None)
if dbconn is None:
    display("No SQL credentials. Check that the file 'environ.txt' is present. Refer to readme for further information")
else:
    dbconn = dbconn.strip('"')

# import custom functions from 'analysis' folder
import sys
sys.path.append('../lib/')
    
from functions import closing_connection, load_filter_codelists, filter_codelists, plotting_all
codes = pd.read_csv(os.path.join('..','data','code_dictionary.csv'))

# +

sql1 = f'''select 
    CTV3Code,
    CASE CTV3Code
      WHEN 'X772q' THEN 'cholesterol-2'
      WHEN 'XaPbt' THEN 'cholesterol-1'
      WHEN 'XE2eB' THEN 'bilirubin'
      END AS name,
    DATEFROMPARTS(YEAR(ConsultationDate), MONTH(ConsultationDate),1) AS month,
    COUNT(*) as events
    FROM CodedEvent
    WHERE CTV3Code IN ('X772q', 'XaPbt', 'XE2eB')
    AND ConsultationDate > '20171231'
    GROUP BY CTV3Code, 
    CASE CTV3Code
      WHEN 'X772q' THEN 'cholesterol-2'
      WHEN 'XaPbt' THEN 'cholesterol-1'
      WHEN 'XE2eB' THEN 'bilirubin'
      END,
    DATEFROMPARTS(YEAR(ConsultationDate), MONTH(ConsultationDate), 1)'''

    
with closing_connection(dbconn) as connection:
    df = pd.read_sql(sql1, connection)
    
df

# +
sql1 = f'''select 
    COUNT(distinct Organisation_ID) as practices
    FROM RegistrationHistory
    WHERE YEAR(EndDate) = '9999'-- live registrations only
    '''

    
with closing_connection(dbconn) as connection:
    df = pd.read_sql(sql1, connection)
    
df

# +
sql1 = '''-- patient registrations
    SELECT
    Patient_ID,
    Organisation_ID AS Practice_ID,
    ROW_NUMBER() OVER (partition by Patient_ID ORDER BY StartDate DESC, EndDate DESC) AS registration_date_rank -- row_num gives unique results
    INTO #reg
    FROM RegistrationHistory
    WHERE YEAR(EndDate) = '9999'; -- live registrations only
    '''

sql2 = '''-- practice list size
    SELECT
    Organisation_ID AS Practice_ID,
    COUNT(DISTINCT Patient_ID) AS list_size
    INTO #listsize
    FROM RegistrationHistory
    WHERE YEAR(EndDate) = '9999' -- live registrations only  
    GROUP BY Organisation_ID
    '''

sql3 = f'''select 
    CTV3Code,
    CASE CTV3Code
      WHEN 'X772q' THEN 'cholesterol-2'
      WHEN 'XaPbt' THEN 'cholesterol-1'
      WHEN 'XE2eB' THEN 'bilirubin'
      END AS name,
    --DATEFROMPARTS(YEAR(ConsultationDate),MONTH(ConsultationDate),1) AS month, 
    CASE WHEN r.Practice_ID IS NOT NULL THEN 1 ELSE 0 END AS patient_currently_registered,
    COUNT(DISTINCT e.Patient_ID) as total_patients,
    COUNT(DISTINCT r.Practice_ID) as total_practices,
    count(*) as events
    --l.list_size as denominator
    --INTO #main
    FROM CodedEvent e
    LEFT JOIN #reg r ON e.Patient_ID = r.Patient_ID AND r.registration_date_rank = 1
    LEFT JOIN #listsize l ON r.Practice_ID = l.Practice_ID
    WHERE 
    ConsultationDate IS NOT NULL 
    AND CTV3Code IN ('X772q', 'XaPbt', 'XE2eB')
    AND ConsultationDate >= '20190101' 
    AND ConsultationDate < '20210101'
    GROUP BY 
    CTV3Code,     
    CASE CTV3Code
      WHEN 'X772q' THEN 'cholesterol-2'
      WHEN 'XaPbt' THEN 'cholesterol-1'
      WHEN 'XE2eB' THEN 'bilirubin'
      END,
    CASE WHEN r.Practice_ID IS NOT NULL THEN 1 ELSE 0 END--,
    --DATEFROMPARTS(YEAR(ConsultationDate), MONTH(ConsultationDate), 1)--, 
    --    r.Practice_ID, l.list_size
    --ORDER BY month
    '''

with closing_connection(dbconn) as connection:
    connection.execute(sql1) # patient registrations
    connection.execute(sql2) # practice list size
    df_new = pd.read_sql(sql3, connection)
    
df_new
# -

dff2 = df_new.copy()
dff2 = dff2.set_index(["month", "name","patient_currently_registered"])[["events"]].unstack()
dff2.columns= dff2.columns.droplevel()
dff2["percent_with_no_current_reg"] = 100*(dff2[0]/(dff2[0]+dff2[1])).round(2)
display(dff2[["percent_with_no_current_reg"]].unstack().sort_index().head(5))
display(dff2[["percent_with_no_current_reg"]].unstack().sort_index().tail(5))

# +
dff3 = df_new.copy()
dff3 = dff3.groupby(["month", "name"])[["total_practices"]].sum().unstack()
dff3.columns= dff3.columns.droplevel()
#dff2["percent_with_no_current_reg"] = 100*(dff2[0]/(dff2[0]+dff2[1])).round(2)
#display(dff2.sort_index().head(15))
#display(dff2.sort_index().tail(15))
dff3["bilirubin"].plot(legend=True, title="practice_count")
dff3["cholesterol-1"].plot(legend=True)
dff3["cholesterol-2"].plot(legend=True)

dff3

# +

df0 = df.copy().set_index("month")
df0 = df0.loc[df0.index < date(2020,12,1)]
df1 = df0[df0["name"]=="bilirubin"].sort_index()
df2 = df0[df0["name"]=="cholesterol-1"].sort_index()
df3 = df0[df0["name"]=="cholesterol-2"].sort_index()

df1["events"].plot(label="bilirubin", legend=True)
df2["events"].plot(label="cholesterol-1", legend=True)
df3["events"].plot(label="cholesterol-2", legend=True)


# +
keywords = ["Nervous system and mental state", "Neurotic, personality and other nonpsychotic disorders"]
highlevel, detailed = load_filter_codelists(keywords=keywords)

# descriptions for ctv3 codes    
codes = pd.read_csv(os.path.join('..','data','code_dictionary.csv'))

plotting_all(highlevel, codes, 3, 1000, dbconn, True)



# +
######################### customise ################################
# Create lists of keywords and/or CTV3 concepts to filter codelist
keywords = ["mental", "learning", "dementia", "deleri", "psycho", "depress", "anxi", "cogn"]
concepts = ["Mental health disorder"]

display(Markdown(f"## Load list of common codes from csv and filter to Mental Health activity only"))
####################################################################


highlevel, detailed = load_filter_codelists(keywords=keywords, concepts=concepts)

subset = highlevel.copy()
d = np.where(subset["digits"].max()==5, 3, 2)
c = subset.loc[subset["digits"]==d] # select only codes with the min number of digits 
                                        # (either all are 2, or there is a mix of 3 & 5, where only the 3-digit ones need a list of sub codes producing)
c = tuple(subset["first_digits"])

from functions import get_subcodes
subcodes = get_subcodes(c, codes, d, 1000, dbconn)
subcodes
