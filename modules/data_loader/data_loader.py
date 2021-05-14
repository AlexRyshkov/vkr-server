import json
import re
from datetime import datetime

import numpy
import pandas as pd
import db
from models import Patient, Diagnose, Mkb, Department, Test, PatientDiagnose, SampleResult, Sample

mkb = None
used_columns = [
    'PatientId',
    'Birthday',
    'Sex',
    'DateTimeSampling',
    'BiomaterialId',
    'HospitalDepartmentId',
    'HospitalDepartmentName',
    'DiagnosisCode',
    'TestId',
    'Mnemonic',
    'TestName',
    'QuantResult',
    'UnitName']

drop_na_columns = [
    'DateTimeSampling',
    'BiomaterialId',
    'PatientId',
    'Birthday',
    'Sex',
    'HospitalDepartmentId',
    'HospitalDepartmentName',
    'DiagnosisCode',
    'TestId',
    'UnitName'
]

# общий анализ крови
complete_blood_id = 135
# биохимический анализ крови
blood_chemistry_id = 1


def columns_to_numeric_locale(df, columns):
    for column in columns:
        df[column] = df[column].str.replace(',', '.')
        df[column] = pd.to_numeric(df[column], errors='coerce')
    return df


def get_patients(df):
    df = df.drop_duplicates('PatientId')
    patients = list(df.apply(
        lambda x: Patient(patient_id=x['PatientId'], birth_date=x['Birthday'], gender='m' if x['Sex'] == 1 else 'f'),
        axis=1))
    return patients


def get_diagnoses(df):
    df = df.drop_duplicates('DiagnosisCode')
    diagnoses = list(df.apply(
        lambda x: Diagnose(code=x['DiagnosisCode'], mkb_id=get_mkb_by_code(x['DiagnosisCode']).id),
        axis=1))
    return diagnoses


def get_mkb_by_code(code):
    global mkb
    letter = code[0]
    number = float(re.search(r'[A-Z]([0-9]+)', code).group(1))
    for mkb_item in mkb:
        codes = mkb_item.codes
        regex = re.search(r'(?P<leftLetter>[A-Z])(?P<leftNum>[0-9]{2})-(?P<rightLetter>[A-Z])(?P<rightNum>[0-9]{2})',
                          codes)
        left_letter = regex.group('leftLetter')
        left_number = float(regex.group('leftNum'))
        right_letter = regex.group('rightLetter')
        right_number = float(regex.group('rightNum'))

        if (letter == left_letter == right_letter) & (left_number <= number <= right_number):
            return mkb_item
        if (letter == left_letter) & (left_number <= number):
            return mkb_item
        if (letter == right_letter) & (right_number >= number):
            return mkb_item
    raise ValueError(f'Не удалось найти класс МКБ для кода `{code}`')


def get_mkb():
    return db.session.query(Mkb).all()


def convert_dates(df):
    df['DateTimeSampling'] = df['DateTimeSampling'].apply(
        lambda x: datetime.strptime(x, '%d.%m.%Y').strftime('%Y-%m-%d'))
    df['Birthday'] = df['Birthday'].apply(lambda x: datetime.strptime(x, '%d.%m.%Y').strftime('%Y-%m-%d'))
    return df


def get_departments(df):
    df = df.drop_duplicates('HospitalDepartmentId')
    departments = list(df.apply(
        lambda x: Department(code=x['HospitalDepartmentId'], name=x['HospitalDepartmentName'], region='Ишим'),
        axis=1))
    return departments


def get_tests(df):
    df = df.drop_duplicates('TestName')
    tests = list(df.apply(lambda x: Test(name=x['TestName'], unit=x['UnitName']), axis=1))
    return tests


