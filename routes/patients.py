from flask_restful import Resource
from models import Patient as PatientModel
from schemas import PatientSchema

patient_schema = PatientSchema()
patients_schema = PatientSchema(many=True, exclude=('diagnoses', 'samples'))


class Patients(Resource):
    def get(self):
        patients = PatientModel.query.with_entities(PatientModel.id, PatientModel.patient_id, PatientModel.birth_date,
                                                    PatientModel.gender).all()
        result = patients_schema.dump(patients)
        return {"patients": result}


class Patient(Resource):
    def get(self, id):
        patient = PatientModel.query.get(id)
        result = patient_schema.dump(patient)
        return {"patient": result}
