from marshmallow import fields

from ma import ma
from models import SampleResult


class SampleResultSchema(ma.SQLAlchemySchema):
    class Meta:
        model = SampleResult

    result = ma.auto_field()
    test = fields.Nested('TestSchema')
