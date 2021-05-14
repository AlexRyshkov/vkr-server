from db import db


class TestNormalValue(db.Model):
    __tablename__ = 'tests_normal_values'
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.ForeignKey('tests.id'), nullable=False, index=True)
    patient_category = db.Column(db.Enum('all', 'child', 'male', 'female'), nullable=False)
    min = db.Column('min', db.Float, nullable=False)
    max = db.Column('max', db.Float, nullable=False)
