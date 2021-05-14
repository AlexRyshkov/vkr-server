from db import db
from models import SampleResult, Test, TestNormalValue
from models import Sample
from models import Patient
from models import Diagnose
from sqlalchemy import and_, func, distinct, not_


def get_samples_results(test_ids, **kwargs):
    filters = kwargs.get('filters', None)
    have_all_tests = kwargs.get('have_all_tests', False)
    exclude_diagnoses = kwargs.get('exclude_diagnoses', False)
    age_label = func.year(Sample.date) - func.year(Patient.birth_date).label('age')
    query = db.session.query(Patient.id, Patient.gender, age_label, SampleResult.test_id, SampleResult.result)
    query = query.join(Patient.samples)
    query = query.join(Sample.results)

    if filters is not None:
        if 'ageRange' in filters:
            startAge = filters['ageRange'][0]
            endAge = filters['ageRange'][1]
            query = query.filter((age_label >= startAge) & (age_label <= endAge))
        if 'dateRange' in filters:
            startDate = filters['dateRange']['startDate']
            endDate = filters['dateRange']['endDate']
            query = query.filter(and_(func.date(Sample.date) >= startDate, func.date(Sample.date) <= endDate))
        if 'genders' in filters:
            genders = []
            if filters['genders']['m']:
                genders.append('m')
            if filters['genders']['f']:
                genders.append('f')
            query = query.filter(Patient.gender.in_(genders))
        if 'diagnoses' in filters:
            patients_query = get_patients(filters, exclude_diagnoses=exclude_diagnoses)
            query = query.filter(Patient.id.in_(patients_query))
        if 'departments' in filters:
            departments_ids = list(map(lambda x: x['value'], filters['departments']))
            query = query.filter(Sample.department_id.in_(departments_ids))

    query = query.filter(SampleResult.test_id.in_(test_ids))
    if have_all_tests:
        test_id_count = func.count(distinct(SampleResult.test_id).label('cnt'))
        patients_with_all_tests = query.with_entities(Patient.id, test_id_count).group_by(
            Patient.id).having(test_id_count == len(test_ids)).all()
        patients_ids = list(map(lambda x: x[0], patients_with_all_tests))
        query = query.filter(Patient.id.in_(patients_ids))

    result = query.all()
    return list(
        {'result': res, 'patient_id': patient_id, 'gender': gender, 'age': age, 'test_id': test_id} for
        patient_id, gender, age, test_id, res in
        result)


def get_patients(filters, exclude_diagnoses):
    query = db.session.query(distinct(Patient.id))
    if 'diagnoses' in filters:
        diagnoses_ids = list(map(lambda x: x['value'], filters['diagnoses']))
        query = query.join(Patient.diagnoses)
        if exclude_diagnoses:
            query = query.filter(not_(Patient.diagnoses.any(Diagnose.id.in_(diagnoses_ids))))
        else:
            query = query.filter(Diagnose.id.in_(diagnoses_ids))
    query = query.order_by(Patient.id)
    return query


def get_test_name(test_id):
    return Test.query.get(test_id).name


def get_test_unit_name(test_id):
    return Test.query.get(test_id).unit


def get_normal_values(test_id):
    return TestNormalValue.query.filter(TestNormalValue.test_id == test_id).all()


def get_patients_with_diagnose(diagnose_id):
    return Diagnose.query.get(diagnose_id).patients
