from db import db

PatientDiagnose = db.Table('patients_diagnoses',
                           db.Column('patient_id', db.Integer, db.ForeignKey('patients.id'), primary_key=True),
                           db.Column('diagnose_id', db.Integer, db.ForeignKey('diagnoses.id'), primary_key=True)
                           )
