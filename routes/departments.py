from flask_restful import Resource
from models import Department
from schemas import DepartmentSchema

departments_schema = DepartmentSchema(many=True)


class Departments(Resource):
    def get(self):
        departments = Department.query.all()
        result = departments_schema.dump(departments)
        return {"departments": result}
