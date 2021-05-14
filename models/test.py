from db import db


class Test(db.Model):
    __tablename__ = 'tests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    unit = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Enum('oak', 'bak'), nullable=True)
    normal_values = db.relationship('TestNormalValue')
