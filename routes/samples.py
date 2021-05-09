from flask_restful import Resource
from models import Sample
from schemas import SampleSchema

samples_schema = SampleSchema(many=True)


class Samples(Resource):
    def get(self):
        samples = Sample.query.all()
        result = samples_schema.dump(samples)
        return {"samples": result}
