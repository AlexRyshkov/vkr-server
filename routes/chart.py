from flask import request
from flask_restful import Resource
import pandas as pd
from helpers import get_age_group, remove_outliers
from queries import get_samples_results


class Chart(Resource):
    def post(self):
        data = request.json
        test_id = data['testId']
        age_interval = int(data['ageInterval'])
        samples_results = get_samples_results(test_ids=[test_id], filters=data['filter'])
        df = pd.DataFrame(samples_results)
        df['result'] = df['result'].astype(float)
        df = remove_outliers(df, 'result')
        quant_column = df.groupby('patient_id')['result'].mean()
        df = df.drop_duplicates('patient_id')
        df['result'] = df['patient_id'].apply(lambda x: quant_column[x])
        if age_interval == 1:
            df = df.groupby('age')
        else:
            df['age_group'] = df['age'].apply(lambda age: get_age_group(age, age_interval))
            df = df.groupby('age_group')
        median = df['result'].median()
        min = df['result'].min()
        max = df['result'].max()
        quantile_bottom = df['result'].quantile(.25)
        quantile_top = df['result'].quantile(.75)
        group_names = list(df.groups.keys())
        group_sizes = df.size()
        labels = []
        if age_interval == 1:
            for i, group_name in enumerate(group_names):
                labels.append(f'{group_name} ({group_sizes.iloc[i]})')
        else:
            for i, group_name in enumerate(group_names):
                labels.append(f'{group_name} - {group_name + age_interval} ({group_sizes.iloc[i]})')
        return {
            'labels': labels,
            'median': list(median.array),
            'min': list(min.array),
            'max': list(max.array),
            'quantile_bottom': list(quantile_bottom.array),
            'quantile_top': list(quantile_top.array)
        }
