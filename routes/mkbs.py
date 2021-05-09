from flask_restful import Resource
from models import Mkb
from schemas import MkbSchema

mkb_schema = MkbSchema(many=True)


class Mkbs(Resource):
    def get(self):
        mkb = Mkb.query.all()
        result = mkb_schema.dump(mkb)
        return {"mkb": result}
