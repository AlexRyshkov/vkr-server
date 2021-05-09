import numpy as np
from flask import request, jsonify
from flask_restful import Resource
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

from helpers import remove_outliers
from queries import get_samples_results, get_test_name

k_max = 5


class Cluster(Resource):
    def post(self):
        data = request.json
        test1_id = data['testId1']
        test2_id = data['testId2']
        test3_id = data['testId3']
        n_clusters = int(data['clustersCount'])
        test1_name = get_test_name(test1_id)
        test2_name = get_test_name(test2_id)
        test3_name = get_test_name(test3_id)
        samples_results = get_samples_results(test_ids=[test1_id, test2_id, test3_id], filters=data['filter'])
        tests_df = pd.DataFrame(samples_results)
        tests_df['result'] = tests_df['result'].astype(float)
        test1_df = tests_df.loc[tests_df['test_id'] == test1_id]
        test2_df = tests_df.loc[tests_df['test_id'] == test2_id]
        test3_df = tests_df.loc[tests_df['test_id'] == test3_id]
        test1_df = remove_outliers(test1_df, 'result')
        test2_df = remove_outliers(test2_df, 'result')
        test3_df = remove_outliers(test3_df, 'result')
        patients = list(set(test1_df['patient_id'].unique()) &
                        set(test2_df['patient_id'].unique()) &
                        set(test3_df['patient_id'].unique()))
        patients.sort()
        test1_df = test1_df[test1_df['patient_id'].isin(patients)]
        test2_df = test2_df[test2_df['patient_id'].isin(patients)]
        test3_df = test3_df[test3_df['patient_id'].isin(patients)]
        x1 = test1_df.groupby('patient_id')['result'].mean().values
        x2 = test2_df.groupby('patient_id')['result'].mean().values
        x3 = test3_df.groupby('patient_id')['result'].mean().values
        x = []
        for i in range(len(x1)):
            x.append([x1[i], x2[i], x3[i]])
        X = StandardScaler().fit_transform(np.array(x))
        best_k = -1
        max_score = -1
        for k in range(2, k_max + 1):
            kmeans = KMeans(n_clusters=k).fit(X)
            labels = kmeans.labels_
            score = silhouette_score(X, labels, metric='euclidean')
            if score > max_score:
                best_k = k
                max_score = score
        kmeans = KMeans(n_clusters=best_k).fit(X)
        labels = kmeans.labels_
        if len(labels) != len(x1) != len(x2) != len(x3) != len(patients):
            raise ValueError('TODO')
        return jsonify({
            'labels': labels,
            'clustersCount': n_clusters,
            'pointsCount': len(labels),
            'patientsIds': patients,
            'x': {'label': test1_name, 'coords': x1},
            'y': {'label': test2_name, 'coords': x2},
            'z': {'label': test3_name, 'coords': x3},
        })
