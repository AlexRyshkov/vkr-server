from flask_restful import Resource
from flask import request, jsonify
from scipy import stats

from helpers import standardize_tests_results, filter_by_normal_values, append_results_without_diagnoses, \
    get_filters_description
from queries import get_samples_results, get_test_name
import pandas as pd


class Histogram(Resource):
    def post(self):
        data = request.json
        test_ids = list(map(lambda x: x['value'], data['testIds']))
        filter = data['filter']
        samples_results = get_samples_results(test_ids=test_ids, filters=filter)
        df = pd.DataFrame(samples_results)
        if data['standardize']:
            df = standardize_tests_results(df)
        if 'resultsNormal' in filter:
            if data['standardize']:
                df = filter_by_normal_values(df, filter)
            else:
                df_standardized = standardize_tests_results(df)
                df_filtered = filter_by_normal_values(df_standardized, filter)
                df = df.iloc[df_filtered.index.tolist()]
        # df = df.loc[-5 <= (df['result'] <= 5)]
        result = {
            'values': {},
            'filter_description': get_filters_description(filter),
            'tests': list(map(lambda x: get_test_name(x), test_ids)),
            'standardize': data['standardize']
        }
        for test_id in test_ids:
            test_name = get_test_name(test_id)
            result['values'][test_name] = list(df.loc[(df['test_id'] == test_id)]['result'])
        return result
