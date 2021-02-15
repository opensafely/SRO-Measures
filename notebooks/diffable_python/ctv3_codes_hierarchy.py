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

dbconn = os.environ.get('DBCONN', None)
if dbconn is None:
    display("No SQL credentials. Check that the file 'environ.txt' is present. Refer to readme for further information")
else:
    dbconn = dbconn.strip('"')

# import custom functions from 'analysis' folder
import sys
sys.path.append('../lib/')
    
from functions import plotting_all, closing_connection
# -

# ## Inspect Top-Level CTV3 Codes

# +
sql = '''select 
LEFT(CTV3Code,1) AS first_digit,
'1' AS digits,
Description
from CTV3Dictionary
where RIGHT(CTV3Code,4)='....' 
and LEFT(CTV3Code,1) NOT IN (
'.', -- Read thesaurus
'0', -- occupations
'9') -- Administration
'''

pd.set_option('display.max_rows', 200)
with closing_connection(dbconn) as connection:
    codes = pd.read_sql(sql, connection)
codes
# -

# ## Inspect Level 2 CTV3 Codes

# +
digit = "1"

sql = f'''select 
LEFT(CTV3Code,2) AS first_digit,
'2' AS digits,
Description
from CTV3Dictionary
where RIGHT(CTV3Code,3)='...' 
AND RIGHT(CTV3Code,4)!='....' 
and CAST(LEFT(CTV3Code,1) AS VARCHAR) = '{digit}'
'''

pd.set_option('display.max_rows', 200)
with closing_connection(dbconn) as connection:
    codes = pd.read_sql(sql, connection)
codes

# -

# ## Create table of level 1 and level 2 CTV3 codes

# +
digit = "2"

sql = f'''select 
LEFT(CTV3Code,CHARINDEX('.',CTV3Code)-1) AS first_digit,
CHARINDEX('.',CTV3Code)-1 AS digits,
Description
from CTV3Dictionary
where (RIGHT(CTV3Code,3)='...' OR RIGHT(CTV3Code,4)='....')
and LEFT(CTV3Code,1) NOT IN (
'.', -- Read thesaurus
'0', -- occupations
'1', -- History/symptoms
'9') -- Administration
'''

pd.set_option('display.max_rows', 200)
with closing_connection(dbconn) as connection:
    codes = pd.read_sql(sql, connection)
codes
# -

# ## Create table of level 2 & 3 CTV3 codes

# +
digit = "4"

sql = f'''select 
LEFT(CTV3Code,CHARINDEX('.',CTV3Code)-1) AS first_digit,
CHARINDEX('.',CTV3Code)-1 AS digits,
Description
from CTV3Dictionary
where RIGHT(CTV3Code,2)='..' --(select codes like '123..')
and RIGHT(CTV3Code,4)!='....' --(don't select codes like '1....')
and LEFT(CTV3Code,1) NOT IN ('.') -- Read thesaurus
and LEFT(CTV3Code,1) = '{digit}'
'''

pd.set_option('display.max_rows', 400)
with closing_connection(dbconn) as connection:
    codes_l3 = pd.read_sql(sql, connection)

codes_l3
# -

# ## Rank level 2 codes by frequency of appearance in 2020

# +
highlevelcode='4'
subset = codes.loc[codes["first_digit"].str[0]== highlevelcode]

codelist = tuple(subset.first_digit)

# select events for selcted subset of codelist
sql = f'''select LEFT(CTV3Code,2) AS first_digit, COUNT(Patient_ID) as events
FROM CodedEvent 
WHERE 
ConsultationDate IS NOT NULL 
AND CAST(LEFT(CTV3Code,2) AS VARCHAR) IN {codelist}
AND YEAR(ConsultationDate) = 2020
GROUP BY LEFT(CTV3Code,2)
'''
with closing_connection(dbconn) as connection:
    df = pd.read_sql(sql, connection).sort_values(by="events", ascending=False)
top_l2 = df.merge(subset, on="first_digit", how="left")

top_l2 = top_l2.loc[top_l2["events"]>100000]
top_l2["events (millions)"] = round(top_l2["events"]/1000000, 2)
top_l2 = top_l2.drop("events", axis=1)
top_l2.head(30)

# -

# ## Rank level 3 codes by frequency of appearance in 2020

# +
codelist = tuple(codes_l3.first_digit)

# select events for selcted subset of codelist
sql = f'''select TOP 50 
LEFT(CTV3Code,3) AS first_digit, COUNT(Patient_ID) as events
FROM CodedEvent 
WHERE 
ConsultationDate IS NOT NULL 
AND CAST(LEFT(CTV3Code,3) AS VARCHAR) IN {codelist}
AND YEAR(ConsultationDate) = 2020
GROUP BY LEFT(CTV3Code,3)
ORDER BY events DESC
'''

with closing_connection(dbconn) as connection:
    df = pd.read_sql(sql, connection).sort_values(by="events", ascending=False)
top_l3 = df.merge(codes_l3, on="first_digit", how="left")

top_l3 = top_l3.loc[top_l3["events"]>10000]
top_l3["events (millions)"] = round(top_l3["events"]/1000000, 2)
top_l3 = top_l3.drop("events", axis=1)
top_l3.head(30)
