from ma import ma
from models import Department


class DepartmentSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Department

    id = ma.auto_field()
    code = ma.auto_field()
    name = ma.auto_field()
    region = ma.auto_field()
