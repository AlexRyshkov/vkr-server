from db import db


class Diagnose(db.Model):
    __tablename__ = 'diagnoses'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255), unique=True, nullable=False)
    mkb_id = db.Column(db.ForeignKey('mkb.id'), nullable=False, index=True)
    mkb = db.relationship('Mkb')
