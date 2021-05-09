from flask_restful import Resource
from models import Diagnose
from schemas import DiagnoseSchema

diagnoses_schema = DiagnoseSchema(many=True)


class Diagnoses(Resource):
    def get(self):
        diagnoses = Diagnose.query.all()
        result = diagnoses_schema.dump(diagnoses)
        return {"diagnoses": result}
