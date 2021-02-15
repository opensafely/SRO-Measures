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

import pandas as pd
import numpy as np
from datetime import timedelta
from IPython.display import display, Markdown

# # create dummy data

# +
# practices
prac = np.arange(1,21,1)

prac = pd.DataFrame(prac, columns=["practice"])
prac['key'] = 0

prac.head(1)

# +
# months
months = pd.date_range(start='2017-05-31', end='2020-06-01', freq="M")
months = months + timedelta(1)
months = pd.DataFrame(months, columns=["month"])
months['key'] = 0

months.head(1)

# +
pts = np.arange(1,21,1)

prac = pd.DataFrame(prac, columns=["practice"])
prac['key'] = 0

prac.head(1)
# -

df1 = months.merge(prac, how='outer', on="key")
df1 = df1.merge(measures, how="outer", on="key").drop("key", axis=1)
df1.info()

# values
df1["values"] = np.random.normal(0.5,0.1,df1.month.count())
df1.loc[df1["month"]>="2020-03-01", "values"] = df1["values"] / 1.2
df1



# # Plot Deciles

# +
for m in df1.measure.drop_duplicates():
    charts.deciles_chart(
        df1.loc[df1["measure"] == m],
        period_column='month',
        column='values',
        title=m,
        ylabel="proportion",
        show_outer_percentiles=True,
        show_legend=True
    )

    # Now add a single line against the deciles
    df_subject = pd.DataFrame(np.random.normal(0.6, 0.05, 37), columns=['val'])
    df_subject['month'] = months["month"].drop_duplicates()
    df_subject.set_index('month')

    plt.plot(df_subject['month'], df_subject['val'], 'r--')
    plt.show()



