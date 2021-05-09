def remove_outliers(df, column):
    return df[((df[column] - df[column].mean()) / df[column].std()).abs() < 3]


def get_age_group(age, interval_length):
    left_border = age // interval_length * interval_length
    return left_border


def normalize_column(df, column_name, a, b):
    min = df[column_name].min()
    max = df[column_name].max()
    denominator = max - min
    df[column_name] = a + (((df[column_name] - min) / denominator) * (b - a))
    return df


def raw_sql_to_dict(raw_result):
    return [dict(row) for row in raw_result]
