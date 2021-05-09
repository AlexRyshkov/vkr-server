from ma import ma
from models import Mkb


class MkbSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Mkb

    id = ma.auto_field()
    name = ma.auto_field()
    codes = ma.auto_field()
