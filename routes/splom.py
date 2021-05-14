from flask_restful import Resource
from flask import request, jsonify

from helpers import standardize_tests_results, filter_by_normal_values, append_results_without_diagnoses, \
    get_filters_description
from queries import get_samples_results, get_test_name, get_patients_with_diagnose
import pandas as pd


class Splom(Resource):
    def post(self):
        data = request.json
        test_ids = data['testIds']
        filter = data['filter']
        diagnose = data['diagnose']
        samples_results = get_samples_results(test_ids=test_ids, filters=filter, have_all_tests=True)
        df = pd.DataFrame(samples_results)
        if diagnose is not None:
            patients_ids_with_diagnoses = list(map(lambda x: x.id, get_patients_with_diagnose(diagnose['value'])))
            df['has_diagnose'] = df['patient_id'].apply(lambda x: x in patients_ids_with_diagnoses)
        if data['standardize']:
            df = standardize_tests_results(df)
        if 'resultsNormal' in filter:
            if data['standardize']:
                df = filter_by_normal_values(df, filter)
            else:
                df_standardized = standardize_tests_results(df)
                df_filtered = filter_by_normal_values(df_standardized, filter)
                df = df.iloc[df_filtered.index.tolist()]
        df['result'] = df['result'].astype(float)
        df['age'] = df['age'].astype(int)
        groupped_patients = df.groupby('patient_id')
        groupped_results = df.groupby(by=['patient_id', 'test_id'])
        results = groupped_results['result'].mean()
        result = {
            'patient_ids': list(groupped_patients.groups),
            'values': {
                'Возраст': list(groupped_patients['age'].mean().values)
            },
            'filter_description': get_filters_description(filter),
            'tests': list(map(lambda x: get_test_name(x), test_ids)),
            'diagnose': diagnose['label'] if diagnose is not None else '',
            'standardize': data['standardize']
        }
        if diagnose is not None:
            result['has_diagnose'] = list(map(lambda x: bool(x), groupped_patients['has_diagnose'].mean().values))
        tests = {}
        for test_id in test_ids:
            test_name = get_test_name(test_id)
            tests[test_id] = test_name
            result['values'][test_name] = []
        for index, value in results.items():
            result['values'][tests[index[1]]].append(value)
        return jsonify(result)
