from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    last_activity_date = db.Column(db.DateTime, default=datetime.utcnow)
    inactivity_threshold_days = db.Column(db.Integer, default=60)
    status = db.Column(db.String(20), default='Active')  # Active, Inactive, Verification_Pending
    
    assets = db.relationship('Asset', backref='owner', lazy=True)
    nominees = db.relationship('Nominee', backref='user', lazy=True)

class Asset(db.Model):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=True)
    asset_type = db.Column(db.String(50), nullable=False)  # document, note, password, media
    encrypted_content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Nominee(db.Model):
    __tablename__ = 'nominees'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    permission_level = db.Column(db.String(20), default='Full')  # Full, Partial
    status = db.Column(db.String(20), default='Accepted') # Pending, Accepted
    
    access_requests = db.relationship('AccessRequest', backref='nominee', lazy=True)

class AccessRequest(db.Model):
    __tablename__ = 'access_requests'
    id = db.Column(db.Integer, primary_key=True)
    nominee_id = db.Column(db.Integer, db.ForeignKey('nominees.id'), nullable=False)
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending') # Pending, Approved, Denied

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
