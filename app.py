import os
from dotenv import load_dotenv
from flask_restful import Api
import pandas as pd
import numpy as np
from flask import Flask, send_file, safe_join
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


@api.representation('application/octet-stream')
def output_file(data, code, headers):
    filepath = safe_join(data["directory"], data["filename"])

    response = send_file(
        filename_or_fp=filepath,
        mimetype="application/octet-stream",
        as_attachment=True,
        attachment_filename=data["filename"]
    )
    return response


api.add_resource(r.Departments, '/api/departments')
api.add_resource(r.Diagnoses, '/api/diagnoses')
api.add_resource(r.Mkbs, '/api/mkb')
api.add_resource(r.Patients, '/api/patients')
api.add_resource(r.Patient, '/api/patients/<int:id>')
api.add_resource(r.Samples, '/api/samples')
api.add_resource(r.Tests, '/api/tests')
api.add_resource(r.Boxplot, '/api/boxplot')
api.add_resource(r.Splom, '/api/splom')
api.add_resource(r.Correlation, '/api/correlation')
api.add_resource(r.Histogram, '/api/histogram')
api.add_resource(r.Cluster, '/api/cluster')
api.add_resource(r.SamplesResultsTable, '/api/tables/samples-results')
api.add_resource(r.SamplesResultsTableDownload, '/api/tables/samplesresults/download')
api.add_resource(r.Upload, '/api/upload')
app.json_encoder = JSONEncoder
app.run()
