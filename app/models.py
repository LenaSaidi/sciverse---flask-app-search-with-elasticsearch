# app/models.py

# from flask_sqlalchemy import SQLAlchemy
from app import db

# db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    firstName = db.Column(db.String(100))
    lastName = db.Column(db.String(100))
    nature = db.Column(db.Text)
    role = db.Column(db.String(50), default='user')  # Default role is 'user'
