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
from ebmdatalab import charts
import matplotlib.gridspec as gridspec

import importlib
importlib.reload(charts)

import pyodbc
import pandas as pd
from IPython.display import display, Markdown
# -

# ## Deciles
#
# Given a dataframe with a date column and a values column, compute
# percentiles for each date and plot them in a line chart.

# +


# make a datafrom with a date column and a values column
df = pd.DataFrame(np.random.rand(1000, 1), columns=['val'])
months = pd.date_range('2018-01-01', periods=12, freq='M')
df['month'] = pd.to_datetime(np.random.choice(months, len(df)))

charts.deciles_chart(
        df,
        period_column='month',
        column='val',
        title="Random values",
        ylabel="n",
        show_outer_percentiles=True,
        show_legend=True
)

# Now add a single line against the deciles
df_subject = pd.DataFrame(np.random.rand(12, 1), columns=['val']) * 100
df_subject['month'] = months
df_subject.set_index('month')

plt.plot(df_subject['month'], df_subject['val'], 'r--')
plt.show()



