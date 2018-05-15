import pandas as pd
import numpy as np
import sys

if sys.argv[1] and sys.argv[2]:
    input_path = sys.argv[1]
    output_path = sys.argv[2]
else:
    input_path = 'output_medium/solution.csv'
    output_path = 'output_medium/test.csv'


def get_rel_max(df):
    df = df.copy()
    maxi = df.groupby('id')['goalfunction'].transform(np.max)
    df['rel max'] = 1 - ((maxi - df.goalfunction)/maxi)

    return df


def strip_id(df):
    df = df.copy()
    id_list = df.id.tolist()
    id_list = [''.join(s for s in i if s.isdigit()) for i in id_list]
    df.id = id_list
    return df


def difference(df, column, target):
    df = df.copy()
    arr = df[column]
    diff = abs(arr - target)
    return diff


def main():

    # read data and preprocess
    df = pd.read_csv(input_path, sep=',')
    df = get_rel_max(df)
    df = strip_id(df)

    # separate the data for each factor
    times = range(0, 61, 1)
    x_1 = df[df['first x'] == 1]
    x_5 = df[df['first x'] == 5]
    x_10 = df[df['first x'] == 10]

    empty_df = pd.DataFrame(columns=['first x', 'goalfunction', 'id', 'tabu tenure', 'time', 'rel max'])

    for x in [x_1, x_5, x_10]:
        for i in times:

            x['diff'] = difference(x, 'time', i)

            # takes the smallest difference between time and target for each group in the dataframe
            temp = x.sort_values(by='diff').groupby('id').head(1)
            empty_df = empty_df.append(temp)

    empty_df = empty_df.drop(['diff'], axis=1)
    empty_df = empty_df.sort_values(by=['id', 'time'])
    empty_df.to_csv(output_path, sep=',', index=False)


if __name__ == '__main__':
    main()
