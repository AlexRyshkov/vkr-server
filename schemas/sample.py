from marshmallow import fields

from ma import ma
from models import Sample


class SampleSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Sample

    id = ma.auto_field()
    type = ma.auto_field()
    date = ma.auto_field()
    patient_id = ma.auto_field()
    results = fields.Nested('SampleResultSchema', many=True)
