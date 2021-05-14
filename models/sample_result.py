from db import db


class SampleResult(db.Model):
    __tablename__ = 'samples_results'
    id = db.Column(db.Integer, primary_key=True)
    sample_id = db.Column(db.Integer, db.ForeignKey('samples.id'))
    sample = db.relationship('Sample', back_populates='results')
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'))
    test = db.relationship('Test')
    result = db.Column('result', db.Float, nullable=False)
