from flask_restful import Resource
from sqlalchemy import func

from models import Diagnose, PatientDiagnose
from schemas import DiagnoseSchema

diagnoses_schema = DiagnoseSchema(many=True, exclude=['mkb'])


class Diagnoses(Resource):
    def get(self):
        label_count = func.count(Diagnose.id).label('diagnoses_count')
        diagnoses = Diagnose.query.with_entities(Diagnose.id, Diagnose.code, Diagnose.name, label_count).join(
            PatientDiagnose).group_by(Diagnose.id).order_by(label_count.desc()).all()
        diagnoses = list(map(lambda diagnose: dict(diagnose), diagnoses))
        for diagnose in diagnoses:
            diagnose['name'] = diagnose['code'] if diagnose['name'] is None else diagnose['name']
        return {"diagnoses": diagnoses}
