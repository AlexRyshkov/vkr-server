from marshmallow import fields

from ma import ma
from models import Patient


class PatientSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Patient

    id = ma.auto_field()
    patient_id = ma.auto_field()
    gender = ma.auto_field()
    birth_date = ma.auto_field()
    diagnoses = fields.Nested('DiagnoseSchema', many=True)
    samples = fields.Nested('SampleSchema', many=True)
