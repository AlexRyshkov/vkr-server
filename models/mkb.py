from db import db


class Mkb(db.Model):
    __tablename__ = 'mkb'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    codes = db.Column(db.String(255), unique=True, nullable=False)
