from flask import request, jsonify
from flask_restful import Resource
import pandas as pd
from helpers import get_age_group, remove_outliers, add_age_group, standardize_tests_results, filter_by_normal_values, \
    append_results_without_diagnoses, get_filters_description
from queries import get_samples_results, get_patients_with_diagnose, get_test_name, get_test_unit_name


class Boxplot(Resource):
    def post(self):
        data = request.json
        filter = data['filter']
        test_id = data['testId']
        age_interval = int(data['ageInterval'])
        groupByDiagnose = data['groupByDiagnose'] if 'groupByDiagnose' in data else None
        samples_results = get_samples_results(test_ids=[test_id], filters=data['filter'])
        df = pd.DataFrame(samples_results)
        if groupByDiagnose is not None:
            patients_with_diagnose = list(
                map(lambda patient: patient.id, get_patients_with_diagnose(groupByDiagnose['id'])))
            df['has_diagnose'] = df['patient_id'].apply(lambda x: x in patients_with_diagnose)
        df['result'] = df['result'].astype(float)
        if data['standardize']:
            df = standardize_tests_results(df)
        if 'resultsNormal' in filter:
            if data['standardize']:
                df = filter_by_normal_values(df, filter)
            else:
                df_standardized = standardize_tests_results(df)
                df_filtered = filter_by_normal_values(df_standardized, filter)
                df = df.iloc[df_filtered.index.tolist()]
        df = add_age_group(df, age_interval)
        groupped_results = df.groupby(by=['age_group', 'patient_id'])
        result = {
            'groups': {},
            'test_name': get_test_name(test_id),
            'unit': get_test_unit_name(test_id),
            'filter_description': get_filters_description(filter),
            'standardize': data['standardize']
        }
        for group, name in groupped_results.groups:
            result['groups'][group] = {
                'values': [],
                'patient_ids': []
            }
        if groupByDiagnose is not None:
            groupped_patients = df.groupby('patient_id')
            result['patient_ids'] = list(groupped_patients.groups)
            result['has_diagnose'] = list(map(lambda x: bool(x), groupped_patients['has_diagnose'].mean().values))
        for age_range, patient_id in groupped_results.groups:
            values = list(groupped_results.get_group((age_range, patient_id))["result"].values)
            result['groups'][age_range]['values'].extend(values)
            result['groups'][age_range]['patient_ids'].extend(
                [patient_id] * len(values))
        return jsonify(result)
