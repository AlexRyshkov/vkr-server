from db import db
from models import PatientDiagnose


class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(255), nullable=False, unique=True)
    gender = db.Column(db.String(255), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    diagnoses = db.relationship('Diagnose', secondary=PatientDiagnose, back_populates="patients")
    samples = db.relationship('Sample', back_populates="patient")
