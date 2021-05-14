from flask_restful import Resource
from flask import request
from werkzeug.utils import secure_filename
from modules.data_loader.data_loader import load_data_from_file


class Upload(Resource):
    def post(self):
        f = request.files['file']
        f.save(secure_filename(f.filename))
        load_data_from_file(f.filename)
        return 'file uploaded successfully'
