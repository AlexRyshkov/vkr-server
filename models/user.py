from db import db


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), nullable=False, unique=True)
    hashpassword = db.Column(db.String(255), nullable=False)
    jwt = db.Column(db.String(255))
