import pandas as pd
import numpy as np
import sys

path = sys.argv[1]
df = pd.read_csv(path, sep=',', decimal=',')

# extract the columns

cols = df.cols
cols = cols.drop([('unique_id', 'random order', 'tabu tenure', 'first x'])
data = df[cols]
data_raw = data.values

# if the range is 60 bins
for i in range(60):
    data_raw[:, i+1] = np.where(pd.isnull(data_raw[:, i+1]), data_raw[:, i], data_raw[:, i+1])

df.loc[:, 4:65] = data_raw

"""
test.to_csv('test.csv', sep=',', decimal='.')
"""

quit()