def get_samples(df):
    df_groupby = df.groupby('PatientId')
    samples = {}
    for patient_id in df_groupby.groups:
        samples[patient_id] = {}
        patient_tests = df_groupby.get_group(patient_id)
        patient_tests_by_date = patient_tests.groupby('DateTimeSampling')
        for sampling_date in patient_tests_by_date.groups:
            current_date_tests = patient_tests_by_date.get_group(sampling_date)
            current_date_tests = current_date_tests[
                current_date_tests['BiomaterialId'].isin([complete_blood_id, blood_chemistry_id])]
            sample_types_df = current_date_tests.drop_duplicates('BiomaterialId').set_index(
                'BiomaterialId')
            sample_tests = {}
            for index, row in sample_types_df.iterrows():
                sample_tests[index] = {
                    'department_id': row['HospitalDepartmentId'],
                    'date': sampling_date,
                    'type': 'cbc' if index == complete_blood_id else 'cmp',
                    'values': []
                }
            for index, row in current_date_tests.iterrows():
                biomaterial_id = row['BiomaterialId']
                sample_tests[biomaterial_id]['values'].append({'test_id': row['TestName'], 'result': row['Result']})
            samples[patient_id][sampling_date] = sample_tests
    return samples


def insert_db(values, df=None, class_field=None, id_column=None):
    db.session.bulk_save_objects(values, return_defaults=True)
    db.session.flush()
    if df is not None and id_column is not None and class_field is not None:
        ids = {}
        for value in values:
            ids[getattr(value, class_field)] = value.id
        df[id_column] = df[id_column].apply(lambda x: ids[x])
    return values


def insert_patients_diagonoses(df):
    df_groupby = df.groupby('PatientId')
    for patient_id in df_groupby.groups:
        codes = df_groupby.get_group(patient_id)['DiagnosisCode'].unique()
        for code in codes:
            db.session.execute(PatientDiagnose.insert().values(patient_id=patient_id, diagnose_id=code))
    db.session.flush()


def insert_samples(samples):
    for patient_id, date_samples in samples.items():
        for date, sample_results in date_samples.items():
            for biomaterial_id, result in sample_results.items():
                sample = Sample(type='cbc' if biomaterial_id == complete_blood_id else 'cmp', date=date,
                                patient_id=patient_id, department_id=result['department_id'])
                for value in result['values']:
                    sample.results.append(SampleResult(test_id=value['test_id'], result=value['result']))
                db.session.add(sample)
    db.session.flush()


def insert_mkb(filename):
    mkb_list = json.load(open(filename, encoding='utf-8'))
    mkb_list = list(map(lambda x: Mkb(name=x['name'], codes=x['codes']), mkb_list))
    return insert_db(mkb_list)


def load_data_from_file(filename):
    print('Загрузка мкб...')
    global mkb
    mkb = insert_mkb('mkb_list.json')
    print('Чтение датасета...')
    df = pd.read_csv(filename, sep=';', usecols=used_columns)
    print('Удаление колонок...')
    df.dropna(subset=drop_na_columns, inplace=True)
    print('Форматирование значений...')
    df = columns_to_numeric_locale(df, ['QuantResult'])
    df.drop(df[((df['QuantResult'] == 0) | (df['QuantResult'] == '') | (
        numpy.isnan(df['QuantResult'])))].index, inplace=True)
    df.rename(columns={'QuantResult': 'Result'}, inplace=True)
    df = convert_dates(df)
    print('Загрузка пациентов...')
    patients = get_patients(df)
    insert_db(patients, df=df, class_field='patient_id', id_column='PatientId')
    print('Загрузка диагнозов...')
    diagnoses = get_diagnoses(df)
    insert_db(diagnoses, df=df, class_field='code', id_column='DiagnosisCode')
    insert_patients_diagonoses(df)
    print('Загрузка подразделений...')
    departments = get_departments(df)
    insert_db(departments, df=df, class_field='code', id_column='HospitalDepartmentId')
    print('Загрузка тестов...')
    tests = get_tests(df)
    insert_db(tests, df=df, class_field='name', id_column='TestName')
    print('Загрузка анализов...')
    samples = get_samples(df)
    insert_samples(samples)
    db.session.commit()
