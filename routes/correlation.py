from flask_restful import Resource
from flask import request, jsonify
import pandas as pd
import scipy.stats
import numpy as np

from helpers import filter_by_normal_values, standardize_tests_results, get_filters_description
from queries import get_samples_results, get_test_name


class Correlation(Resource):
    def post(self):
        data = request.json
        filter = data['filter'] if 'filter' in data else None
        test_ids = list(map(lambda x: x['value'], data['testIds']))
        samples_results = get_samples_results(test_ids=test_ids, filters=filter, have_all_tests=True)
        df = pd.DataFrame(samples_results)
        df['result'] = df['result'].astype(float)
        df = standardize_tests_results(df)
        if 'resultsNormal' in filter:
            df = filter_by_normal_values(df, filter)
        groupped_results = df.groupby(by=['test_id', 'patient_id']).mean()
        data = list(map(lambda test_id: groupped_results.loc[test_id,]['result'].tolist(), test_ids))
        result = np.corrcoef(data).round(decimals=2)
        return jsonify({
            'tests': list(map(lambda x: get_test_name(x), test_ids)),
            'values': result,
            'filter_description': get_filters_description(filter)
        })
