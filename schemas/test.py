from ma import ma
from models import Test


class TestSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Test

    id = ma.auto_field()
    name = ma.auto_field()
    unit = ma.auto_field()
