from db import db


class Diagnose(db.Model):
    __tablename__ = 'diagnoses'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255),  nullable=False)
    name = db.Column(db.String(255), unique=False, nullable=True)
    mkb_id = db.Column(db.ForeignKey('mkb.id'), nullable=True, index=True)
    mkb = db.relationship('Mkb')
    patients = db.relationship('Patient', secondary='patients_diagnoses', back_populates="diagnoses")
