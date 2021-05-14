from flask_restful import Resource
from models import Test, SampleResult, TestNormalValue
from schemas import TestSchema
from sqlalchemy import extract, func

tests_schema = TestSchema(many=True)


class Tests(Resource):
    def get(self):
        tests = Test.query.with_entities(Test.id, Test.name, Test.unit, Test.type,
                                         func.count(Test.id).label('results_count')).join(
            SampleResult).group_by(Test.id).order_by(Test.type.desc()).all()
        tests = list(map(lambda test: dict(test), tests))
        return {"tests": tests}
