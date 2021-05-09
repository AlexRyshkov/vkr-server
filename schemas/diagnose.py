from marshmallow import fields

from ma import ma
from models import Diagnose


class DiagnoseSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Diagnose

    id = ma.auto_field()
    code = ma.auto_field()
    mkb = fields.Nested('MkbSchema')
