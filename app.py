import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask.json import JSONEncoder
from db import db
from ma import ma
import routes as r
import models


class JSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, pd.Series):
            return o.tolist()
        return super().default(o)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config["DEBUG"] = True
CORS(app)
db.app = app
db.init_app(app)
ma.init_app(app)
api = Api(app)
api.add_resource(r.Departments, '/api/departments')
api.add_resource(r.Diagnoses, '/api/diagnoses')
api.add_resource(r.Mkbs, '/api/mkb')
api.add_resource(r.Patients, '/api/patients')
api.add_resource(r.Patient, '/api/patients/<int:id>')
api.add_resource(r.Samples, '/api/samples')
api.add_resource(r.Tests, '/api/tests')
api.add_resource(r.Chart, '/api/chart')
api.add_resource(r.Cluster, '/api/cluster')
app.json_encoder = JSONEncoder
app.run()
