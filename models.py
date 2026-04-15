from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=True) # Added for MNC verification
    email = db.Column(db.String(120), unique=True, nullable=True)
    mobile_number = db.Column(db.String(15), nullable=True) # Added for contact
    registration_year = db.Column(db.Integer, nullable=True) # Added for MNC verification
    state_medical_council = db.Column(db.String(100), nullable=True) # Added for verification
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin' or 'doctor'
    license_id = db.Column(db.String(50), unique=True, nullable=True)
    is_license_valid = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)

class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    images = db.relationship('MedicalImage', backref='folder', lazy=True)

class MedicalImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    encrypted_image_path = db.Column(db.String(255), nullable=False)
    key_path = db.Column(db.String(255), nullable=False)
    qkd_protocol_used = db.Column(db.String(50), nullable=False)
    lattice_hash = db.Column(db.String(16), nullable=True) # New: Lattice secret hash prefix
    fusion_id = db.Column(db.String(16), nullable=True)    # New: Final fused key hash prefix
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class VerificationSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.String(50), unique=True, nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)
    registration_year = db.Column(db.String(20), nullable=True)
    mobile_number = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    state = db.Column(db.String(100), nullable=True)
