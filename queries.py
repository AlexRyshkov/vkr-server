from helpers import raw_sql_to_dict
from db import db
from models import SampleResult
from models import Sample
from models import Patient
from models import Diagnose
from sqlalchemy import and_, func


def get_samples_results(test_ids, filters):
    age_label = func.year(Sample.date) - func.year(Patient.birth_date).label('age')
    query = db.session.query(SampleResult.result, Patient.id, age_label, SampleResult.test_id)
    query = query.join(Patient.samples)
    query = query.join(Sample.results)

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
    if 'mkb' in filters:
        patients_query = get_patients(filters)
        query = query.filter(Patient.id.in_(patients_query))
    if 'departments' in filters:
        departments_ids = list(map(lambda x: x['id'], filters['departments']))
        query = query.filter(Sample.department_id.in_(departments_ids))

    result = query.filter(SampleResult.test_id.in_(test_ids)).all()
    return list(
        {'result': res, 'patient_id': patient_id, 'age': age, 'test_id': test_id} for res, patient_id, age, test_id in
        result)


def get_patients(filters):
    query = db.session.query(Patient.id)
    if 'mkb' in filters:
        mkb_ids = list(map(lambda x: x['id'], filters['mkb']))
        query = query.join(Patient.diagnoses)
        query = query.filter(Diagnose.mkb_id.in_(mkb_ids))
    return query


def get_samples_results1(**kwargs):
    test_ids = kwargs.get('test_ids')
    min_age = kwargs.get('min_age')
    max_age = kwargs.get('max_age')
    results = db.session.execute(
        """select
        p.id as patient_id, sr.result,
        YEAR(s.date) - YEAR(p.birth_date) AS age,
        sr.test_id
        from samples_results sr
        join samples s on  sr.sample_id = s.id
        join patients p on s.patient_id = p.id
        where sr.test_id in :test_ids
        having age between :min_age and :max_age;""",
        {'test_ids': test_ids, 'min_age': min_age,
         'max_age': max_age})
    return raw_sql_to_dict(results)


def get_test_name(test_id):
    result = db.session.execute("""
    select name from tests
    where id = :test_id;""", {'test_id': test_id})
    return raw_sql_to_dict(result)[0]['name']
