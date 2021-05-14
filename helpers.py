from queries import get_normal_values, get_samples_results
import pandas as pd


def remove_outliers(df, column):
    return df[((df[column] - df[column].mean()) / df[column].std()).abs() < 3]


def get_age_group(age, interval_length):
    left_border = age // interval_length * interval_length
    return f'{left_border} - {left_border + interval_length} лет'


def add_age_group(df, age_interval, age_column='age'):
    if age_interval == 1:
        df['age_group'] = df[age_column]
    else:
        df['age_group'] = df[age_column].apply(lambda age: get_age_group(age, age_interval))
    return df


def standardize_tests_results(df, results_column='result'):
    """
    Стандартизация значений биохимических показателей в датафрейме
    :param df: датафрейм со значениями биохимических показателей
    :param results_column: колонка датафрейма, в которую будет записан результат нормализации
    :return: датафрейм с нормализованными значениями биохимических показателей
    """
    test_ids = df['test_id'].unique()
    for test_id in test_ids:
        normal_values = get_normal_values(test_id)
        for normal_value in normal_values:
            df = standardize_tests_results_for_patients_category(df, test_id, normal_value, results_column)
    return df


def standardize_tests_results_for_patients_category(df_original, test_id, category_normal_values, results_column):
    """
    Стандартизация значений указанного биохимического показателя для определённой категории пациентов
    :param df: датафрейм со значениями биохимических показателей
    :param test_id: id биохимического показателя
    :param category_normal_values: нормальные значения для категории пациентов
    :param results_column: колонка датафрейма, в которую будет записан результат нормализации
    :return: датафрейм с нормализованными значениями указанного биохимического показателя для определённой категории пациентов
    """
    df = df_original.copy()
    min = category_normal_values.min
    max = category_normal_values.max
    denominator = max - min
    if category_normal_values.patient_category == 'all':
        df.loc[df['test_id'] == test_id, results_column] = (df[results_column] - min) / denominator
    if category_normal_values.patient_category == 'male':
        df.loc[(df['test_id'] == test_id) & (df['gender'] == 'm'), results_column] = (df[
                                                                                          results_column] - min) / denominator
    if category_normal_values.patient_category == 'female':
        df.loc[(df['test_id'] == test_id) & (df['gender'] == 'f'), results_column] = (df[
                                                                                          results_column] - min) / denominator
    if category_normal_values.patient_category == 'child':
        df.loc[(df['test_id'] == test_id) & (df['age'] in [1, 18]), results_column] = (df[
                                                                                           results_column] - min) / denominator
    if category_normal_values.patient_category == 'newborn':
        df.loc[(df['test_id'] == test_id) & (df['age'] in [0, 1]), results_column] = (df[
                                                                                          results_column] - min) / denominator
    return df


def filter_by_normal_values(df, filter, remove_patients=False):
    if remove_patients:
        patients_to_delete = set()
        if not filter['resultsNormal']['normal']:
            patients_to_delete.update(df.loc[((df['result'] >= 0) & (df['result'] <= 1))]['patient_id'].tolist())
        if not filter['resultsNormal']['aboveNormal']:
            patients_to_delete.update(df.loc[(df['result'] > 1)]['patient_id'].tolist())
        if not filter['resultsNormal']['belowNormal']:
            patients_to_delete.update(df.loc[(df['result'] < 0)]['patient_id'].tolist())
        if len(patients_to_delete) > 0:
            df = df.drop(df[df['patient_id'].isin(patients_to_delete)].index)
    else:
        if not filter['resultsNormal']['normal']:
            df = df.drop(df[((df['result'] >= 0) & (df['result'] <= 1))].index)
        if not filter['resultsNormal']['aboveNormal']:
            df = df.drop(df[(df['result'] > 1)]['patient_id'].index)
        if not filter['resultsNormal']['belowNormal']:
            df = df.drop(df[(df['result'] < 0)].index)
    return df


def append_results_without_diagnoses(df, test_ids, filter):
    samples_results_excluded = get_samples_results(test_ids=test_ids, filters=filter,
                                                   have_all_tests=True,
                                                   exclude_diagnoses=True)
    df_excluded = pd.DataFrame(samples_results_excluded)
    df_excluded['has_diagnose'] = False
    return pd.concat([df, df_excluded], ignore_index=True)


def raw_sql_to_dict(raw_result):
    return [dict(row) for row in raw_result]


def get_filters_description(filters):
    description = ''
    if 'departments' in filters:
        description += 'Подразделения: ' + ', '.join(map(lambda x: x['label'], filters['departments'])) + '\r\n'
    else:
        description += 'Подразделения: любые\r\n'
    if 'diagnoses' in filters:
        description += 'Диагнозы: ' + ', '.join(map(lambda x: x['label'], filters['diagnoses'])) + '\r\n'
    else:
        description += 'Диагнозы: любые\r\n'
    if 'genders' in filters and not (filters['genders']['m'] and filters['genders']['f']):
        description += 'Пол пациентов: '
        if filters['genders']['m']:
            description += 'мужской'
        if filters['genders']['f']:
            description += 'женский'
        description += '\r\n'
    else:
        description += 'Пол: любой\r\n'
    if 'resultsNormal' in filters and not all(map(lambda x: filters['resultsNormal'][x], filters['resultsNormal'])):
        description += 'Значения показателей: '
        values = []
        if filters['resultsNormal']['normal']:
            values.append('норма')
        if filters['resultsNormal']['aboveNormal']:
            values.append('выше нормы')
        if filters['resultsNormal']['belowNormal']:
            values.append('ниже нормы')
        description += ', '.join(values) + '\r\n'
    else:
        'Значения показателей: все\r\n'
    if 'ageRange' in filters and filters['ageRange'][0] != 0 and filters['ageRange'][1] != 100:
        description += f'Возраст: от {filters["ageRange"][0]} до {filters["ageRange"][1]} лет\r\n'
    else:
        description += 'Возраст: любой\r\n'
    if 'dateRange' in filters:
        description += f'Временной диапазон: c {filters["dateRange"]["startDate"]} по {filters["dateRange"]["endDate"]}\r\n'
    else:
        description += 'Временной диапазон: любой\r\n'
    return description

