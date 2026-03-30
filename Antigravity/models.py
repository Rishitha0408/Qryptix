from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin' or 'doctor'
    license_id = db.Column(db.String(50), unique=True, nullable=True)
    is_approved = db.Column(db.Boolean, default=False)

class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    hashed_password = db.Column(db.String(255), nullable=False) # to lock access
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    images = db.relationship('MedicalImage', backref='folder', lazy=True)

class MedicalImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    encrypted_image_path = db.Column(db.String(255), nullable=False)
    key_path = db.Column(db.String(255), nullable=False)
    qkd_protocol_used = db.Column(db.String(50), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
