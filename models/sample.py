from db import db


class Sample(db.Model):
    __tablename__ = 'samples'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum('cbc', 'cmp', 'other'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    patient_id = db.Column(db.ForeignKey('patients.id'), nullable=False, index=True)
    department_id = db.Column(db.ForeignKey('departments.id'), nullable=False, index=True)
    department = db.relationship('Department')
    patient = db.relationship('Patient', back_populates='samples')
    results = db.relationship("SampleResult")
